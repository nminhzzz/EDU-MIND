"""
Service xử lý các nghiệp vụ liên quan đến Người dùng (Users) — Giai đoạn 4.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.admin import AdminUserCreate, AdminUserUpdate
from app.repositories.user_repository import user_repository
from app.core.security import hash_password


def list_users_admin(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Admin lấy danh sách người dùng kèm lọc theo role/trạng thái."""
    return user_repository.get_multi_filtered(
        db, role=role, is_active=is_active, skip=skip, limit=limit
    )


def create_user_admin(db: Session, obj_in: AdminUserCreate) -> User:
    """Admin tạo tài khoản thành viên mới thủ công."""
    existing = user_repository.get_by_email(db, email=obj_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email này đã được đăng ký sử dụng."
        )

    # Chuyển đổi payload để hash mật khẩu trước khi tạo
    db_obj = User(
        email=obj_in.email,
        password_hash=hash_password(obj_in.password),
        full_name=obj_in.full_name,
        role=obj_in.role,
        grade=obj_in.grade,
        is_active=True
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user_admin(
    db: Session,
    user_id: int,
    obj_in: AdminUserUpdate,
    current_admin_id: int
) -> User:
    """Admin cập nhật thông tin người dùng (chặn tự vô hiệu hóa)."""
    user = user_repository.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản người dùng."
        )

    # Kiểm tra trùng email
    if obj_in.email is not None:
        existing = user_repository.get_by_email(db, email=obj_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Địa chỉ email đã được sử dụng bởi một tài khoản khác."
            )
        user.email = obj_in.email

    # Chốt chặn tự khóa mình
    if obj_in.is_active is not None:
        if user_id == current_admin_id and obj_in.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn không thể tự vô hiệu hóa tài khoản quản trị viên của chính mình."
            )
        user.is_active = obj_in.is_active

    if obj_in.password is not None:
        user.password_hash = hash_password(obj_in.password)
    if obj_in.full_name is not None:
        user.full_name = obj_in.full_name
    if obj_in.role is not None:
        user.role = obj_in.role
    if obj_in.grade is not None:
        user.grade = obj_in.grade

    db.commit()
    db.refresh(user)
    return user


def delete_user_admin(db: Session, user_id: int, current_admin_id: int) -> User:
    """Admin xóa tài khoản người dùng (chặn tự xóa)."""
    if user_id == current_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể tự xóa tài khoản quản trị viên của chính mình."
        )

    user = user_repository.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản người dùng."
        )

    return user_repository.remove(db, id=user_id)
