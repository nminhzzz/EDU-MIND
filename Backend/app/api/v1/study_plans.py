"""
API quản lý kế hoạch học tập chi tiết hàng ngày (Study Plans) — Giai đoạn 2.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.study_plan_progress import StudyPlanProgress
from app.schemas.study_plan import StudyPlanResponse, StudyPlanUpdate
from app.services.plan_service import generate_and_save_daily_plans

router = APIRouter()


# ── POST /plans/generate/{goal_id} — Kích hoạt Daily Planner Agent ────────
@router.post(
    "/generate/{goal_id}",
    summary="Kích hoạt Daily Planner Agent để lập lịch học chi tiết hàng ngày",
    description="""
    Nhận mục tiêu học tập theo tuần, sử dụng AI sinh lịch chi tiết từng ngày dựa trên tuỳ chọn rảnh và số giờ học.
    Có thể truyền các tham số tùy biến trong request body, nếu trống sẽ lấy từ cài đặt StudentPreference của học sinh.
    """
)
def generate_daily_schedule(
    goal_id: int,
    study_hours_per_day: Optional[float] = None,
    preferred_time: Optional[str] = None,
    off_days: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Kiểm tra mục tiêu học tập tồn tại và thuộc về học sinh hiện tại
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mục tiêu học tập với ID={goal_id}."
        )

    try:
        plans = generate_and_save_daily_plans(
            db=db,
            goal_id=goal_id,
            study_hours_per_day=study_hours_per_day,
            preferred_time=preferred_time,
            off_days=off_days
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi AI lập lịch học hàng ngày: {str(e)}"
        )

    return {
        "message": "AI lập lịch học chi tiết hàng ngày thành công!",
        "goal_id": goal_id,
        "total_tasks": len(plans),
        "plans": [
            {
                "id": p.id,
                "title": p.title,
                "task_description": p.task_description,
                "study_date": str(p.study_date),
                "start_time": str(p.start_time),
                "end_time": str(p.end_time),
                "status": p.status
            }
            for p in plans
        ]
    }


# ── GET /plans/ — Lấy danh sách plans của học sinh ───────────
@router.get(
    "/",
    response_model=List[StudyPlanResponse],
    summary="Lấy danh sách các task học tập hàng ngày của học sinh"
)
def get_my_plans(
    goal_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    query = db.query(StudyPlan).filter(StudyPlan.student_id == current_user.id)

    if goal_id:
        query = query.filter(StudyPlan.goal_id == goal_id)
    if status_filter:
        query = query.filter(StudyPlan.status == status_filter)
    if start_date:
        query = query.filter(StudyPlan.study_date >= start_date)
    if end_date:
        query = query.filter(StudyPlan.study_date <= end_date)

    plans = query.order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc()).all()
    return plans


# ── GET /plans/{plan_id} — Chi tiết 1 plan ────────────────────
@router.get(
    "/{plan_id}",
    response_model=StudyPlanResponse,
    summary="Xem chi tiết một task học tập hàng ngày"
)
def get_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.student_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lịch học này."
        )
    return plan


# ── PATCH /plans/{plan_id} — Cập nhật trạng thái task ──────────
@router.patch(
    "/{plan_id}",
    response_model=StudyPlanResponse,
    summary="Cập nhật trạng thái hoặc thông tin một task học tập"
)
def update_plan(
    plan_id: int,
    body: StudyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.student_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lịch học này."
        )

    update_data = body.model_dump(exclude_unset=True)

    # Cập nhật các trường
    for field, value in update_data.items():
        setattr(plan, field, value)

    # Nếu cập nhật status, kiểm tra và cập nhật tiến độ học tập (StudyPlanProgress)
    if "status" in update_data:
        status_val = update_data["status"]
        # Lấy hoặc tạo bản ghi tiến độ cho plan này
        progress = db.query(StudyPlanProgress).filter(StudyPlanProgress.study_plan_id == plan.id).first()
        
        # Phần trăm hoàn thành tương ứng
        percent = 0.0
        if status_val == "doing":
            percent = 50.0
        elif status_val == "done":
            percent = 100.0

        if not progress:
            progress = StudyPlanProgress(
                study_plan_id=plan.id,
                student_id=current_user.id,
                completion_percent=percent,
                completed_at=datetime.utcnow() if status_val == "done" else None
            )
            db.add(progress)
        else:
            progress.completion_percent = percent
            if status_val == "done":
                progress.completed_at = datetime.utcnow()
            else:
                progress.completed_at = None

    db.commit()
    db.refresh(plan)
    return plan
