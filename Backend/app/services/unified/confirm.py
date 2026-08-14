"""
Unified goal confirmation — persist draft directly into MySQL.
"""

from datetime import datetime, date
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.enums import GoalStatus, PlanStatus
from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.subject import Subject
from app.models.user import User
from app.repositories.goal_repository import goal_repository
from app.repositories.plan_repository import plan_repository
from app.schemas.unified_goal import UnifiedGoalPlanResponse
from app.services.outbox_service import stage_outbox_job

logger = get_logger(__name__)

def _cancel_active_goals(
    db: Session, student_id: int, subject_id: int
) -> None:
    goal_repository.cancel_active_for_subject(db, student_id, subject_id)


def _create_study_plans(
    db: Session,
    plan: UnifiedGoalPlanResponse,
    goal_id: int,
    student_id: int,
) -> List[StudyPlan]:
    db_plans: List[StudyPlan] = []

    for day_task in plan.daily_schedule:
        if not day_task.task or not day_task.task.strip():
            continue

        try:
            study_date_val = datetime.strptime(day_task.date, "%Y-%m-%d").date()
        except Exception:
            continue

        start_time_str = day_task.start_time or "18:00"
        end_time_str = day_task.end_time or "20:00"

        try:
            start_time_val = datetime.strptime(start_time_str, "%H:%M").time()
        except Exception:
            start_time_val = datetime.strptime("18:00", "%H:%M").time()

        try:
            end_time_val = datetime.strptime(end_time_str, "%H:%M").time()
        except Exception:
            end_time_val = datetime.strptime("20:00", "%H:%M").time()

        db_plan = StudyPlan(
            goal_id=goal_id,
            student_id=student_id,
            title=day_task.task,
            task_description=day_task.description,
            rag_content=None,
            study_date=study_date_val,
            start_time=start_time_val,
            end_time=end_time_val,
            status=PlanStatus.TODO,
        )
        db.add(db_plan)
        db_plans.append(db_plan)

    db.flush()
    return db_plans


async def confirm_unified_draft(
    db: Session,
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    plan: UnifiedGoalPlanResponse,
) -> Dict[str, Any]:
    """
    Xác nhận lưu lộ trình học tập trực tiếp từ payload gửi lên vào MySQL.
    """
    _cancel_active_goals(db, student.id, subject_obj.id)

    db_goal = StudyGoal(
        student_id=student.id,
        subject_id=subject_obj.id,
        title=f"Lộ trình học {subject_obj.name} - Mục tiêu {target_score}/10",
        target_score=target_score,
        deadline=deadline,
        status=GoalStatus.ACTIVE,
    )
    db.add(db_goal)
    db.flush()

    db_plans = _create_study_plans(db, plan, db_goal.id, student.id)
    total_quizzes = 0

    first_plan = (
        min(db_plans, key=lambda item: (item.study_date, item.start_time))
        if db_plans
        else None
    )
    if first_plan and plan_repository.queue_generation(db, first_plan):
        stage_outbox_job(
            db,
            task_name="app.workers.tasks.task_generate_single_plan_material",
            args=[first_plan.id],
            unique_key=f"plan-generation:{first_plan.id}:{first_plan.generation_attempts}",
        )

    commit_or_rollback(db)
    db.refresh(db_goal)

    return {
        "goal": db_goal,
        "total_plans": len(db_plans),
        "total_quizzes": total_quizzes,
    }
