import datetime
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class ClassroomStudent(Base):
    """Bảng trung gian nhiều-nhiều giữa Classroom và User (học sinh)."""

    __tablename__ = "classroom_students"

    # Đảm bảo mỗi học sinh chỉ tham gia 1 lần vào mỗi lớp
    __table_args__ = (
        UniqueConstraint("classroom_id", "student_id", name="uq_classroom_student"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    classroom_id = Column(
        BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    classroom = relationship("Classroom", back_populates="students")
    student = relationship("User", foreign_keys=[student_id])
