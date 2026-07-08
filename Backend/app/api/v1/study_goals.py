"""
API quản lý mục tiêu học tập (Study Goals).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, get_db
from app.models.user import User
from app.schemas.study_goal import StudyGoalResponse, StudyGoalUpdate
from app.schemas.study_plan import StudyPlanResponse
from app.services.goal_service import (
    delete_student_goal,
    get_student_goal,
    list_goal_plans,
    list_student_goals,
    update_student_goal,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[StudyGoalResponse],
    summary="Lấy danh sách mục tiêu học tập của học sinh",
)
def get_my_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    return list_student_goals(db, current_user.id)


@router.get(
    "/{goal_id}",
    response_model=StudyGoalResponse,
    summary="Xem chi tiết một mục tiêu học tập",
)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return get_student_goal(db, goal_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{goal_id}",
    response_model=StudyGoalResponse,
    summary="Cập nhật trạng thái mục tiêu học tập",
)
def update_goal(
    goal_id: int,
    body: StudyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return update_student_goal(db, goal_id, current_user.id, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/{goal_id}/plans",
    response_model=List[StudyPlanResponse],
    summary="Xem lịch học chi tiết của một mục tiêu",
)
def get_goal_plans(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return list_goal_plans(db, goal_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa mục tiêu học tập và toàn bộ lịch học, đề thi liên quan",
)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return delete_student_goal(db, goal_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa lộ trình: {str(exc)}",
        ) from exc
