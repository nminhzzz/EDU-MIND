import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from app.api.deps import get_current_user
from app.models.user import User
from app.core.uploader import upload_file_helper

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Tải tệp tin lên hệ thống (Dùng chung cho Tài liệu, Avatar, v.v...)",
)
async def upload_file(
    file: UploadFile = File(..., description="Tệp tin cần tải lên"),
    folder: str = Form(
        "general", description="Thư mục phân loại (ví dụ: study_documents, avatars)"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Tải file hoặc ảnh lên dịch vụ Cloudinary.
    Trả về đường dẫn URL và thông tin định dạng của tệp tin.
    """
    try:
        file_url = upload_file_helper(file, folder=folder)
        filename = file.filename or "file"
        file_type = os.path.splitext(filename)[1].replace(".", "").lower() or "binary"

        return {
            "url": file_url,
            "filename": filename,
            "file_type": file_type,
            "folder": folder,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tải tệp lên: {str(e)}",
        )
