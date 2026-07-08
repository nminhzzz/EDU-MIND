"""
Learning Analytics service — evaluates student performance and triggers
AI-generated study recommendations.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.agents.analytics.agent import evaluate_learning_performance
from app.agents.recommender.agent import generate_recommendation
from app.core.cache import get_cached, set_cached, system_analytics_key
from app.core.enums import NotificationType
from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.models.learning_analytic import LearningAnalytic
from app.models.quiz import Quiz
from app.models.subject import Subject
from app.models.user import User
from app.repositories import chat_repository
from app.repositories.ai_recommendation_review_repository import (
    ai_recommendation_review_repository,
)
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
SCORE_ADAPTIVE_PLAN_THRESHOLD = 7.0
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


async def _create_pending_recommendation(
    db: Session,
    ctx: QuizSubmissionContext,
    student_id: int,
    score: float,
    weak_topics: list,
) -> None:
    """Generate an AI recommendation and stage a pending teacher review."""
    try:
        ai_recommendation_text = await asyncio.to_thread(
            generate_recommendation,
            subject_name=ctx.subject.name,
            topic_name=ctx.quiz.title,
            score=score,
            weak_topics=weak_topics,
        )

        teacher_id: Optional[int] = (
            ctx.quiz.classroom.teacher_id
            if ctx.quiz.classroom and ctx.quiz.classroom.teacher_id
            else None
        )

        ai_recommendation_review_repository.add_pending(
            db,
            student_id=student_id,
            teacher_id=teacher_id,
            recommendation=ai_recommendation_text,
        )

        notification_repository.create(
            db,
            user_id=student_id,
            title="Đề xuất ôn tập AI đang chờ giáo viên duyệt",
            content=(
                f"Dựa trên kết quả bài '{ctx.quiz.title}' ({score}/10), "
                "AI đã tạo đề xuất ôn tập và gửi cho giáo viên phê duyệt."
            ),
            notification_type=NotificationType.PLAN,
        )
    except Exception as exc:
        logger.warning("AI Recommender Agent error: %s", exc)


async def _trigger_adaptive_plan(
    db: Session,
    ctx: QuizSubmissionContext,
    student_id: int,
    subject_id: int,
    score: float,
    weak_topics: list,
) -> None:
    """Create a chat session and notification when the student needs plan refinement."""
    try:
        active_goal = goal_repository.get_active_for_subject(
            db, student_id, subject_id
        )
        if not active_goal or not weak_topics or score >= SCORE_ADAPTIVE_PLAN_THRESHOLD:
            return

        weak_topics_str = "; ".join(
            t.get("topic", str(t)) if isinstance(t, dict) else str(t)
            for t in weak_topics
        )
        if not weak_topics_str:
            return

        logger.info(
            "Adaptive Plan: refining for student %d — weak topics: %s",
            student_id,
            weak_topics_str,
        )

        topic_session = await chat_repository.create_chat_session(
            student_id=student_id,
            title=f"Tự động điều chỉnh lộ trình - {ctx.subject.name} (Điểm yếu)",
        )

        await chat_repository.add_chat_message(
            topic_session,
            "user",
            f"Tôi vừa làm bài '{ctx.quiz.title}' được {score}/10. "
            f"Các phần yếu cần cải thiện: {weak_topics_str}. "
            "Hãy điều chỉnh lộ trình học tập của tôi để tập trung ôn các phần này.",
        )

        notification_repository.create(
            db,
            user_id=student_id,
            title="Lộ trình học được điều chỉnh tự động",
            content=(
                f"Dựa trên kết quả bài thi '{ctx.quiz.title}' ({score}/10), "
                f"AI đã phân tích điểm yếu và điều chỉnh lộ trình học tập môn {ctx.subject.name}. "
                "Vui lòng kiểm tra lại lộ trình."
            ),
            notification_type=NotificationType.PLAN,
        )
    except Exception as exc:
        logger.warning("Adaptive Plan error: %s", exc)


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
    4. If score < 7.0 and the student has an active goal, trigger adaptive plan refinement.
    5. Send notification to the student.
    """
    ctx = _load_submission_context(db, student_id, subject_id, quiz_id)
    if ctx is None:
        return

    analytic, attempts_history = _recalculate_learning_analytic(
        db, student_id, subject_id, ctx.subject.name
    )

    await _apply_ai_analytics(analytic, ctx.subject.name, attempts_history)

    if score < SCORE_RECOMMENDATION_THRESHOLD:
        await _create_pending_recommendation(
            db, ctx, student_id, score, analytic.weak_topics or []
        )

    await _trigger_adaptive_plan(
        db, ctx, student_id, subject_id, score, analytic.weak_topics or []
    )

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
