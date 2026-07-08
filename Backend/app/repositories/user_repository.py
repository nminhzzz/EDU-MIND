"""
Repository cho User — Giai đoạn 4.
"""

from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.admin import AdminUserCreate, AdminUserUpdate


class UserRepository(BaseRepository[User, AdminUserCreate, AdminUserUpdate]):
    """
    Repository truy xuất dữ liệu cho bảng users.
    """

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Tìm người dùng theo email (chuẩn hóa chữ thường)."""
        return db.query(User).filter(User.email == email.lower().strip()).first()

    def get_student_by_email(self, db: Session, email: str) -> Optional[User]:
        """Return a student account by email, or None if not found."""
        return (
            db.query(User)
            .filter(User.email == email.lower().strip(), User.role == UserRole.STUDENT)
            .first()
        )

    def get_multi_filtered(
        self,
        db: Session,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Lấy danh sách người dùng kèm lọc theo role và trạng thái hoạt động."""
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def count_by_role(self, db: Session) -> Dict[str, int]:
        """Return user counts grouped by role in a single query."""
        return dict(db.query(User.role, func.count(User.id)).group_by(User.role).all())


user_repository = UserRepository(User)
