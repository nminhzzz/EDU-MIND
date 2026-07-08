"""
Shared file upload endpoint — Cloudinary or local fallback.
"""

import os

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_current_user
from app.infrastructure.uploader import upload_file_helper
from app.models.user import User

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
) -> dict:
    """
    Upload a file to Cloudinary (or local fallback).
    Returns the public URL and basic file metadata.
    """
    file_url = upload_file_helper(file, folder=folder)
    filename = file.filename or "file"
    file_type = os.path.splitext(filename)[1].replace(".", "").lower() or "binary"

    return {
        "url": file_url,
        "filename": filename,
        "file_type": file_type,
        "folder": folder,
    }
