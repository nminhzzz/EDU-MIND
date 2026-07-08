"""
Repository cho ClassroomStudent — Giai đoạn 4.
"""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.repositories.base import BaseRepository
from app.models.classroom_student import ClassroomStudent


class ClassroomStudentRepository(
    BaseRepository[ClassroomStudent, BaseModel, BaseModel]
):
    """
    Repository truy xuất dữ liệu cho bảng classroom_students.
    """

    def get_by_relation(
        self, db: Session, classroom_id: int, student_id: int
    ) -> ClassroomStudent:
        """Kiểm tra xem học sinh đã ở trong lớp học chưa."""
        return (
            db.query(ClassroomStudent)
            .filter(
                ClassroomStudent.classroom_id == classroom_id,
                ClassroomStudent.student_id == student_id,
            )
            .first()
        )

    def teacher_teaches_student(
        self, db: Session, teacher_id: int, student_id: int
    ) -> bool:
        """Return True if the student belongs to any classroom taught by the teacher."""
        return (
            db.query(ClassroomStudent)
            .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
            .filter(
                Classroom.teacher_id == teacher_id,
                ClassroomStudent.student_id == student_id,
            )
            .first()
            is not None
        )

    def get_by_classroom(
        self, db: Session, classroom_id: int
    ) -> List[ClassroomStudent]:
        """Return all enrollments for a classroom."""
        return (
            db.query(ClassroomStudent)
            .filter(ClassroomStudent.classroom_id == classroom_id)
            .all()
        )

    def count_by_classroom(self, db: Session, classroom_id: int) -> int:
        """Return the number of students enrolled in a classroom."""
        return (
            db.query(ClassroomStudent)
            .filter(ClassroomStudent.classroom_id == classroom_id)
            .count()
        )

    def count_unique_students_for_teacher(self, db: Session, teacher_id: int) -> int:
        """Return distinct students across all classrooms taught by a teacher."""
        return (
            db.query(ClassroomStudent.student_id)
            .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
            .filter(Classroom.teacher_id == teacher_id)
            .distinct()
            .count()
        )

    def stage_enrollment(
        self, db: Session, classroom_id: int, student_id: int
    ) -> ClassroomStudent:
        """Stage a classroom enrollment in the current session (no commit)."""
        db_relation = ClassroomStudent(
            classroom_id=classroom_id, student_id=student_id
        )
        db.add(db_relation)
        return db_relation


classroom_student_repository = ClassroomStudentRepository(ClassroomStudent)
