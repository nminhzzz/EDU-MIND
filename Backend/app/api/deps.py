"""
FastAPI dependency injection.
Provides: get_db (MySQL session), get_current_user (JWT auth),
role-based guards, and rate_limiter.
"""

from dataclasses import dataclass
from typing import Generator, Optional
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserRole
from app.core.security import decode_access_token
from app.database.mysql import SessionLocal
from app.database.redis import get_redis
from app.models.user import User
from app.repositories.user_repository import user_repository

# Bearer token extractor — auto_error=False so cookie-based auth doesn't crash here.
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy DB session for each request.
    The session is always closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Token extraction
# ---------------------------------------------------------------------------

def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    Extract the access token from:
    1. Authorization: Bearer <token> header (highest priority — best CSRF protection).
    2. HttpOnly 'access_token' cookie (with Origin/Referer CSRF check for write methods).
    """
    if credentials and credentials.credentials:
        return credentials.credentials

    token = request.cookies.get("access_token")
    if token:
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            _verify_csrf_origin(request)
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không tìm thấy thông tin xác thực (token). Vui lòng đăng nhập.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _verify_csrf_origin(request: Request) -> None:
    """
    Raise 403 if the request origin is not in the allowed CORS list.

    Both the Origin header and the Referer header are checked. The Referer
    is parsed with urlparse so only scheme+host+port is compared — a raw
    startswith() check is vulnerable to subdomain confusion attacks where an
    attacker registers a domain like 'http://localhost:3000.evil.com'.
    """
    allowed = set(settings.BACKEND_CORS_ORIGINS)
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    def _origin_from_referer(ref: str) -> str:
        """Extract scheme://host:port from a full Referer URL."""
        parsed = urlparse(ref)
        # urlparse stores host+port together in netloc
        return f"{parsed.scheme}://{parsed.netloc}"

    is_trusted = (origin and origin in allowed) or (
        referer and _origin_from_referer(referer) in allowed
    )

    if not is_trusted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cảnh báo CSRF: Request bị từ chối do không trùng khớp Origin được tin tưởng.",
        )


# ---------------------------------------------------------------------------
# Current user / role guards
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TokenUser:
    """JWT-derived principal for long-lived streams — avoids holding a DB session."""

    id: int
    role: UserRole


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token_user(token: str = Depends(get_token_from_request)) -> TokenUser:
    """
    Decode the access token without opening a DB session.

    Use for SSE/streaming endpoints so get_db is not held for the stream lifetime.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise _invalid_credentials()

    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        raise _invalid_credentials()

    try:
        return TokenUser(id=int(user_id), role=UserRole(role))
    except ValueError as exc:
        raise _invalid_credentials() from exc


def get_current_student_from_token(
    user: TokenUser = Depends(get_token_user),
) -> TokenUser:
    """Student guard for streaming endpoints — no DB lookup."""
    if user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có quyền truy cập endpoint này.",
        )
    return user


def get_current_user(
    token: str = Depends(get_token_from_request),
    db: Session = Depends(get_db),
) -> User:
    """Validate the access token and return the authenticated User."""
    payload = decode_access_token(token)
    if payload is None:
        raise _invalid_credentials()

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise _invalid_credentials()

    user = user_repository.get(db, int(user_id))
    if user is None:
        raise _invalid_credentials()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa.",
        )

    return user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Allow only students (and admins) to access the endpoint."""
    if current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có quyền truy cập endpoint này.",
        )
    return current_user


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Allow only teachers (and admins) to access the endpoint."""
    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giáo viên mới có quyền truy cập endpoint này.",
        )
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow only admins to access the endpoint."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có quyền truy cập hệ thống quản trị này.",
        )
    return current_user


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

def rate_limiter(limit: int, period_seconds: int, action: str = "default"):
    """
    Dependency that limits API call frequency per student using Redis.

    Args:
        limit: Maximum number of requests allowed within *period_seconds*.
        period_seconds: Sliding window duration in seconds.
        action: Logical name for the rate-limited action — used to namespace
                the Redis key so different endpoints don't share a counter.
    """

    async def dependency(current_user: User = Depends(get_current_student)) -> None:
        redis = get_redis()
        key = f"rate_limit:{action}:{current_user.id}"

        current_count = redis.get(key)
        if current_count and int(current_count) >= limit:
            ttl = redis.ttl(key)
            wait = ttl if ttl > 0 else period_seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Tần suất gọi quá nhanh! Vui lòng thử lại sau {wait} giây.",
            )

        pipeline = redis.pipeline()
        pipeline.incr(key)
        if not current_count:
            pipeline.expire(key, period_seconds)
        pipeline.execute()

    return dependency
