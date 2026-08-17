from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, JSON, String, Text

from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AIJob(Base):
    """User-owned, cancellable background AI operation."""

    __tablename__ = "ai_jobs"
    __table_args__ = (
        Index("ix_ai_jobs_owner_created", "user_id", "created_at"),
        Index("ix_ai_jobs_status", "status"),
    )

    id = Column(String(36), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(String(40), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    celery_task_id = Column(String(255), nullable=True)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)
