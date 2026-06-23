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


def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> str:
    """
    Trích xuất access token từ:
    1. Cookie 'access_token'
    2. Header 'Authorization: Bearer <token>' (cho Swagger UI/Postman)
    """
    # 1. Thử lấy từ cookie 'access_token'
    token = request.cookies.get("access_token")
    if token:
        return token

    # 2. Thử lấy từ Header Authorization qua HTTPBearer
    if credentials and credentials.credentials:
        return credentials.credentials

    # Nếu không tìm thấy bất kỳ token nào
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không tìm thấy thông tin xác thực (token). Vui lòng đăng nhập.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(get_token_from_request),
    db: Session = Depends(get_db)
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa."
        )

    return user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Dependency chỉ cho phép học sinh (role=student) truy cập."""
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có quyền truy cập endpoint này."
        )
    return current_user


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Dependency chỉ cho phép giáo viên (role=teacher) truy cập."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giáo viên mới có quyền truy cập endpoint này."
        )
    return current_user
