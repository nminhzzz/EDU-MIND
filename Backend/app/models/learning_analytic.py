import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    Numeric,
    Integer,
    JSON,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class LearningAnalytic(Base):
    __tablename__ = "learning_analytics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject_id = Column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    # Điểm trung bình tổng hợp từ tất cả quiz_attempts của học sinh theo môn
    average_score = Column(Numeric(5, 2), nullable=False, default=0.0)

    # Số đề thi đã hoàn thành
    quizzes_completed = Column(Integer, nullable=False, default=0)

    # Danh sách chủ đề yếu: [{"topic": "Chương 2", "score": 40}]
    weak_topics = Column(JSON, nullable=True)

    # Danh sách chủ đề mạnh: [{"topic": "Chương 1", "score": 85}]
    strong_topics = Column(JSON, nullable=True)

    # Nhận xét tổng hợp của AI (LearningAnalyticsAgent sinh ra)
    ai_feedback = Column(Text, nullable=True)

    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    student = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="learning_analytics" if False else None,
    )
    subject = relationship(
        "Subject", foreign_keys=[subject_id], back_populates="learning_analytics"
    )
