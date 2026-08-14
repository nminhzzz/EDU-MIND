"""
Authentication service — registration, login, token refresh, and revocation.

HTTP concerns (cookies, response bodies) stay in the API router.
This module owns credential validation, user persistence, and JWT lifecycle.
"""

from datetime import datetime, timezone
from typing import Callable, Optional
import hashlib

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserRole
from app.core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    consume_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    set_user_active_session,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.core.logging import get_logger

logger = get_logger("security.auth")


def _email_fingerprint(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]


def _revoke_token(raw_token: str, decode_fn: Callable[[str], Optional[dict]]) -> None:
    """Add a JWT to the Redis blacklist for the remainder of its TTL."""
    payload = decode_fn(raw_token)
    if not payload:
        return
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        remaining = int(exp - datetime.now(timezone.utc).timestamp())
        if remaining > 0:
            blacklist_token(jti, remaining)


def register_user(db: Session, body: RegisterRequest) -> User:
    """Create a new student or teacher account."""
    email = body.email.lower().strip()

    if user_repository.get_by_email(db, email=email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký.",
        )

    user = User(
        email=email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        grade=body.grade if body.role == UserRole.STUDENT else None,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(
        "event=registration user_id=%s role=%s email_fp=%s",
        user.id,
        user.role,
        _email_fingerprint(email),
    )
    return user


def authenticate_user(db: Session, body: LoginRequest) -> tuple[str, str]:
    """
    Validate credentials and return (access_token, refresh_token).
    Tokens are meant to be stored in HttpOnly cookies by the caller.
    """
    email = body.email.lower().strip()
    user = user_repository.get_by_email(db, email=email)

    if not user or not verify_password(body.password, user.password_hash):
        logger.warning("event=login_failed email_fp=%s", _email_fingerprint(email))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )
    if not user.is_active:
        logger.warning("event=login_blocked user_id=%s reason=inactive", user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa.",
        )

    import uuid
    sid = uuid.uuid4().hex

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "sid": sid})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "sid": sid})

    # Single Active Session: Register session ID (sid) in Redis
    set_user_active_session(
        user.id,
        sid,
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    logger.info("event=login_success user_id=%s sid=%s", user.id, sid[:12])

    return access_token, refresh_token


def refresh_user_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    """
    Validate a refresh token, blacklist it (rotation), and issue new token pair.
    Returns (access_token, refresh_token).
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy Refresh Token. Vui lòng đăng nhập lại.",
        )

    payload = consume_refresh_token(refresh_token)
    if payload is None:
        logger.warning("event=refresh_rejected reason=invalid_or_replayed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.",
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin người dùng.",
        )

    user = user_repository.get(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa.",
        )

    sid = payload.get("sid") or uuid.uuid4().hex
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "sid": sid})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id), "sid": sid})

    # Single Active Session: Maintain session ID (sid) in Redis
    set_user_active_session(
        user.id,
        sid,
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    logger.info("event=refresh_success user_id=%s sid=%s", user.id, sid[:12])

    return access_token, new_refresh_token


def revoke_user_tokens(access_token: str, refresh_token: Optional[str] = None) -> None:
    """Blacklist access and refresh tokens."""
    _revoke_token(access_token, decode_access_token)
    if refresh_token:
        _revoke_token(refresh_token, decode_refresh_token)
