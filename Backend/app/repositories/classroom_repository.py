"""
Repository cho Classroom — Giai đoạn 4.
"""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate


class ClassroomRepository(BaseRepository[Classroom, ClassroomCreate, ClassroomUpdate]):
    """
    Repository truy xuất dữ liệu cho bảng classrooms.
    """

    def get_by_teacher(self, db: Session, teacher_id: int) -> List[Classroom]:
        """Lấy danh sách các lớp do giáo viên này dạy."""
        return db.query(Classroom).filter(Classroom.teacher_id == teacher_id).all()

    def get_by_student(self, db: Session, student_id: int) -> List[Classroom]:
        """Lấy danh sách các lớp học sinh này đã tham gia."""
        return (
            db.query(Classroom)
            .join(ClassroomStudent, ClassroomStudent.classroom_id == Classroom.id)
            .filter(ClassroomStudent.student_id == student_id)
            .all()
        )

    def get_by_code(self, db: Session, class_code: str) -> Classroom:
        """Tìm lớp học theo class_code."""
        return db.query(Classroom).filter(Classroom.class_code == class_code).first()


classroom_repository = ClassroomRepository(Classroom)
