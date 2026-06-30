import os
import shutil
from fastapi import UploadFile
from app.core.config import settings


def upload_file_helper(file: UploadFile) -> str:
    """
    Hàm trợ giúp upload tài liệu.
    Nếu cấu hình Cloudinary đầy đủ -> Upload lên Cloudinary (resource_type='raw').
    Ngược lại -> Lưu cục bộ trên server tại thư mục uploads/documents/.
    """
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )
            # Upload raw file (PDF, docx, txt...)
            res = cloudinary.uploader.upload(
                file.file,
                resource_type="raw",
                public_id=f"study_documents/{file.filename}"
            )
            return res.get("secure_url") or res.get("url")
        except Exception as e:
            print(f"[Warning] Cloudinary upload failed, falling back to local storage: {e}")

    # Fallback: Lưu local trên server
    upload_dir = "uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, file.filename)
    # Reset con trỏ file trước khi đọc lại
    file.file.seek(0)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/static/documents/{file.filename}"
