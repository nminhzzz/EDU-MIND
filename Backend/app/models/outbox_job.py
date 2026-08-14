from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, JSON, String, Text

from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OutboxJob(Base):
    """Durable hand-off from a MySQL transaction to the Celery broker."""

    __tablename__ = "outbox_jobs"
    __table_args__ = (
        Index("ix_outbox_jobs_dispatch", "status", "available_at", "id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_name = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    unique_key = Column(String(255), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    available_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)
