"""
Repository cho Classroom — Giai đoạn 4.
"""

from typing import List, Optional
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

    def count_all(self, db: Session) -> int:
        """Return the total number of classrooms."""
        return db.query(Classroom).count()

    def stage_classroom(
        self,
        db: Session,
        *,
        teacher_id: int,
        subject_id: int,
        class_name: str,
        class_code: str,
        description: Optional[str],
    ) -> Classroom:
        """Stage a new classroom in the current session (no commit)."""
        db_obj = Classroom(
            teacher_id=teacher_id,
            subject_id=subject_id,
            class_name=class_name,
            class_code=class_code,
            description=description,
        )
        db.add(db_obj)
        return db_obj


classroom_repository = ClassroomRepository(Classroom)
