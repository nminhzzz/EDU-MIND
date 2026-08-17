"""
File upload adapter — Cloudinary (preferred) or local disk (fallback).
"""

import os
import re
import shutil
import uuid
from pathlib import Path

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
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

# Callers may select a logical bucket, but never an arbitrary filesystem path.
ALLOWED_FOLDERS = {"general", "study_documents", "avatars", "classroom_quizzes"}


def validate_file_signature(data: bytes, ext: str) -> bool:
    """Reject obvious extension spoofing before parsing or publishing an upload."""
    ext = ext.lower()
    signatures = {
        ".pdf": (b"%PDF-",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".gif": (b"GIF87a", b"GIF89a"),
        ".bmp": (b"BM",),
        ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
        ".docx": (b"PK\x03\x04",),
        ".pptx": (b"PK\x03\x04",),
        ".xlsx": (b"PK\x03\x04",),
    }
    if ext == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    expected = signatures.get(ext)
    if expected:
        return any(data.startswith(signature) for signature in expected)
    if ext in {".txt", ".csv"}:
        return b"\x00" not in data[:8192]
    return True


def _sanitize_filename(raw: str) -> str:
    """Strip directory traversal and keep only the base filename."""
    return os.path.basename(raw).strip() or "upload"


def _slugify_public_id(name: str) -> str:
    """Cloudinary public_id safe segment — no spaces or special chars."""
    slug = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
    return slug or "upload"


def upload_file_helper(
    file: UploadFile, folder: str = "general", *, restricted: bool = False
) -> str:
    """
    Upload a document or image to Cloudinary (preferred) or local storage (fallback).

    Raises HTTPException 400 for disallowed file types.
    Raises HTTPException 413 if the file exceeds MAX_UPLOAD_BYTES.
    """
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thư mục tải lên không hợp lệ.",
        )

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
    if not validate_file_signature(data, ext):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung tệp không khớp với định dạng đã khai báo.",
        )
    file.file.seek(0)

    # Cloudinary treats PDFs as image assets. This preserves application/pdf
    # delivery and browser preview support; office/text documents remain raw.
    resource_type = "image" if ext in IMAGE_EXTENSIONS or ext == ".pdf" else "raw"
    storage_name = f"{uuid.uuid4().hex}{ext}"

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
            base_name = _slugify_public_id(os.path.splitext(storage_name)[0])
            public_id = f"{folder}/{base_name}" if resource_type == "raw" else f"{folder}/{storage_name}"
            upload_options = {
                "resource_type": resource_type,
                "public_id": public_id,
                "type": "authenticated" if restricted else "upload",
            }
            if not restricted:
                upload_options["access_mode"] = "public"
            res = cloudinary.uploader.upload(file.file, **upload_options)
            return res.get("secure_url") or res.get("url")
        except (HTTPException, Exception) as exc:
            if isinstance(exc, HTTPException):
                raise
            logger.warning("Cloudinary upload failed, falling back to local storage: %s", exc)

    # Fallback: save to local disk
    uploads_root = (Path.cwd() / "uploads").resolve()
    upload_dir = (uploads_root / folder).resolve()
    try:
        upload_dir.relative_to(uploads_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Đường dẫn tải lên không hợp lệ.") from exc
    upload_dir.mkdir(parents=True, exist_ok=True)
    local_path = upload_dir / storage_name
    file.file.seek(0)
    with local_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/static/{folder}/{storage_name}"
