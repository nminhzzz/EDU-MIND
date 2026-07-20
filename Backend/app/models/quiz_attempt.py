import datetime
from sqlalchemy import Column, BigInteger, JSON, Numeric, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (
        Index("ix_quiz_attempt_student_quiz", "student_id", "quiz_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id = Column(
        BigInteger, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Đáp án học sinh chọn: [{"question_index": 0, "answer": "A", "is_correct": true}, ...]
    answers = Column(JSON, nullable=False)

    # Điểm số (thang 10)
    score = Column(Numeric(5, 2), nullable=False)

    correct_count = Column(Integer, nullable=False, default=0)
    wrong_count = Column(Integer, nullable=False, default=0)

    # Thời gian làm bài (giây)
    duration_seconds = Column(Integer, nullable=False)

    # Số lần thoát tab / đổi màn hình
    tab_violations_count = Column(Integer, nullable=False, default=0)

    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", foreign_keys=[student_id])
