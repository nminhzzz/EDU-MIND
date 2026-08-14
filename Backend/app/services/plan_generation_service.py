"""Use cases for durable, lazy generation of one study plan."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database.unit_of_work import commit_or_rollback
from app.models.study_plan import StudyPlan
from app.repositories.plan_repository import plan_repository
from app.services.outbox_service import stage_outbox_job


def request_plan_generation(
    db: Session,
    plan: StudyPlan,
    *,
    recover_stale: bool = False,
) -> bool:
    """Queue exactly one attempt, serializing concurrent requests per plan row."""
    # React Strict Mode, double-clicks, and network retries can arrive together.
    # Lock and refresh the row so only the first transaction can stage an outbox job.
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan.id)
        .populate_existing()
        .with_for_update()
        .one()
    )

    if recover_stale and plan.generation_status == "generating":
        started_at = plan.generation_started_at
        if started_at is not None and started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        if started_at and started_at < datetime.now(timezone.utc) - timedelta(minutes=20):
            plan_repository.fail_generation(db, plan, "Generation worker timed out; queued for recovery.")

    if not plan_repository.queue_generation(db, plan):
        return False

    stage_outbox_job(
        db,
        task_name="app.workers.tasks.task_generate_single_plan_material",
        args=[plan.id],
        unique_key=f"plan-generation:{plan.id}:{plan.generation_attempts}",
    )
    commit_or_rollback(db)
    db.refresh(plan)
    return True


def claim_plan_generation(db: Session, plan_id: int) -> bool:
    claimed = plan_repository.claim_generation(db, plan_id)
    commit_or_rollback(db)
    return claimed
