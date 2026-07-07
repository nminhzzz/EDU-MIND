"""
API xác thực: Đăng ký + Đăng nhập.
Endpoints:
    POST /api/v1/auth/register  — Tạo tài khoản mới
    POST /api/v1/auth/login     — Đăng nhập, nhận JWT token
    GET  /api/v1/auth/me        — Xem thông tin cá nhân (cần token)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_token_from_request
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token,
    blacklist_token,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserResponse
from app.core.config import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Tạo tài khoản học sinh / giáo viên mới."""
    # Chuẩn hóa email: viết thường + xóa khoảng trắng thừa
    email_normalized = body.email.lower().strip()

    # Kiểm tra email trùng
    existing = db.query(User).filter(User.email == email_normalized).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được đăng ký."
        )

    user = User(
        email=email_normalized,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        grade=body.grade if body.role == "student" else None,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", summary="Đăng nhập và nhận JWT token qua Cookies")
def login(response: Response, body: LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập bằng email + password.
    Cấp tokens lưu trong HttpOnly Cookies bảo mật cao (chống XSS).
    """
    # Chuẩn hóa email để đối chiếu DB chính xác
    email_normalized = body.email.lower().strip()

    user = db.query(User).filter(User.email == email_normalized).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị vô hiệu hóa."
        )

    # 1. Tạo tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 2. Thiết lập access_token vào Cookie (chuyển sang httponly=True để chống XSS hoàn toàn)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # Không cho phép JS đọc để bảo mật tối đa
        secure=settings.COOKIE_SECURE,  # Bật True ở production
        samesite="lax",
    )

    # 3. Thiết lập refresh_token vào HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,  # Không cho phép JS đọc
        secure=settings.COOKIE_SECURE,  # Bật True ở production
        samesite="lax",
        path="/api/v1/auth/refresh",  # Chỉ gửi cookie này khi gọi endpoint refresh để tăng bảo mật
    )

    return {
        "message": "Đăng nhập thành công!",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh", summary="Cấp lại access token từ refresh token trong HttpOnly Cookie"
)
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """
    Học sinh tự động gia hạn token: đọc refresh_token từ HttpOnly cookie,
    xác thực và trả về access_token mới trong cookie.
    """
    # 1. Lấy refresh_token từ HttpOnly Cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy Refresh Token. Vui lòng đăng nhập lại.",
        )

    # 2. Giải mã và xác thực refresh token
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin người dùng.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa.",
        )

    # 3. Tạo access_token mới
    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    # 4. Ghi đè access_token mới vào Cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # Không cho phép JS đọc
        secure=settings.COOKIE_SECURE,  # Bật True ở production
        samesite="lax",
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", summary="Đăng xuất và xóa các cookies")
def logout(
    request: Request, response: Response, token: str = Depends(get_token_from_request)
):
    """
    Đăng xuất và vô hiệu hóa token:
    1. Cho Access Token hiện tại vào blacklist (Redis) để ngăn chặn phát sinh cuộc gọi API sau đó.
    2. Cho Refresh Token hiện tại vào blacklist (Redis) để chặn refresh.
    3. Xóa sạch cookies ở phía client.
    """
    from datetime import datetime, timezone

    # 1. Thu hồi Access Token hiện tại
    payload = decode_access_token(token)
    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            now = datetime.now(timezone.utc).timestamp()
            remaining = int(exp - now)
            if remaining > 0:
                blacklist_token(jti, remaining)

    # 2. Thu hồi Refresh Token hiện tại
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        refresh_payload = decode_refresh_token(refresh_token)
        if refresh_payload:
            r_jti = refresh_payload.get("jti")
            r_exp = refresh_payload.get("exp")
            if r_jti and r_exp:
                now = datetime.now(timezone.utc).timestamp()
                remaining = int(r_exp - now)
                if remaining > 0:
                    blacklist_token(r_jti, remaining)

    # 3. Xóa các Cookies khỏi trình duyệt
    response.delete_cookie(
        key="access_token", secure=settings.COOKIE_SECURE, samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth/refresh",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
    return {"message": "Đăng xuất thành công!"}


@router.get(
    "/me", response_model=UserResponse, summary="Xem thông tin tài khoản đang đăng nhập"
)
def get_me(current_user: User = Depends(get_current_user)):
    """Trả về thông tin người dùng hiện tại từ JWT token."""
    return current_user
