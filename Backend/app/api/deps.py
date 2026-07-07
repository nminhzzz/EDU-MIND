"""
FastAPI Dependency Injection.
Cung cấp: get_db (MySQL session) + get_current_user (JWT auth).
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.mysql import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User

# Bearer token extractor (auto_error=False để không crash nếu dùng Cookie)
bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    """
    Dependency cung cấp SQLAlchemy DB Session cho mỗi request.
    Tự động đóng session sau khi request hoàn thành.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.core.config import settings


def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    Trích xuất access token từ:
    1. Header 'Authorization: Bearer <token>' (Ưu tiên hàng đầu - chống CSRF tốt nhất)
    2. Cookie 'access_token' (Bảo vệ bổ sung bằng cách kiểm tra Origin/Referer đối với các request ghi)
    """
    # 1. Thử lấy từ Header Authorization trước (Swagger UI, Postman, hoặc SPA custom headers)
    if credentials and credentials.credentials:
        return credentials.credentials

    # 2. Thử lấy từ cookie 'access_token'
    token = request.cookies.get("access_token")
    if token:
        # Bảo vệ chống CSRF đối với các request sửa đổi dữ liệu (POST, PUT, DELETE, PATCH)
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")

            allowed = settings.BACKEND_CORS_ORIGINS
            is_trusted = False

            if origin and origin in allowed:
                is_trusted = True
            elif referer:
                for allowed_origin in allowed:
                    if referer.startswith(allowed_origin):
                        is_trusted = True
                        break

            if not is_trusted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cảnh báo CSRF: Request bị từ chối do không trùng khớp Origin được tin tưởng.",
                )
        return token

    # Nếu không tìm thấy bất kỳ token nào
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không tìm thấy thông tin xác thực (token). Vui lòng đăng nhập.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(get_token_from_request), db: Session = Depends(get_db)
) -> User:
    """
    Dependency xác thực access token từ Cookie hoặc Header và trả về User hiện tại.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị vô hiệu hóa."
        )

    return user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Dependency chỉ cho phép học sinh (role=student) truy cập."""
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có quyền truy cập endpoint này.",
        )
    return current_user


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Dependency chỉ cho phép giáo viên (role=teacher) truy cập."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giáo viên mới có quyền truy cập endpoint này.",
        )
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency chỉ cho phép quản trị viên (role=admin) truy cập."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có quyền truy cập hệ thống quản trị này.",
        )
    return current_user


from app.database.redis import get_redis_client


def rate_limiter(limit: int, period_seconds: int):
    """
    Dependency giới hạn tần suất gọi API của học sinh sử dụng Redis.
    limit: số lượng request tối đa trong khoảng thời gian.
    period_seconds: khoảng thời gian giới hạn (giây).
    """

    async def dependency(current_user: User = Depends(get_current_student)):
        redis_client = get_redis_client()
        key = f"rate_limit:draft:{current_user.id}"

        current_requests = redis_client.get(key)
        if current_requests and int(current_requests) >= limit:
            ttl = redis_client.ttl(key)
            if ttl < 0:
                ttl = period_seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Tần suất tạo lộ trình quá nhanh! Vui lòng thử lại sau {ttl} giây.",
            )

        pipeline = redis_client.pipeline()
        pipeline.incr(key)
        if not current_requests:
            pipeline.expire(key, period_seconds)
        pipeline.execute()

    return dependency
