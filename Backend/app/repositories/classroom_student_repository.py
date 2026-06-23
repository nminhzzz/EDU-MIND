"""
Repository cho ClassroomStudent — Giai đoạn 4.
"""
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.classroom_student import ClassroomStudent


class ClassroomStudentRepository(BaseRepository[ClassroomStudent, BaseModel, BaseModel]):
    """
    Repository truy xuất dữ liệu cho bảng classroom_students.
    """
    def get_by_relation(self, db: Session, classroom_id: int, student_id: int) -> ClassroomStudent:
        """Kiểm tra xem học sinh đã ở trong lớp học chưa."""
        return (
            db.query(ClassroomStudent)
            .filter(
                ClassroomStudent.classroom_id == classroom_id,
                ClassroomStudent.student_id == student_id
            )
            .first()
        )


classroom_student_repository = ClassroomStudentRepository(ClassroomStudent)
