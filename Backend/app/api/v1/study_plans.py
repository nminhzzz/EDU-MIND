"""
API quản lý kế hoạch học tập chi tiết hàng ngày (Study Plans).
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, get_db
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.study_plan import StudyPlanResponse, StudyPlanUpdate
from app.services.plan_service import (
    get_student_plan,
    list_student_plans,
    update_student_plan,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[StudyPlanResponse],
    summary="Lấy danh sách các task học tập hàng ngày của học sinh",
)
def get_my_plans(
    goal_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    return list_student_plans(
        db,
        current_user.id,
        goal_id=goal_id,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/{plan_id}",
    response_model=StudyPlanResponse,
    summary="Xem chi tiết một task học tập hàng ngày",
)
def get_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return get_student_plan(db, plan_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{plan_id}",
    response_model=StudyPlanResponse,
    summary="Cập nhật trạng thái hoặc thông tin một task học tập",
)
def update_plan(
    plan_id: int,
    body: StudyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        res = update_student_plan(db, plan_id, current_user.id, body)
        # Xóa cache dashboard của học sinh để cập nhật tiến trình hoàn thành task
        try:
            get_redis().delete(f"dashboard_snapshot:{current_user.id}")
        except Exception:
            pass
        return res
    except ValueError as exc:
        detail = str(exc)
        if "tự tích hoàn thành" in detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=detail
            ) from exc
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
