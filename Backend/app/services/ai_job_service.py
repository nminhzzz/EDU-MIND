from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_job import AIJob
from app.workers.celery_app import celery


TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_ai_job(db: Session, *, user_id: int, job_type: str, payload: dict[str, Any]) -> AIJob:
    job_id = str(uuid.uuid4())
    job = AIJob(
        id=job_id,
        user_id=user_id,
        job_type=job_type,
        status="queued",
        celery_task_id=job_id,
        payload=payload,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        celery.send_task(
            "app.workers.tasks.task_run_ai_job",
            args=[job_id],
            task_id=job_id,
            queue="ai_tasks",
        )
    except Exception as exc:
        job.status = "failed"
        job.error = "Không thể đưa tác vụ vào hàng đợi."
        job.finished_at = _now()
        db.commit()
        raise RuntimeError("Không thể đưa tác vụ AI vào hàng đợi.") from exc
    return job


def get_owned_ai_job(db: Session, *, job_id: str, user_id: int) -> AIJob:
    job = db.query(AIJob).filter(AIJob.id == job_id, AIJob.user_id == user_id).first()
    if not job:
        raise ValueError("Không tìm thấy tác vụ AI.")
    return job


def cancel_ai_job(db: Session, *, job_id: str, user_id: int) -> AIJob:
    job = (
        db.query(AIJob)
        .filter(AIJob.id == job_id, AIJob.user_id == user_id)
        .with_for_update()
        .first()
    )
    if not job:
        raise ValueError("Không tìm thấy tác vụ AI.")
    if job.status in TERMINAL_STATUSES:
        return job

    job.status = "cancelled"
    job.finished_at = _now()
    db.commit()
    celery.control.revoke(job.celery_task_id or job.id, terminate=True, signal="SIGTERM")
    cleanup_job_files(job.payload)
    db.refresh(job)
    return job


def cleanup_job_files(payload: dict[str, Any] | None) -> None:
    temp_dir = (payload or {}).get("temp_dir")
    if not temp_dir:
        return
    target = Path(temp_dir).resolve()
    uploads_root = target.parent
    if uploads_root.name == "ai_jobs" and uploads_root.parent.name == "uploads":
        shutil.rmtree(target, ignore_errors=True)


def serialize_ai_job(job: AIJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }
