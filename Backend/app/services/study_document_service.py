"""
Study document use cases — upload, list, delete with RAG embedding sync.
"""

import os
import re
from typing import Any, List, Optional

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


async def upload_study_document(
    db: Session,
    db_mongo: Any,
    *,
    teacher_id: int,
    subject_id: int,
    title: str,
    file: UploadFile,
) -> StudyDocument:
    """Upload a teaching document and optionally index it for RAG."""
    subject = get_subject(db, subject_id)

    file_url = upload_file_helper(file)
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
    commit_or_rollback(db)
    db.refresh(db_doc)

    try:
        file.file.seek(0)
        file_bytes = await file.read()
        content = _extract_content(file_bytes, file_type, subject.name, title)

        if db_mongo is not None:
            await save_study_material(
                db_mongo=db_mongo,
                subject_id=subject_id,
                topic=title,
                content=content,
                metadata={"document_id": db_doc.id, "file_name": file.filename},
            )
    except Exception as exc:
        logger.warning("Failed to generate/save embedding in MongoDB: %s", exc)

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


def _cloudinary_public_id(file_url: str) -> Optional[str]:
    """Extract Cloudinary public_id from a delivery URL."""
    match = re.search(r"/upload/(?:s--[^/]+--/)?(?:v\d+/)?(.+)$", file_url)
    return match.group(1) if match else None


def _cloudinary_version(file_url: str) -> Optional[int]:
    match = re.search(r"/upload/(?:s--[^/]+--/)?v(\d+)/", file_url)
    return int(match.group(1)) if match else None


def _configure_cloudinary() -> None:
    import cloudinary

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


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


def _local_disk_path(doc: StudyDocument) -> str:
    rel = doc.file_path.removeprefix("/static/")
    return os.path.join(_uploads_root(), rel)


def get_document_view_url(doc: StudyDocument) -> str:
    """
    Return a browser-openable URL for a stored document.

    Cloudinary: return the stored delivery URL as-is (requires
    "Allow delivery of PDF and ZIP files" in Cloudinary Security settings).
    Local files are served via /static (mounted in main.py).
    """
    file_path = doc.file_path

    if file_path.startswith("http"):
        return file_path

    if file_path.startswith("/static/"):
        base = settings.API_V1_STR.replace("/api/v1", "")
        return f"{base}{file_path}"

    return file_path


def _fetch_cloudinary_bytes(doc: StudyDocument) -> bytes:
    """Download raw file bytes from Cloudinary using authenticated URLs."""
    import urllib.error
    import urllib.request

    import cloudinary.utils

    _configure_cloudinary()
    file_path = doc.file_path
    public_id = _cloudinary_public_id(file_path) or ""
    base_id = public_id.rsplit(".", 1)[0] if "." in public_id else public_id
    fmt = doc.file_type or "pdf"

    candidates = []
    if base_id:
        candidates.append(
            cloudinary.utils.private_download_url(
                base_id, format=fmt, resource_type="raw"
            )
        )
    candidates.append(get_document_view_url(doc))
    if file_path.startswith("http"):
        candidates.append(file_path)

    last_error: Exception | None = None
    for url in dict.fromkeys(candidates):
        try:
            with urllib.request.urlopen(url, timeout=45) as resp:
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

    if doc.file_path.startswith("/static/"):
        path = _local_disk_path(doc)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Không tìm thấy file local: {path}")
        with open(path, "rb") as handle:
            return handle.read(), media_type, filename

    if doc.file_path.startswith("http"):
        return _fetch_cloudinary_bytes(doc), media_type, filename

    raise FileNotFoundError("Đường dẫn tài liệu không hợp lệ.")


def get_study_document_for_user(
    db: Session, document_id: int, user_id: int, *, is_teacher: bool
) -> StudyDocument:
    """Return a document if the user is allowed to view it."""
    doc = study_document_repository.get(db, document_id)
    if not doc:
        raise ValueError(f"Không tìm thấy tài liệu với ID={document_id}.")
    if is_teacher and doc.created_by != user_id:
        raise PermissionError("Bạn không có quyền xem tài liệu của giáo viên khác.")
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
