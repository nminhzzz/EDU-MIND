"""
Bảo mật: Hash mật khẩu (bcrypt) + tạo/verify JWT token.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

# --- Bản vá lỗi tương thích giữa passlib và bcrypt 4.x/5.x ---
import bcrypt
if not hasattr(bcrypt, "__about__"):
    class BcryptAboutPatch:
        __version__ = getattr(bcrypt, "__version__", "4.0.0")
    bcrypt.__about__ = BcryptAboutPatch()

from jose import JWTError, jwt

from app.core.config import settings

# ── Cấu hình từ config settings ──────────────────────────────────
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu plain với hash đã lưu trong DB."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt trước khi lưu vào DB."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token.
    - data: payload muốn encode (thường là {"sub": str(user_id)})
    - expires_delta: thời gian hết hạn tùy chỉnh (mặc định theo settings)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Giải mã và xác thực JWT token.
    Trả về payload dict nếu hợp lệ, None nếu hết hạn hoặc sai chữ ký.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """Tạo JWT refresh token với hạn dùng dài (mặc định 7 ngày)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_refresh_token(token: str) -> Optional[dict]:
    """Giải mã và xác thực refresh token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
