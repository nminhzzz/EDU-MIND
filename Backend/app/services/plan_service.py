"""
Daily study plan use cases — list, read, and update with progress tracking.
"""

from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import PlanStatus
from app.database.unit_of_work import commit_or_rollback
from app.models.study_plan import StudyPlan
from app.repositories.plan_repository import plan_repository
from app.schemas.study_plan import StudyPlanUpdate


def list_student_plans(
    db: Session,
    student_id: int,
    *,
    goal_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[StudyPlan]:
    """Return filtered study plans for a student."""
    return plan_repository.list_for_student(
        db,
        student_id,
        goal_id=goal_id,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date,
        active_goals_only=goal_id is None,
    )


def get_student_plan(db: Session, plan_id: int, student_id: int) -> StudyPlan:
    """Return one study plan owned by the student."""
    plan = plan_repository.get_for_student(db, plan_id, student_id)
    if not plan:
        raise ValueError("Không tìm thấy lịch học này.")
    return plan


def update_student_plan(
    db: Session, plan_id: int, student_id: int, body: StudyPlanUpdate
) -> StudyPlan:
    """Update a study plan and sync progress when status changes."""
    plan = get_student_plan(db, plan_id, student_id)
    update_data = body.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] == PlanStatus.DONE:
        raise ValueError(
            "Bạn không thể tự tích hoàn thành nhiệm vụ này. Hãy hoàn thành bài kiểm tra nhanh đạt từ 8 điểm trở lên để hệ thống tự động xác nhận."
        )

    for field, value in update_data.items():
        setattr(plan, field, value)

    if "status" in update_data:
        plan_repository.upsert_progress_for_status(
            db,
            plan,
            student_id,
            update_data["status"],
            datetime.now(timezone.utc),
        )

    commit_or_rollback(db)
    db.refresh(plan)
    return plan
