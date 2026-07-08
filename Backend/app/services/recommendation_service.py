"""
Service xử lý các nghiệp vụ liên quan đến Phê duyệt Đề xuất học tập AI (HITL).
"""

import asyncio
from datetime import date, time, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.cache import invalidate, student_recommendations_key
from app.core.enums import NotificationType, RecommendationStatus
from app.database.unit_of_work import commit_or_rollback
from app.models.ai_recommendation_review import AIRecommendationReview
from app.repositories.ai_recommendation_review_repository import (
    ai_recommendation_review_repository,
)
from app.repositories.classroom_student_repository import classroom_student_repository
from app.repositories.goal_repository import goal_repository
from app.repositories.notification_repository import notification_repository
from app.repositories.plan_repository import plan_repository
from app.repositories.user_repository import user_repository


def get_pending_reviews(db: Session, teacher_id: int) -> List[AIRecommendationReview]:
    """Lấy danh sách các đề xuất ôn tập đang chờ duyệt của học sinh thuộc lớp giáo viên này dạy."""
    return ai_recommendation_review_repository.get_pending_by_teacher(db, teacher_id)


def _schedule_review_email(
    *,
    student_email: str,
    student_name: str,
    status: str,
    recommendation: str,
    teacher_feedback: Optional[str],
) -> None:
    from app.infrastructure.email import (  # noqa: PLC0415
        send_recommendation_approved_email,
        send_recommendation_rejected_email,
    )

    try:
        loop = asyncio.get_event_loop()
        if status == RecommendationStatus.APPROVED:
            loop.create_task(
                send_recommendation_approved_email(
                    student_email, student_name, recommendation
                )
            )
        else:
            loop.create_task(
                send_recommendation_rejected_email(
                    student_email,
                    student_name,
                    teacher_feedback or "Giáo viên đã điều chỉnh đề xuất.",
                )
            )
    except RuntimeError:
        pass


def review_recommendation(
    db: Session,
    review_id: int,
    teacher_id: int,
    status: str,
    teacher_feedback: Optional[str] = None,
) -> AIRecommendationReview:
    """Giáo viên phê duyệt hoặc từ chối đề xuất ôn tập từ AI."""
    review = ai_recommendation_review_repository.get(db, review_id)
    if not review:
        raise ValueError(f"Không tìm thấy đề xuất học tập với ID={review_id}.")

    if not classroom_student_repository.teacher_teaches_student(
        db, teacher_id, review.student_id
    ):
        raise PermissionError("Bạn không có quyền phê duyệt đề xuất cho học sinh này.")

    review.status = status
    review.teacher_feedback = teacher_feedback
    review.teacher_id = teacher_id

    if status == RecommendationStatus.APPROVED:
        goal = goal_repository.get_latest_for_student(db, review.student_id)
        if goal:
            title_text = (
                f"[Ôn tập AI] {review.recommendation[:50]}..."
                if len(review.recommendation) > 50
                else f"[Ôn tập AI] {review.recommendation}"
            )
            plan_repository.stage_review_plan(
                db,
                student_id=review.student_id,
                goal_id=goal.id,
                title=title_text,
                task_description=review.recommendation,
                study_date=date.today() + timedelta(days=1),
                start_time=time(19, 0, 0),
                end_time=time(20, 0, 0),
            )

        notification_repository.create(
            db,
            user_id=review.student_id,
            title="Đề xuất học tập mới được phê duyệt",
            content=(
                f"Thầy cô đã phê duyệt một đề xuất ôn tập từ AI cho bạn: "
                f"{review.recommendation[:120]}..."
            ),
            notification_type=NotificationType.PLAN,
        )

    commit_or_rollback(db)
    db.refresh(review)

    try:
        loop = asyncio.get_event_loop()
        loop.create_task(invalidate(student_recommendations_key(review.student_id)))
    except RuntimeError:
        pass

    student = user_repository.get(db, review.student_id)
    if student:
        _schedule_review_email(
            student_email=student.email,
            student_name=student.full_name or student.email,
            status=status,
            recommendation=review.recommendation,
            teacher_feedback=teacher_feedback,
        )

    return review


async def get_student_recommendations(
    db: Session, student_id: int
) -> List[dict]:
    """Lấy danh sách các đề xuất học tập AI đã được duyệt dành cho học sinh.

    Cached per-student for 10 minutes; invalidated on teacher approve/reject.
    """
    from app.core.cache import get_cached, set_cached  # noqa: PLC0415
    from app.schemas.ai_recommendation_review import AIRecommendationReviewResponse

    cache_key = student_recommendations_key(student_id)
    cached = await get_cached(cache_key)
    if cached is not None:
        return cached

    rows = ai_recommendation_review_repository.get_approved_by_student(db, student_id)
    serialised = [
        AIRecommendationReviewResponse.model_validate(r).model_dump(mode="json")
        for r in rows
    ]
    await set_cached(cache_key, serialised, ttl_seconds=600)
    return serialised
