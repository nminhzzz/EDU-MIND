"""
Transaction boundary helpers for service-layer use cases.

Repositories flush or add to the session; services own commit/rollback.
"""

from sqlalchemy.orm import Session

from app.core.logging import get_logger

logger = get_logger(__name__)


def commit_or_rollback(db: Session) -> None:
    """
    Commit the current transaction.

    On failure, roll back the session and re-raise so the caller (e.g. Celery
    task) can retry or log the error.
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Transaction commit failed — rolled back.")
        raise
