import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Date,
    Time,
    Boolean,
    Enum,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    goal_id = Column(
        BigInteger, ForeignKey("study_goals.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    task_description = Column(Text, nullable=True)
    rag_content = Column(Text, nullable=True)

    study_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # True nếu task được AI sinh ra, False nếu giáo viên tự tạo
    ai_generated = Column(Boolean, default=True)

    status = Column(
        Enum("todo", "doing", "done", name="plan_task_status"),
        nullable=False,
        default="todo",
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    goal = relationship(
        "StudyGoal", foreign_keys=[goal_id], back_populates="study_plans"
    )
    progress_records = relationship(
        "StudyPlanProgress", back_populates="study_plan", cascade="all, delete-orphan"
    )

    @property
    def subject_id(self) -> int:
        return self.goal.subject_id if self.goal else None
