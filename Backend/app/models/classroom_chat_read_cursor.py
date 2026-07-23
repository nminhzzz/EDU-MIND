"""
ClassroomChatReadCursor — tracks the last message each user has read
in each classroom, enabling unread-count queries.
"""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ClassroomChatReadCursor(Base):
    __tablename__ = "classroom_chat_read_cursors"

    __table_args__ = (
        UniqueConstraint("classroom_id", "user_id", name="uq_chat_cursor_classroom_user"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    classroom_id = Column(
        BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # ID of the last ClassroomChatMessage the user has seen
    last_read_message_id = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    user = relationship("User", foreign_keys=[user_id])
