import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Lớp học chứa đề thi này (NULL nếu là đề AI tự sinh cho cá nhân)
    classroom_id = Column(
        BigInteger,
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=True
    )
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )
    # Giáo viên tạo đề (NULL nếu do AI tạo hoàn toàn)
    teacher_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    title = Column(String(255), nullable=False)

    difficulty = Column(
        Enum("easy", "medium", "hard", name="quiz_difficulty"),
        nullable=False,
        default="medium"
    )

    total_questions = Column(Integer, nullable=False, default=5)

    # True nếu đề thi được AI tự sinh từ QuestionBank
    generated_by_ai = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    classroom = relationship("Classroom", back_populates="quizzes")
    subject = relationship("Subject", foreign_keys=[subject_id], back_populates="quizzes")
    teacher = relationship("User", foreign_keys=[teacher_id])
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
