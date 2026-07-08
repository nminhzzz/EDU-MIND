"""
Repository for LearningAnalytic records.
"""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.learning_analytic import LearningAnalytic
from app.repositories.base import BaseRepository


class AnalyticRepository(BaseRepository[LearningAnalytic, BaseModel, BaseModel]):
    """Data access for the learning_analytics table."""

    def get_by_student_and_subject(
        self, db: Session, student_id: int, subject_id: int
    ) -> Optional[LearningAnalytic]:
        """Return the analytic profile for a student/subject pair, if it exists."""
        return (
            db.query(LearningAnalytic)
            .filter(
                LearningAnalytic.student_id == student_id,
                LearningAnalytic.subject_id == subject_id,
            )
            .first()
        )

    def list_by_student(
        self, db: Session, student_id: int
    ) -> List[LearningAnalytic]:
        """Return all analytic profiles for a student."""
        return (
            db.query(LearningAnalytic)
            .filter(LearningAnalytic.student_id == student_id)
            .all()
        )

    def ensure_for_student_subject(
        self, db: Session, student_id: int, subject_id: int
    ) -> LearningAnalytic:
        """
        Return the existing analytic record or create a blank one (flush only).
        The caller owns the transaction commit.
        """
        analytic = self.get_by_student_and_subject(db, student_id, subject_id)
        if analytic:
            return analytic

        analytic = LearningAnalytic(
            student_id=student_id,
            subject_id=subject_id,
            average_score=0.0,
            quizzes_completed=0,
            weak_topics=[],
            strong_topics=[],
        )
        db.add(analytic)
        db.flush()
        return analytic


analytic_repository = AnalyticRepository(LearningAnalytic)
