"""
Repository for QuizAttempt records.
"""

from typing import List, Optional, Tuple

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.repositories.base import BaseRepository


class AttemptRepository(BaseRepository[QuizAttempt, BaseModel, BaseModel]):
    """Data access for the quiz_attempts table."""

    def get_by_student(self, db: Session, student_id: int) -> List[QuizAttempt]:
        """Return all attempts submitted by a student."""
        return db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()

    def get_by_student_and_subject(
        self, db: Session, student_id: int, subject_id: int
    ) -> List[QuizAttempt]:
        """Return attempts for a student filtered by subject via quiz join."""
        return (
            db.query(QuizAttempt)
            .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
            .filter(QuizAttempt.student_id == student_id, Quiz.subject_id == subject_id)
            .all()
        )

    def get_with_quiz_by_student(
        self, db: Session, student_id: int
    ) -> List[Tuple[QuizAttempt, Quiz]]:
        """Return attempts with quiz data, most recent first."""
        return (
            db.query(QuizAttempt, Quiz)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .options(joinedload(Quiz.subject))
            .filter(QuizAttempt.student_id == student_id)
            .order_by(QuizAttempt.submitted_at.desc())
            .all()
        )

    def get_classroom_attempts_with_users(
        self, db: Session, classroom_id: int
    ) -> List[Tuple[QuizAttempt, Quiz, User]]:
        """Return attempts for a classroom with quiz and student details."""
        return (
            db.query(QuizAttempt, Quiz, User)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .join(User, QuizAttempt.student_id == User.id)
            .filter(Quiz.classroom_id == classroom_id)
            .all()
        )

    def stage_attempt(
        self,
        db: Session,
        *,
        quiz_id: int,
        student_id: int,
        answers: list,
        score: float,
        correct_count: int,
        wrong_count: int,
        duration_seconds: int,
    ) -> QuizAttempt:
        """Stage a quiz attempt in the current session (no commit)."""
        db_attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            answers=answers,
            score=score,
            correct_count=correct_count,
            wrong_count=wrong_count,
            duration_seconds=duration_seconds,
        )
        db.add(db_attempt)
        return db_attempt

    def has_attempt(
        self, db: Session, quiz_id: int, student_id: int
    ) -> bool:
        """Return True if the student has submitted an attempt for the quiz."""
        return (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.student_id == student_id,
            )
            .first()
            is not None
        )

    def count_for_student(self, db: Session, student_id: int) -> int:
        """Return the total number of quiz attempts for a student."""
        return (
            db.query(QuizAttempt)
            .filter(QuizAttempt.student_id == student_id)
            .count()
        )

    def avg_score_for_student(
        self, db: Session, student_id: int
    ) -> Optional[float]:
        """Return the average quiz score for a student, or None if no attempts."""
        avg_score = (
            db.query(func.avg(QuizAttempt.score))
            .filter(QuizAttempt.student_id == student_id)
            .scalar()
        )
        return float(avg_score) if avg_score is not None else None


attempt_repository = AttemptRepository(QuizAttempt)
