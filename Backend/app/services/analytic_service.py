"""
Learning Analytics service — evaluates student performance and triggers
AI-generated study recommendations.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.agents.analytics.agent import evaluate_learning_performance
from app.core.cache import get_cached, set_cached, system_analytics_key
from app.core.enums import NotificationType
from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.models.learning_analytic import LearningAnalytic
from app.models.quiz import Quiz
from app.models.subject import Subject
from app.models.user import User
from app.repositories.analytic_repository import analytic_repository
from app.repositories.attempt_repository import attempt_repository
from app.repositories.classroom_repository import classroom_repository
from app.repositories.goal_repository import goal_repository
from app.repositories.notification_repository import notification_repository
from app.repositories.plan_repository import plan_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.subject_repository import subject_repository
from app.repositories.user_repository import user_repository

logger = get_logger(__name__)

# Business thresholds — kept as module constants for clarity and testability.
SCORE_RECOMMENDATION_THRESHOLD = 8.0
PASS_SCORE_THRESHOLD = 5.0


@dataclass(frozen=True)
class QuizSubmissionContext:
    """Entities loaded for a post-quiz analytics workflow."""

    subject: Subject
    student: User
    quiz: Quiz


def _load_submission_context(
    db: Session,
    student_id: int,
    subject_id: int,
    quiz_id: int,
) -> Optional[QuizSubmissionContext]:
    subject = subject_repository.get(db, subject_id)
    student = user_repository.get(db, student_id)
    quiz = quiz_repository.get_with_classroom(db, quiz_id)

    if not subject or not student or not quiz:
        return None

    return QuizSubmissionContext(subject=subject, student=student, quiz=quiz)


def _recalculate_learning_analytic(
    db: Session,
    student_id: int,
    subject_id: int,
    subject_name: str,
) -> tuple[LearningAnalytic, List[Dict[str, Any]]]:
    """Upsert analytic record and rebuild attempt history for the AI agent."""
    analytic = analytic_repository.ensure_for_student_subject(
        db, student_id, subject_id
    )

    attempts = attempt_repository.get_by_student_and_subject(
        db, student_id, subject_id
    )
    quizzes_completed = len(attempts)
    average_score = (
        sum(float(a.score) for a in attempts) / quizzes_completed
        if quizzes_completed > 0
        else 0.0
    )
    analytic.quizzes_completed = quizzes_completed
    analytic.average_score = average_score

    quiz_title_map = quiz_repository.get_title_map(
        db, {a.quiz_id for a in attempts}
    )

    attempts_history = [
        {
            "topic": quiz_title_map.get(
                a.quiz_id, f"Bài kiểm tra {subject_name}"
            ),
            "score": float(a.score),
            "is_passed": float(a.score) >= PASS_SCORE_THRESHOLD,
        }
        for a in attempts
    ]
    return analytic, attempts_history


async def _apply_ai_analytics(
    analytic: LearningAnalytic,
    subject_name: str,
    attempts_history: List[Dict[str, Any]],
) -> None:
    """Call the Analytics Agent and write weak/strong topics onto the record."""
    try:
        ai_evaluation = await asyncio.to_thread(
            evaluate_learning_performance,
            subject_name=subject_name,
            attempts_history=attempts_history,
        )
        analytic.weak_topics = [t.model_dump() for t in ai_evaluation.weak_topics]
        analytic.strong_topics = [t.model_dump() for t in ai_evaluation.strong_topics]
        analytic.ai_feedback = ai_evaluation.ai_feedback
    except Exception as exc:
        logger.warning("AI Analytics Agent error: %s", exc)


# _create_pending_recommendation removed to disable AI recommendations


def _add_progress_notification(
    db: Session,
    ctx: QuizSubmissionContext,
    student_id: int,
    score: float,
) -> None:
    """Notify the student that their learning profile was updated."""
    notification_repository.create(
        db,
        user_id=student_id,
        title="Hồ sơ học tập được cập nhật",
        content=(
            f"Kết quả bài thi '{ctx.quiz.title}' đạt {score}/10 đã được lưu "
            f"và đánh giá vào profile học sinh môn {ctx.subject.name}."
        ),
        notification_type=NotificationType.SCORE,
    )


async def update_student_analytics_and_recommend(
    db: Session,
    student_id: int,
    subject_id: int,
    quiz_id: int,
    score: float,
) -> None:
    """
    Background task triggered after a quiz submission:
    1. Recalculate LearningAnalytic (avg score, completed quizzes).
    2. Call AI Analytics Agent to identify weak/strong topics.
    3. If score < 8.0, generate an AI study recommendation and schedule a review plan.
    4. Send notification to the student.
    """
    ctx = _load_submission_context(db, student_id, subject_id, quiz_id)
    if ctx is None:
        return

    analytic, attempts_history = _recalculate_learning_analytic(
        db, student_id, subject_id, ctx.subject.name
    )

    await _apply_ai_analytics(analytic, ctx.subject.name, attempts_history)

    _add_progress_notification(db, ctx, student_id, score)

    commit_or_rollback(db)


async def get_system_analytics(db: Session) -> dict:
    """Return platform-wide operational statistics for the Admin dashboard.

    Result is cached in Redis for 5 minutes to avoid repeated full-table scans.
    """
    cache_key = system_analytics_key()
    cached = await get_cached(cache_key)
    if cached is not None:
        return cached

    role_counts = user_repository.count_by_role(db)

    result = {
        "total_students": role_counts.get("student", 0),
        "total_teachers": role_counts.get("teacher", 0),
        "total_admins": role_counts.get("admin", 0),
        "total_classrooms": classroom_repository.count_all(db),
        "total_active_goals": goal_repository.count_active(db),
        "total_study_plans": plan_repository.count_all(db),
        "total_quizzes": quiz_repository.count_all(db),
    }
    await set_cached(cache_key, result, ttl_seconds=300)
    return result
