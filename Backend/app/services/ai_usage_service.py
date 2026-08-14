"""Application-level persistence for provider token metadata."""

from collections.abc import Callable

from app.core.config import settings
from app.core.logging import get_logger
from app.database.mysql import SessionLocal
from app.models.ai_usage import AIUsage

logger = get_logger(__name__)


def build_usage_recorder(
    request_type: str, *, goal_id: int | None = None, plan_id: int | None = None
) -> Callable[[dict], None]:
    def record(usage: dict) -> None:
        with SessionLocal() as db:
            db.add(
                AIUsage(
                    request_type=request_type,
                    goal_id=goal_id,
                    plan_id=plan_id,
                    model=settings.DEEPSEEK_MODEL,
                    prompt_tokens=int(usage.get("prompt_tokens") or 0),
                    completion_tokens=int(usage.get("completion_tokens") or 0),
                    cached_tokens=int(usage.get("cached_tokens") or 0),
                    total_tokens=int(usage.get("total_tokens") or 0),
                )
            )
            db.commit()

    return record
