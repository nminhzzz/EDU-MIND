import os
import shutil
from fastapi import UploadFile
from app.core.config import settings


def upload_file_helper(file: UploadFile, folder: str = "general") -> str:
    """
    Hàm trợ giúp upload tài liệu hoặc hình ảnh lên Cloudinary / Local storage.
    """
    # Phân loại tệp tin dựa trên đuôi file
    filename = file.filename or "file"
    ext = os.path.splitext(filename)[1].lower()
    is_image = ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"]
    resource_type = "image" if is_image else "raw"

    if (
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    ):
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            # Tạo public_id giữ nguyên tên và đuôi tệp tin
            public_id = f"{folder}/{filename}"

            res = cloudinary.uploader.upload(
                file.file, resource_type=resource_type, public_id=public_id
            )
            return res.get("secure_url") or res.get("url")
        except Exception as e:
            print(
                f"[Warning] Cloudinary upload failed, falling back to local storage: {e}"
            )

    # Fallback: Lưu local trên server
    upload_dir = f"uploads/{folder}"
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, filename)
    file.file.seek(0)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/static/{folder}/{filename}"
