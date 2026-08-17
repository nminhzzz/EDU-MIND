"""
Study document use cases — upload, list, delete with RAG embedding sync.
"""

import os
import re
import time
from typing import Any, List, Optional
from urllib.parse import unquote

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.infrastructure.document_parser import extract_text_from_docx, extract_text_from_pdf
from app.infrastructure.uploader import upload_file_helper
from app.models.study_document import StudyDocument
from app.repositories.study_document_repository import study_document_repository
from app.services.embedding_service import save_study_material
from app.services.subject_service import get_subject
from app.services.outbox_service import stage_outbox_job

logger = get_logger(__name__)

_TEXT_EXTENSIONS = {"txt", "md", "json", "csv", "html"}


def _extract_content(
    file_bytes: bytes, file_type: str, subject_name: str, title: str
) -> str:
    """Extract plain-text content from uploaded file bytes."""
    if file_type in _TEXT_EXTENSIONS:
        return file_bytes.decode("utf-8", errors="ignore")
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes) or (
            f"Tài liệu giảng dạy môn {subject_name}: {title}. Định dạng: {file_type}."
        )
    if file_type in {"docx", "doc"}:
        return extract_text_from_docx(file_bytes) or (
            f"Tài liệu giảng dạy môn {subject_name}: {title}. Định dạng: {file_type}."
        )
    return f"Tài liệu giảng dạy môn {subject_name}: {title}. Định dạng: {file_type}."


async def _index_document_embedding(
    db_mongo: Any,
    *,
    subject_id: int,
    title: str,
    content: str,
    document_id: int,
    file_name: str,
) -> None:
    """Background task — Gemini embedding can take 30–90s; must not block upload response."""
    try:
        await save_study_material(
            db_mongo=db_mongo,
            subject_id=subject_id,
            topic=title,
            content=content,
            metadata={"document_id": document_id, "file_name": file_name},
        )
    except Exception as exc:
        logger.warning(
            "Failed to generate/save embedding for document %s: %s",
            document_id,
            exc,
        )


async def upload_study_document(
    db: Session,
    db_mongo: Any,
    *,
    teacher_id: int,
    subject_id: int,
    title: str,
    file: UploadFile,
    index_in_background: bool = False,
    on_index_ready=None,
) -> StudyDocument:
    """Upload a teaching document; RAG indexing runs inline or in a background task."""
    subject = get_subject(db, subject_id)

    file.file.seek(0)
    file_bytes = await file.read()
    file.file.seek(0)

    file_url = upload_file_helper(
        file, folder="study_documents", restricted=True
    )
    file_type = (
        os.path.splitext(file.filename or "file")[1].replace(".", "").lower()
        or "binary"
    )

    db_doc = study_document_repository.stage_document(
        db,
        subject_id=subject_id,
        created_by=teacher_id,
        title=title,
        file_path=file_url,
        file_type=file_type,
    )
    if index_in_background:
        db.flush()
        stage_outbox_job(
            db,
            task_name="app.workers.tasks.task_index_study_document",
            args=[db_doc.id],
            unique_key=f"document-index:{db_doc.id}",
        )
    commit_or_rollback(db)
    db.refresh(db_doc)

    if db_mongo is not None:
        content = _extract_content(file_bytes, file_type, subject.name, title)
        index_kwargs = {
            "db_mongo": db_mongo,
            "subject_id": subject_id,
            "title": title,
            "content": content,
            "document_id": db_doc.id,
            "file_name": file.filename or "upload",
        }
        if index_in_background:
            pass
        elif on_index_ready is not None:
            on_index_ready(**index_kwargs)
        else:
            await _index_document_embedding(**index_kwargs)

    return db_doc


async def reindex_study_document_rag(
    db: Session,
    db_mongo: Any,
    *,
    document_id: int,
) -> int:
    """Tái index tài liệu đã upload vào MongoDB RAG (chia chunk nếu file dài)."""
    doc = study_document_repository.get(db, document_id)
    if not doc:
        raise ValueError(f"Không tìm thấy tài liệu với ID={document_id}.")

    subject = get_subject(db, doc.subject_id)
    content, _, _ = read_study_document_file(doc)
    file_type = doc.file_type
    text = _extract_content(content, file_type, subject.name, doc.title)

    await db_mongo.study_material_embeddings.delete_many(
        {"metadata.document_id": document_id}
    )
    await save_study_material(
        db_mongo=db_mongo,
        subject_id=doc.subject_id,
        topic=doc.title,
        content=text,
        metadata={"document_id": doc.id, "file_name": f"{doc.title}.{doc.file_type}"},
    )
    return doc.subject_id


def list_study_documents(
    db: Session, *, subject_id: Optional[int] = None
) -> List[StudyDocument]:
    """Return study documents with optional subject filter."""
    return study_document_repository.list_all(db, subject_id=subject_id)


def _cloudinary_asset_parts(
    file_url: str, file_type: str
) -> Optional[tuple[str, str, str]]:
    """Return resource type, delivery type and extension-free public ID."""
    clean_url = file_url.split("?", 1)[0]
    match = re.search(
        r"/(image|video|raw)/(upload|private|authenticated)/"
        r"(?:s--[^/]+--/)?(?:v\d+/)?(.+)$",
        clean_url,
    )
    if not match:
        return None
    resource_type, delivery_type, public_id = match.groups()
    public_id = unquote(public_id)
    suffix = f".{(file_type or '').lower().lstrip('.')}"
    if suffix != "." and public_id.lower().endswith(suffix):
        public_id = public_id[: -len(suffix)]
    return resource_type, delivery_type, public_id


