"""
FastAPI Router cho các API Phê duyệt Đề xuất học tập AI (Recommendation Reviews) — Giai đoạn 4.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_teacher
from app.models.user import User
from app.schemas.ai_recommendation_review import (
    AIRecommendationReviewResponse,
    AIRecommendationReviewUpdate
)
from app.services.recommendation_service import (
    get_pending_reviews,
    review_recommendation
)

router = APIRouter()


# ── GET /pending — Lấy danh sách đề xuất cần duyệt (Chỉ Giáo viên) ────────
@router.get(
    "/pending",
    response_model=List[AIRecommendationReviewResponse],
    summary="Giáo viên xem danh sách các đề xuất học tập AI đang chờ duyệt"
)
def api_get_pending_reviews(
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher)
):
    return get_pending_reviews(db=db, teacher_id=current_teacher.id)


# ── PATCH /{review_id} — Phê duyệt / Từ chối đề xuất (Chỉ Giáo viên) ─────
@router.patch(
    "/{review_id}",
    response_model=AIRecommendationReviewResponse,
    summary="Giáo viên phê duyệt (approved) hoặc từ chối (rejected) đề xuất ôn tập"
)
def api_review_recommendation(
    review_id: int,
    body: AIRecommendationReviewUpdate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher)
):
    try:
        return review_recommendation(
            db=db,
            review_id=review_id,
            teacher_id=current_teacher.id,
            status=body.status,
            teacher_feedback=body.teacher_feedback
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
