"""
Study Documents API — upload and manage teaching materials with RAG embedding.
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher, get_current_user, get_db
from app.database.mongodb import get_mongodb_db
from app.models.user import User
from app.schemas.study_document import StudyDocumentResponse
from app.services.study_document_service import (
    delete_study_document,
    get_document_view_url,
    get_study_document_for_user,
    list_study_documents,
    read_study_document_file,
    upload_study_document,
)

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
    db_mongo: Any = Depends(get_mongodb_db),
    current_teacher: User = Depends(get_current_teacher),
) -> StudyDocumentResponse:
    try:
        return await upload_study_document(
            db,
            db_mongo,
            teacher_id=current_teacher.id,
            subject_id=subject_id,
            title=title,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/",
    response_model=List[StudyDocumentResponse],
    summary="Xem danh sách tài liệu giảng dạy",
)
def list_documents(
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[StudyDocumentResponse]:
    return list_study_documents(db, subject_id=subject_id)


@router.get(
    "/{document_id}/file",
    summary="Tải/xem file tài liệu qua backend (proxy Cloudinary PDF)",
)
def download_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        doc = get_study_document_for_user(
            db,
            document_id,
            current_user.id,
            is_teacher=(current_user.role == "teacher"),
        )
        content, media_type, filename = read_study_document_file(doc)
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Không thể tải file tài liệu: {exc}",
        ) from exc


@router.get(
    "/{document_id}/view-url",
    summary="Lấy URL xem/tải tài liệu (signed URL cho Cloudinary PDF)",
)
def get_document_view_url_api(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        doc = get_study_document_for_user(
            db,
            document_id,
            current_user.id,
            is_teacher=(current_user.role == "teacher"),
        )
        return {"url": get_document_view_url(doc)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Giáo viên xóa tài liệu khỏi kho",
)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    db_mongo: Any = Depends(get_mongodb_db),
    current_teacher: User = Depends(get_current_teacher),
) -> dict:
    try:
        return await delete_study_document(
            db,
            db_mongo,
            document_id=document_id,
            teacher_id=current_teacher.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
