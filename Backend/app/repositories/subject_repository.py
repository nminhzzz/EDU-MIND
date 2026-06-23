"""
Repository cho Subject — Giai đoạn 4.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    """
    Repository truy xuất dữ liệu cho bảng subjects.
    """
    def get_by_code(self, db: Session, code: str) -> Optional[Subject]:
        """Lấy thông tin môn học theo mã code duy nhất."""
        return db.query(Subject).filter(Subject.code == code).first()


subject_repository = SubjectRepository(Subject)
