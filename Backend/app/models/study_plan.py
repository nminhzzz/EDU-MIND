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
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from app.models.base import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"
    __table_args__ = (
        Index("ix_study_plan_student_date", "student_id", "study_date"),
        Index("ix_study_plan_goal", "goal_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    goal_id = Column(
        BigInteger, ForeignKey("study_goals.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    task_description = Column(Text, nullable=True)
    rag_content = Column(Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True)
    lesson_summary = Column(Text, nullable=True)
    generation_status = Column(String(20), nullable=False, default="not_started")
    lesson_status = Column(String(20), nullable=False, default="not_started")
    quiz_status = Column(String(20), nullable=False, default="not_started")
    generation_error = Column(Text, nullable=True)
    generation_attempts = Column(BigInteger, nullable=False, default=0)
    generation_started_at = Column(DateTime, nullable=True)
    generation_finished_at = Column(DateTime, nullable=True)

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
