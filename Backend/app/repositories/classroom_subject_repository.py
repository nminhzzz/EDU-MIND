"""
Repository cho ClassroomSubject — Giai đoạn 4.
"""
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.classroom_subject import ClassroomSubject


class ClassroomSubjectRepository(BaseRepository[ClassroomSubject, BaseModel, BaseModel]):
    """
    Repository truy xuất dữ liệu cho bảng classroom_subjects.
    """
    def get_by_relation(self, db: Session, classroom_id: int, subject_id: int) -> ClassroomSubject:
        """Kiểm tra xem môn học đã được gán vào lớp học chưa."""
        return (
            db.query(ClassroomSubject)
            .filter(
                ClassroomSubject.classroom_id == classroom_id,
                ClassroomSubject.subject_id == subject_id
            )
            .first()
        )


classroom_subject_repository = ClassroomSubjectRepository(ClassroomSubject)
