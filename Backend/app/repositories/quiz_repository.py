"""
Repository cho Quiz — Giai đoạn 4.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.quiz import Quiz
from pydantic import BaseModel


class QuizRepository(BaseRepository[Quiz, BaseModel, BaseModel]):
    """
    Repository truy xuất dữ liệu cho bảng quizzes.
    """

    def get_by_classroom(self, db: Session, classroom_id: int) -> List[Quiz]:
        """Lấy toàn bộ đề thi/bài tập thuộc về lớp học."""
        return db.query(Quiz).filter(Quiz.classroom_id == classroom_id).all()


quiz_repository = QuizRepository(Quiz)
