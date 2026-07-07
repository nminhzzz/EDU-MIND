import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Enum,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class Notification(Base):
    __tablename__ = "notifications"

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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
