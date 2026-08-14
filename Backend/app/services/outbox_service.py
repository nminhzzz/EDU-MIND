"""Transactional outbox used for reliable Celery publication."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.mysql import SessionLocal
from app.models.outbox_job import OutboxJob

logger = get_logger(__name__)

MAX_DISPATCH_ATTEMPTS = 20
ALLOWED_TASKS = frozenset(
    {
        "app.workers.tasks.task_generate_plan_materials",
        "app.workers.tasks.task_generate_attempt_assessment",
        "app.workers.tasks.task_update_analytics",
        "app.workers.tasks.task_index_study_document",
    }
)


def stage_outbox_job(
    db: Session,
    *,
    task_name: str,
    args: list[Any],
    unique_key: str,
    kwargs: dict[str, Any] | None = None,
) -> OutboxJob:
    """Stage a job without committing; the caller owns the transaction."""
    if task_name not in ALLOWED_TASKS:
        raise ValueError(f"Task is not allowed in the transactional outbox: {task_name}")
    job = OutboxJob(
        task_name=task_name,
        payload={"args": args, "kwargs": kwargs or {}},
        unique_key=unique_key,
    )
    db.add(job)
    return job


def dispatch_pending_outbox_jobs(limit: int = 100) -> dict[str, int]:
    """Publish due jobs. A crash after publish can duplicate, so consumers remain idempotent."""
    from app.workers.celery_app import celery

    sent = 0
    failed = 0
    now = datetime.now(timezone.utc)
    for _ in range(limit):
        with SessionLocal() as db:
            job = (
                db.query(OutboxJob)
                .filter(
                    OutboxJob.status.in_(("pending", "failed")),
                    OutboxJob.available_at <= now,
                    OutboxJob.attempts < MAX_DISPATCH_ATTEMPTS,
                )
                .order_by(OutboxJob.id)
                .with_for_update(skip_locked=True)
                .first()
            )
            if job is None:
                break
            try:
                if job.task_name not in ALLOWED_TASKS:
                    raise ValueError(f"Rejected non-allowlisted task: {job.task_name}")
                payload = job.payload or {}
                celery.send_task(
                    job.task_name,
                    args=payload.get("args", []),
                    kwargs=payload.get("kwargs", {}),
                )
                job.status = "dispatched"
                job.attempts += 1
                job.last_error = None
                sent += 1
            except Exception as exc:
                job.status = "failed"
                job.attempts += 1
                delay_seconds = min(300, 2 ** min(job.attempts, 8))
                job.available_at = now + timedelta(seconds=delay_seconds)
                job.last_error = str(exc)[:2000]
                failed += 1
                logger.warning("Outbox publish failed for job %s: %s", job.id, exc)
            db.commit()

    return {"sent": sent, "failed": failed}
