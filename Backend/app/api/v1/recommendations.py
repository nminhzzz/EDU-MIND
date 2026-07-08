"""
FastAPI Router cho các API Phê duyệt Đề xuất học tập AI (Recommendation Reviews) — Giai đoạn 4.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_teacher, get_current_student
from app.models.user import User
from app.schemas.ai_recommendation_review import (
    AIRecommendationReviewResponse,
    AIRecommendationReviewUpdate,
)
from app.services.recommendation_service import (
    get_pending_reviews,
    review_recommendation,
    get_student_recommendations,
)

router = APIRouter()


# ── GET /pending — Lấy danh sách đề xuất cần duyệt (Chỉ Giáo viên) ────────
@router.get(
    "/pending",
    response_model=List[AIRecommendationReviewResponse],
    summary="Giáo viên xem danh sách các đề xuất học tập AI đang chờ duyệt",
)
def api_get_pending_reviews(
    db: Session = Depends(get_db), current_teacher: User = Depends(get_current_teacher)
):
    return get_pending_reviews(db=db, teacher_id=current_teacher.id)


# ── GET /my-recommendations — Lấy danh sách đề xuất đã duyệt (Chỉ Học sinh) ─
@router.get(
    "/my-recommendations",
    response_model=List[AIRecommendationReviewResponse],
    summary="Học sinh xem danh sách các đề xuất học tập AI đã được phê duyệt",
)
async def api_get_student_recommendations(
    db: Session = Depends(get_db), current_student: User = Depends(get_current_student)
):
    return await get_student_recommendations(db=db, student_id=current_student.id)


# ── PATCH /{review_id} — Phê duyệt / Từ chối đề xuất (Chỉ Giáo viên) ─────
@router.patch(
    "/{review_id}",
    response_model=AIRecommendationReviewResponse,
    summary="Giáo viên phê duyệt (approved) hoặc từ chối (rejected) đề xuất ôn tập",
)
def api_review_recommendation(
    review_id: int,
    body: AIRecommendationReviewUpdate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    return review_recommendation(
        db=db,
        review_id=review_id,
        teacher_id=current_teacher.id,
        status=body.status,
        teacher_feedback=body.teacher_feedback,
    )
