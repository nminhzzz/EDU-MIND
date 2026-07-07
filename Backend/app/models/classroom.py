import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    subject_id = Column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    class_name = Column(String(255), nullable=False)

    # Mã lớp duy nhất để học sinh tham gia (ví dụ: "TOAN12A-2024")
    class_code = Column(String(50), unique=True, nullable=False, index=True)

    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship(
        "ClassroomStudent", back_populates="classroom", cascade="all, delete-orphan"
    )
    subject = relationship(
        "Subject", foreign_keys=[subject_id], back_populates="classrooms"
    )
    quizzes = relationship("Quiz", back_populates="classroom")
