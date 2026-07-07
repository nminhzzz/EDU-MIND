import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Numeric,
    Date,
    Enum,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudyGoal(Base):
    __tablename__ = "study_goals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject_id = Column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)

    # Điểm số mục tiêu (thang 10 hoặc 100 tùy cấu hình)
    target_score = Column(Numeric(5, 2), nullable=False)

    deadline = Column(Date, nullable=False)

    status = Column(
        Enum("active", "completed", "cancelled", name="goal_status"),
        nullable=False,
        default="active",
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship(
        "User", foreign_keys=[student_id], back_populates="study_goals"
    )
    subject = relationship(
        "Subject", foreign_keys=[subject_id], back_populates="study_goals"
    )
    study_plans = relationship(
        "StudyPlan", back_populates="goal", cascade="all, delete-orphan"
    )
