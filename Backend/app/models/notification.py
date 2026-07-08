from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Enum,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notification_user_read", "user_id", "is_read"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    type = Column(
        Enum("quiz", "plan", "score", "system", name="notification_types"),
        nullable=False,
        default="system",
    )

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
