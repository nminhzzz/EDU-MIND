"""
File upload adapter — Cloudinary (preferred) or local disk (fallback).
"""

import os
import re
import shutil

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Upload constraints ─────────────────────────────────────────────────────────
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf", ".doc", ".docx", ".txt", ".pptx", ".xlsx", ".csv",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}


def _sanitize_filename(raw: str) -> str:
    """Strip directory traversal and keep only the base filename."""
    return os.path.basename(raw).strip() or "upload"


def _slugify_public_id(name: str) -> str:
    """Cloudinary public_id safe segment — no spaces or special chars."""
    slug = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
    return slug or "upload"


def upload_file_helper(file: UploadFile, folder: str = "general") -> str:
    """
    Upload a document or image to Cloudinary (preferred) or local storage (fallback).

    Raises HTTPException 400 for disallowed file types.
    Raises HTTPException 413 if the file exceeds MAX_UPLOAD_BYTES.
    """
    raw_name = file.filename or "upload"
    filename = _sanitize_filename(raw_name)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Định dạng tệp '{ext}' không được phép. Chỉ chấp nhận: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )

    # Read once to check size, then reset for upload
    data = file.file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Tệp quá lớn. Kích thước tối đa cho phép là {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )
    file.file.seek(0)

    resource_type = "image" if ext in IMAGE_EXTENSIONS else "raw"

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
            # Strip extension for raw files — Cloudinary appends it in the delivery URL.
            base_name = _slugify_public_id(os.path.splitext(filename)[0])
            public_id = f"{folder}/{base_name}" if resource_type == "raw" else f"{folder}/{filename}"
            res = cloudinary.uploader.upload(
                file.file,
                resource_type=resource_type,
                public_id=public_id,
                type="upload",
                access_mode="public",
            )
            return res.get("secure_url") or res.get("url")
        except (HTTPException, Exception) as exc:
            if isinstance(exc, HTTPException):
                raise
            logger.warning("Cloudinary upload failed, falling back to local storage: %s", exc)

    # Fallback: save to local disk
    upload_dir = f"uploads/{folder}"
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, filename)
    file.file.seek(0)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/static/{folder}/{filename}"
