"""
Authentication service — registration, login, token refresh, and revocation.

HTTP concerns (cookies, response bodies) stay in the API router.
This module owns credential validation, user persistence, and JWT lifecycle.
"""

from datetime import datetime, timezone
from typing import Callable, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest


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
    return user


def authenticate_user(db: Session, body: LoginRequest) -> tuple[str, str]:
    """
    Validate credentials and return (access_token, refresh_token).
    Tokens are meant to be stored in HttpOnly cookies by the caller.
    """
    email = body.email.lower().strip()
    user = user_repository.get_by_email(db, email=email)

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa.",
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
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

    payload = decode_refresh_token(refresh_token)
    if payload is None:
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

    _revoke_token(refresh_token, decode_refresh_token)

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return access_token, new_refresh_token


def revoke_user_tokens(access_token: str, refresh_token: Optional[str] = None) -> None:
    """Blacklist access and refresh tokens."""
    _revoke_token(access_token, decode_access_token)
    if refresh_token:
        _revoke_token(refresh_token, decode_refresh_token)
