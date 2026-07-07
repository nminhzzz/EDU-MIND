import datetime
from sqlalchemy import Column, BigInteger, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudyPlanProgress(Base):
    """
    Theo dõi tiến độ hoàn thành (%) của từng task trong study_plans.
    Cho phép cập nhật tiến trình nhiều lần trước khi task hoàn thành 100%.
    """

    __tablename__ = "study_plan_progress"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    study_plan_id = Column(
        BigInteger, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False
    )
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Phần trăm hoàn thành: 0.00 -> 100.00
    completion_percent = Column(Numeric(5, 2), nullable=False, default=0.0)

    # Thời điểm hoàn thành 100% (NULL nếu chưa xong)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    study_plan = relationship("StudyPlan", foreign_keys=[study_plan_id])
    student = relationship("User", foreign_keys=[student_id])
