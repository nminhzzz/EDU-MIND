from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    Boolean,
    Enum,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        Index("ix_quiz_student_subject", "student_id", "subject_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject_id = Column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    study_plan_id = Column(
        BigInteger, ForeignKey("study_plans.id", ondelete="SET NULL"), nullable=True
    )
    classroom_id = Column(
        BigInteger, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True
    )

    title = Column(String(255), nullable=False)

    difficulty = Column(
        Enum("easy", "medium", "hard", name="quiz_difficulty"),
        nullable=False,
        default="medium",
    )

    total_questions = Column(Integer, nullable=False, default=5)

    # Danh sách câu hỏi lưu dạng JSON:
    # [{"question_text": "...", "options": [{"key": "A", "value": "..."}, ...], "correct_answer": "A", "explanation": "..."}]
    questions = Column(JSON, nullable=False)

    generated_by_ai = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    subject = relationship(
        "Subject", foreign_keys=[subject_id], back_populates="quizzes"
    )
    study_plan = relationship("StudyPlan", foreign_keys=[study_plan_id])
    classroom = relationship("Classroom", back_populates="quizzes")
    attempts = relationship(
        "QuizAttempt", back_populates="quiz", cascade="all, delete-orphan"
    )
