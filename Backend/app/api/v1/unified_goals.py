"""
Unified AI Flow endpoints (Phase 1 + 2 + 3):
    POST /api/v1/goals/unified/draft    — Generate or refine a study roadmap draft
    POST /api/v1/goals/unified/confirm  — Persist the draft to MySQL
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, get_db, rate_limiter
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.study_goal import StudyGoalConfirm, StudyGoalDraftCreate
from app.services.subject_service import get_subject
from app.services.unified_service import (
    confirm_unified_draft,
    generate_materials_and_quizzes_for_plans_bg,
    generate_unified_draft,
    validate_goal_deadline,
)

router = APIRouter()


def _get_subject_or_404(db: Session, subject_id: int):
    try:
        return get_subject(db, subject_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "/unified/draft",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limiter(limit=5, period_seconds=600, action="unified_draft"))],
    summary="Tạo bản nháp lộ trình học tập hợp nhất (Phase 1 + 2 + 3)",
    description="Nhập mục tiêu + deadline + lịch rảnh, sinh trọn gói: Lộ trình tuần, Lịch ngày, Giáo trình RAG và Quizzes.",
)
async def create_or_update_unified_draft(
    body: StudyGoalDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> dict:
    subject = _get_subject_or_404(db, body.subject_id)
    validate_goal_deadline(subject.name, body.target_score, body.deadline)

    result = await generate_unified_draft(
        student=current_user,
        subject_obj=subject,
        target_score=body.target_score,
        deadline=body.deadline,
        user_message=body.user_message,
        session_id=body.session_id,
    )
    return {
        "message": "Sinh lộ trình nháp hợp nhất thành công!",
        "session_id": result["session_id"],
        "plan": result["plan"],
    }


@router.post(
    "/unified/confirm",
    status_code=status.HTTP_201_CREATED,
    summary="Xác nhận lưu chính thức lộ trình nháp hợp nhất vào MySQL",
    description="Đọc cache Redis hoặc Mongo của session_id, ghi MySQL đồng thời (StudyGoal, StudyPlans, Quiz).",
)
async def confirm_unified(
    body: StudyGoalConfirm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> dict:
    redis = get_redis()
    lock_key = f"lock:confirm:{body.session_id}"

    if not redis.set(lock_key, "locked", nx=True, ex=10):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yêu cầu xác nhận lộ trình đang được xử lý. Vui lòng không nhấn liên tục.",
        )

    try:
        subject = _get_subject_or_404(db, body.subject_id)

        result = await confirm_unified_draft(
            db=db,
            student=current_user,
            subject_obj=subject,
            session_id=body.session_id,
            target_score=body.target_score,
            deadline=body.deadline,
        )

        goal = result["goal"]
        background_tasks.add_task(
            generate_materials_and_quizzes_for_plans_bg,
            goal.id,
            current_user.id,
            subject.id,
        )

        # Xóa cache dashboard của học sinh
        try:
            redis.delete(f"dashboard_snapshot:{current_user.id}")
        except Exception:
            pass

        return {
            "message": "Xác nhận và lưu lộ trình hợp nhất chính thức thành công!",
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "subject_id": goal.subject_id,
                "target_score": float(goal.target_score),
                "deadline": str(goal.deadline),
                "status": goal.status,
                "created_at": str(goal.created_at),
            },
            "total_plans": result["total_plans"],
            "total_quizzes": result["total_quizzes"],
        }
    finally:
        try:
            redis.delete(lock_key)
        except Exception:
            pass
