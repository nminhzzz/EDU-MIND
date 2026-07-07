"""
Repository cho QuizAttempt — Giai đoạn 4.
"""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.quiz_attempt import QuizAttempt
from pydantic import BaseModel


class AttemptRepository(BaseRepository[QuizAttempt, BaseModel, BaseModel]):
    """
    Repository truy xuất dữ liệu cho bảng quiz_attempts.
    """

    def get_by_student(self, db: Session, student_id: int) -> List[QuizAttempt]:
        """Lấy toàn bộ lịch sử nộp bài của học sinh này."""
        return db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()


attempt_repository = AttemptRepository(QuizAttempt)
