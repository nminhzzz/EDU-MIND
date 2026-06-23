import datetime
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class ClassroomSubject(Base):
    """Bảng trung gian nhiều-nhiều giữa Classroom và Subject."""
    __tablename__ = "classroom_subjects"

    # Đảm bảo mỗi môn học chỉ được gán 1 lần vào mỗi lớp
    __table_args__ = (
        UniqueConstraint("classroom_id", "subject_id", name="uq_classroom_subject"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    classroom_id = Column(
        BigInteger,
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False
    )
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    classroom = relationship("Classroom", back_populates="subjects")
    subject = relationship("Subject", foreign_keys=[subject_id])
