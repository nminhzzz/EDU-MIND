import datetime
from sqlalchemy import Column, BigInteger, JSON, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id = Column(
        BigInteger,
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False
    )
    student_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Đáp án học sinh chọn: [{"question_bank_id": 1, "answer": "A"}, ...]
    answers = Column(JSON, nullable=False)

    # Điểm số (thang 10)
    score = Column(Numeric(5, 2), nullable=False)

    correct_count = Column(Integer, nullable=False, default=0)
    wrong_count = Column(Integer, nullable=False, default=0)

    # Thời gian làm bài (giây)
    duration_seconds = Column(Integer, nullable=False)

    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", foreign_keys=[student_id])
