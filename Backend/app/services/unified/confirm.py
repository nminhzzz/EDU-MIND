"""
Unified goal confirmation — persist draft from Redis/MongoDB into MySQL.
"""

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.enums import GoalStatus, PlanStatus
from app.core.logging import get_logger
from app.database.redis import get_redis
from app.database.unit_of_work import commit_or_rollback
from app.models.quiz import Quiz
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.subject import Subject
from app.models.user import User
from app.repositories import chat_repository
from app.repositories.goal_repository import goal_repository
from app.schemas.unified_goal import UnifiedGoalPlanResponse

logger = get_logger(__name__)

_QUIZ_TITLE_NOISE = [
    "quiz",
    "bài kiểm tra",
    "tuần",
    "luyện tập",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    ":",
    "-",
    "_",
]


async def _resolve_plan_from_draft(
    session_id: str,
) -> UnifiedGoalPlanResponse:
    """Load a draft plan from Redis, falling back to MongoDB chat history."""
    redis_client = get_redis()
    redis_key = f"unified_draft:{session_id}"
    cached_data = redis_client.get(redis_key)

    if cached_data:
        logger.debug("Redis cache HIT for key %s", redis_key)
        try:
            return UnifiedGoalPlanResponse(**json.loads(cached_data))
        except Exception as exc:
            logger.warning("Failed to parse Redis cache data: %s", exc)

    logger.debug("Redis cache MISS for key %s — falling back to MongoDB", redis_key)
    last_msg = await chat_repository.get_last_assistant_message(session_id)
    if not last_msg:
        raise ValueError(
            "Không tìm thấy lộ trình nháp cũ trong cache hay MongoDB. Vui lòng tạo mới."
        )
    try:
        return UnifiedGoalPlanResponse(**json.loads(last_msg))
    except Exception as exc:
        raise ValueError(f"Dữ liệu lộ trình nháp bị lỗi cấu trúc: {exc}") from exc


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


def _match_quiz_to_plan(quiz_title: str, db_plans: List[StudyPlan]) -> Optional[int]:
    clean_quiz_title = quiz_title.lower()
    for token in _QUIZ_TITLE_NOISE:
        clean_quiz_title = clean_quiz_title.replace(token, "")
    clean_quiz_title = clean_quiz_title.strip()

    for plan in db_plans:
        if len(clean_quiz_title) >= 3 and (
            clean_quiz_title in plan.title.lower()
            or plan.title.lower() in clean_quiz_title
        ):
            return plan.id

    return db_plans[-1].id if db_plans else None


def _persist_plan_quizzes(
    db: Session,
    plan: UnifiedGoalPlanResponse,
    db_plans: List[StudyPlan],
    student_id: int,
    subject_id: int,
) -> int:
    total_quizzes = 0

    for quiz_item in plan.quizzes:
        questions_json = []
        for q in quiz_item.questions:
            options_data = (
                [{"key": opt.key, "value": opt.value} for opt in q.options]
                if q.options
                else []
            )
            questions_json.append(
                {
                    "question_text": q.question_text,
                    "options": options_data,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
            )

        matched_plan_id = _match_quiz_to_plan(quiz_item.title, db_plans)

        db_quiz = Quiz(
            student_id=student_id,
            subject_id=subject_id,
            study_plan_id=matched_plan_id,
            title=quiz_item.title,
            difficulty="medium",
            total_questions=len(questions_json),
            questions=questions_json,
            generated_by_ai=True,
        )
        db.add(db_quiz)
        total_quizzes += 1

    return total_quizzes


async def confirm_unified_draft(
    db: Session,
    student: User,
    subject_obj: Subject,
    session_id: str,
    target_score: float,
    deadline: date,
) -> Dict[str, Any]:
    """
    Xác nhận lưu lộ trình nháp trọn gói từ Redis (hoặc Fallback Mongo) vào MySQL.
    """
    plan = await _resolve_plan_from_draft(session_id)

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
    total_quizzes = _persist_plan_quizzes(
        db, plan, db_plans, student.id, subject_obj.id
    )

    commit_or_rollback(db)
    db.refresh(db_goal)

    redis_key = f"unified_draft:{session_id}"
    try:
        get_redis().delete(redis_key)
        logger.debug("Deleted Redis cache key %s after confirmation", redis_key)
    except Exception as exc:
        logger.warning("Failed to delete Redis cache key %s: %s", redis_key, exc)

    return {
        "goal": db_goal,
        "total_plans": len(db_plans),
        "total_quizzes": total_quizzes,
    }
