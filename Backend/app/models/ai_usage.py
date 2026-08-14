import datetime

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String

from app.models.base import Base


class AIUsage(Base):
    """Token usage emitted by one provider request."""

    __tablename__ = "ai_usage"
    __table_args__ = (
        Index("ix_ai_usage_request_created", "request_type", "created_at"),
        Index("ix_ai_usage_goal_plan", "goal_id", "plan_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    request_type = Column(String(40), nullable=False)
    goal_id = Column(BigInteger, nullable=True)
    plan_id = Column(BigInteger, nullable=True)
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    cached_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
