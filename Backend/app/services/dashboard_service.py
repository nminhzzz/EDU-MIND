"""
Student dashboard snapshot — aggregates goals, plans, quizzes, and weak areas.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.enums import PlanStatus
from app.models.study_plan import StudyPlan
from app.repositories.analytic_repository import analytic_repository
from app.repositories.attempt_repository import attempt_repository
from app.repositories.goal_repository import goal_repository
from app.repositories.notification_repository import notification_repository
from app.repositories.plan_repository import plan_repository


def _summarize_weak_areas(analytics) -> List[str]:
    weak_summary: List[str] = []
    for analytic in analytics:
        if not analytic.weak_topics:
            continue
        weak_summary.extend(
            topic.get("topic", str(topic)) if isinstance(topic, dict) else str(topic)
            for topic in analytic.weak_topics[:2]
        )
    return weak_summary[:3]


def _format_next_task(plan: StudyPlan) -> Dict[str, str]:
    return {
        "title": plan.title,
        "date": plan.study_date.isoformat(),
        "time": (
            f"{plan.start_time.strftime('%H:%M')} - "
            f"{plan.end_time.strftime('%H:%M')}"
        ),
    }


def build_dashboard_payload(db: Session, student_id: int) -> Dict[str, Any]:
    """Build the realtime dashboard JSON snapshot for a student."""
    today = date.today()

    active_goals = goal_repository.count_active_for_student(db, student_id)
    today_plans = plan_repository.list_today_for_active_goals(db, student_id, today)
    today_total = len(today_plans)
    today_done = sum(1 for plan in today_plans if plan.status == PlanStatus.DONE)
    today_doing = sum(1 for plan in today_plans if plan.status == PlanStatus.DOING)

    total_plans_all = plan_repository.count_for_active_goals(db, student_id)
    done_plans_all = plan_repository.count_done_for_active_goals(db, student_id)
    progress_pct = (
        round(done_plans_all / total_plans_all * 100) if total_plans_all else 0
    )

    avg_score = attempt_repository.avg_score_for_student(db, student_id) or 0.0
    next_plan = plan_repository.get_next_todo_for_active_goals(db, student_id, today)
    weak_areas = _summarize_weak_areas(
        analytic_repository.list_by_student(db, student_id)
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_goals": active_goals,
        "today": {
            "total_tasks": today_total,
            "done": today_done,
            "doing": today_doing,
            "remaining": today_total - today_done - today_doing,
        },
        "overall": {
            "progress_pct": progress_pct,
            "done_plans": done_plans_all,
            "total_plans": total_plans_all,
        },
        "quizzes": {
            "total_attempts": attempt_repository.count_for_student(db, student_id),
            "avg_score": round(float(avg_score), 1),
        },
        "next_task": _format_next_task(next_plan) if next_plan else None,
        "weak_areas": weak_areas,
        "unread_notifications": notification_repository.count_unread_for_user(
            db, student_id
        ),
    }
