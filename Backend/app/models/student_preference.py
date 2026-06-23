import datetime
from sqlalchemy import Column, BigInteger, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudentPreference(Base):
    __tablename__ = "student_preferences"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # 1-1 với users
    )

    # Số giờ học mỗi ngày mong muốn
    study_hours_per_day = Column(Integer, nullable=True, default=2)

    # Khung giờ ưa thích: "morning", "afternoon", "evening", "night"
    preferred_study_time = Column(String(50), nullable=True, default="evening")

    # Lịch rảnh theo ngày trong tuần: {"mon": true, "tue": false, ...}
    available_schedule = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    student = relationship("User", foreign_keys=[student_id], back_populates="preference")
