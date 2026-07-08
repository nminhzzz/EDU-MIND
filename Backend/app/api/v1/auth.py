"""
Authentication endpoints:
    POST /api/v1/auth/register  — Create a new account
    POST /api/v1/auth/login     — Login, receive JWT via HttpOnly cookies
    POST /api/v1/auth/refresh   — Refresh access token
    POST /api/v1/auth/logout    — Revoke tokens and clear cookies
    GET  /api/v1/auth/me        — Return current user info
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_token_from_request
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import (
    authenticate_user,
    refresh_user_tokens,
    register_user,
    revoke_user_tokens,
)
from app.services.email_service import send_welcome_email

router = APIRouter()


def _set_access_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/api/v1/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="access_token", secure=settings.COOKIE_SECURE, samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth/refresh",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> User:
    """Create a new student or teacher account."""
    user = register_user(db, body)
    background_tasks.add_task(send_welcome_email, user.email, user.full_name or user.email)
    return user


@router.post("/login", summary="Đăng nhập và nhận JWT token qua Cookies")
def login(
    response: Response, body: LoginRequest, db: Session = Depends(get_db)
) -> dict:
    """
    Authenticate with email + password.
    Tokens are stored in HttpOnly cookies to prevent XSS.
    """
    access_token, refresh_token = authenticate_user(db, body)
    _set_access_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)

    # Tokens are delivered exclusively via HttpOnly cookies to prevent XSS.
    # Do NOT include access_token in the response body.
    return {"message": "Đăng nhập thành công!", "token_type": "bearer"}


@router.post("/refresh", summary="Cấp lại access token từ refresh token")
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> dict:
    """
    Silently renew the access token using the HttpOnly refresh token cookie.
    Implements refresh token rotation: the consumed refresh token is blacklisted
    and a brand-new one is issued, so each token can only be used once.
    """
    refresh_token = request.cookies.get("refresh_token")
    access_token, new_refresh_token = refresh_user_tokens(db, refresh_token or "")

    _set_access_cookie(response, access_token)
    _set_refresh_cookie(response, new_refresh_token)

    # Tokens are delivered exclusively via HttpOnly cookies — never expose them
    # in the response body, as that would defeat the XSS-protection guarantee.
    return {"message": "Token đã được làm mới thành công.", "token_type": "bearer"}


@router.post("/logout", summary="Đăng xuất và xóa các cookies")
def logout(
    request: Request,
    response: Response,
    token: str = Depends(get_token_from_request),
) -> dict:
    """
    Revoke both access and refresh tokens by adding them to the Redis blacklist,
    then clear the cookies on the client.
    """
    revoke_user_tokens(token, request.cookies.get("refresh_token"))
    _clear_auth_cookies(response)
    return {"message": "Đăng xuất thành công!"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Xem thông tin tài khoản đang đăng nhập",
)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the currently authenticated user."""
    return current_user
