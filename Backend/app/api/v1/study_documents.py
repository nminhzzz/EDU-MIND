import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_teacher, get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.study_document import StudyDocument
from app.schemas.study_document import StudyDocumentResponse
from app.core.uploader import upload_file_helper
from app.services.embedding_service import save_study_material
from app.database.mongodb import get_mongodb_db
from app.core.document_parser import extract_text_from_pdf, extract_text_from_docx

router = APIRouter()


@router.post(
    "/",
    response_model=StudyDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên tải tài liệu mới lên kho lưu trữ",
)
async def upload_document(
    subject_id: int = Form(..., description="ID môn học"),
    title: str = Form(..., description="Tiêu đề tài liệu"),
    file: UploadFile = File(..., description="File tài liệu (PDF, docx, txt, md...)"),
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    # 1. Kiểm tra môn học có tồn tại không
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={subject_id}.",
        )

    # 2. Upload file (lưu Cloudinary hoặc fallback local)
    file_url = upload_file_helper(file)
    file_type = os.path.splitext(file.filename)[1].replace(".", "").lower() or "binary"

    # 3. Tạo bản ghi MySQL
    db_doc = StudyDocument(
        subject_id=subject_id,
        created_by=current_teacher.id,
        title=title,
        file_path=file_url,
        file_type=file_type,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # 4. Trích xuất text content và đồng bộ hóa Vector Embedding vào MongoDB RAG
    try:
        file.file.seek(0)
        file_bytes = await file.read()

        # Trích xuất văn bản dựa trên định dạng tệp tin
        if file_type in ["txt", "md", "json", "csv", "html"]:
            content = file_bytes.decode("utf-8", errors="ignore")
        elif file_type == "pdf":
            content = (
                extract_text_from_pdf(file_bytes)
                or f"Tài liệu giảng dạy môn {subject.name}: {title}. Định dạng file: {file_type}."
            )
        elif file_type in ["docx", "doc"]:
            content = (
                extract_text_from_docx(file_bytes)
                or f"Tài liệu giảng dạy môn {subject.name}: {title}. Định dạng file: {file_type}."
            )
        else:
            content = f"Tài liệu giảng dạy môn {subject.name}: {title}. Định dạng file: {file_type}."

        db_mongo = get_mongodb_db()
        if db_mongo is not None:
            # Lưu tài liệu kèm document_id vào metadata để dễ dàng xóa/quản lý sau này
            await save_study_material(
                db_mongo=db_mongo,
                subject_id=subject_id,
                topic=title,
                content=content,
                metadata={"document_id": db_doc.id, "file_name": file.filename},
            )
    except Exception as e:
        print(f"[Warning] Failed to generate/save embedding in MongoDB: {e}")

    return db_doc


@router.get(
    "/",
    response_model=List[StudyDocumentResponse],
    summary="Xem danh sách tài liệu giảng dạy",
)
def list_documents(
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(StudyDocument)
    if subject_id is not None:
        query = query.filter(StudyDocument.subject_id == subject_id)
    return query.all()


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Giáo viên xóa tài liệu khỏi kho",
)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    # 1. Kiểm tra tài liệu tồn tại
    doc = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu với ID={document_id}.",
        )

    # Kiểm tra quyền chủ sở hữu
    if doc.created_by != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa tài liệu của giáo viên khác.",
        )

    # 2. Xóa khỏi MongoDB RAG (đồng bộ)
    try:
        db_mongo = get_mongodb_db()
        if db_mongo is not None:
            # Xóa các vector chunks có document_id tương ứng
            await db_mongo.study_material_embeddings.delete_many(
                {"metadata.document_id": document_id}
            )
    except Exception as e:
        print(f"[Warning] Failed to delete embeddings from MongoDB: {e}")

    # 3. Xóa bản ghi MySQL
    db.delete(doc)
    db.commit()

    return {"message": "Đã xóa tài liệu và các vector embeddings liên quan thành công."}
