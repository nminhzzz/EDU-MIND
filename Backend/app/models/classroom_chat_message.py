from datetime import datetime, timezone
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ClassroomChatMessage(Base):
    __tablename__ = "classroom_chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    classroom_id = Column(
        BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    sender_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    # Relationships
    classroom = relationship("Classroom")
    sender = relationship("User", foreign_keys=[sender_id])