def _configure_cloudinary() -> None:
    import cloudinary

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def get_document_view_url(doc: StudyDocument) -> str:
    """Return a short-lived Cloudinary URL or an authorized local endpoint."""
    file_path = doc.file_path

    if file_path.startswith("http"):
        parts = _cloudinary_asset_parts(file_path, doc.file_type)
        if not parts:
            raise ValueError("URL lưu trữ tài liệu không thuộc Cloudinary hợp lệ.")
        resource_type, delivery_type, public_id = parts
        _configure_cloudinary()
        import cloudinary.utils

        if resource_type == "image":
            # PDFs stored as image assets keep application/pdf and render in
            # the browser's native viewer instead of forcing a download.
            return cloudinary.utils.cloudinary_url(
                public_id,
                format=(doc.file_type or "pdf").lower().lstrip("."),
                resource_type=resource_type,
                type=delivery_type,
                sign_url=True,
                secure=True,
            )[0]

        # Raw/office assets are downloads by nature. They still bypass the app
        # server through a short-lived Cloudinary API URL.
        return cloudinary.utils.private_download_url(
            public_id,
            format=(doc.file_type or "pdf").lower().lstrip("."),
            resource_type=resource_type,
            type=delivery_type,
            expires_at=int(time.time()) + 600,
            attachment=False,
        )

    return f"{settings.API_V1_STR}/documents/{doc.id}/file"


def _media_type_for(file_type: str) -> str:
    mapping = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain; charset=utf-8",
        "md": "text/markdown; charset=utf-8",
    }
    return mapping.get(file_type.lower(), "application/octet-stream")


def _uploads_root() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def _fetch_cloudinary_bytes(doc: StudyDocument) -> bytes:
    """Download raw file bytes from Cloudinary using authenticated URLs."""
    import urllib.request

    import cloudinary.utils

    _configure_cloudinary()
    file_path = doc.file_path
    parts = _cloudinary_asset_parts(file_path, doc.file_type)
    public_id = parts[2] if parts else ""
    resource_type = parts[0] if parts else "raw"
    delivery_type = parts[1] if parts else "upload"
    base_id = public_id
    fmt = doc.file_type or "pdf"

    candidates = []
    if base_id:
        candidates.append(
            cloudinary.utils.private_download_url(
                base_id,
                format=fmt,
                resource_type=resource_type,
                type=delivery_type,
                expires_at=int(time.time()) + 600,
                attachment=False,
            )
        )
    last_error: Exception | None = None
    for url in dict.fromkeys(candidates):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read()
                if data:
                    return data
        except Exception as exc:
            last_error = exc
            logger.warning("Cloudinary fetch failed for %s via %s: %s", doc.id, url[:80], exc)

    raise RuntimeError(
        f"Không thể tải tài liệu từ Cloudinary (doc #{doc.id}). "
        f"Lỗi cuối: {last_error}"
    )


def read_study_document_file(doc: StudyDocument) -> tuple[bytes, str, str]:
    """Return (file_bytes, media_type, download_filename)."""
    media_type = _media_type_for(doc.file_type)
    filename = f"{doc.title}.{doc.file_type}"

    if doc.file_path.startswith("http"):
        return _fetch_cloudinary_bytes(doc), media_type, filename

    rel = doc.file_path.removeprefix("/static/").removeprefix("static/").removeprefix("uploads/")
    possible_paths = [
        os.path.join(_uploads_root(), rel),
        doc.file_path,
        os.path.join(os.getcwd(), doc.file_path),
    ]

    for p in possible_paths:
        if os.path.isfile(p):
            with open(p, "rb") as handle:
                return handle.read(), media_type, filename

    raise FileNotFoundError(f"Tài liệu '{doc.title}' không tìm thấy tập tin thực tế trên hệ thống (đường dẫn: {doc.file_path}).")


def get_study_document_for_user(
    db: Session,
    document_id: int,
    user_id: int,
    *,
    is_teacher: bool,
    is_admin: bool = False,
) -> StudyDocument:
    """Return a document if the user is allowed to view it."""
    doc = study_document_repository.get(db, document_id)
    if not doc:
        raise ValueError(f"Không tìm thấy tài liệu với ID={document_id}.")
    if is_admin:
        return doc
    if is_teacher and doc.created_by != user_id:
        raise PermissionError("Bạn không có quyền xem tài liệu của giáo viên khác.")
    if not is_teacher:
        from app.models.classroom import Classroom
        from app.models.classroom_student import ClassroomStudent

        allowed = (
            db.query(ClassroomStudent.id)
            .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
            .filter(
                ClassroomStudent.student_id == user_id,
                Classroom.teacher_id == doc.created_by,
                Classroom.subject_id == doc.subject_id,
            )
            .first()
        )
        if not allowed:
            raise PermissionError("Bạn không có quyền xem tài liệu này.")
    return doc


async def delete_study_document(
    db: Session,
    db_mongo: Any,
    *,
    document_id: int,
    teacher_id: int,
) -> dict:
    """Delete a document and its MongoDB embeddings."""
    doc = study_document_repository.get(db, document_id)
    if not doc:
        raise ValueError(f"Không tìm thấy tài liệu với ID={document_id}.")

    if doc.created_by != teacher_id:
        raise PermissionError("Bạn không có quyền xóa tài liệu của giáo viên khác.")

    try:
        if db_mongo is not None:
            await db_mongo.study_material_embeddings.delete_many(
                {"metadata.document_id": document_id}
            )
    except Exception as exc:
        logger.warning("Failed to delete embeddings from MongoDB: %s", exc)

    db.delete(doc)
    commit_or_rollback(db)

    return {"message": "Đã xóa tài liệu và các vector embeddings liên quan thành công."}
