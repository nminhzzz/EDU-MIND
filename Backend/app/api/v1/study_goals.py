"""
API quản lý mục tiêu học tập (Study Goals) — Giai đoạn 1.
Endpoints:
    POST /api/v1/goals/              — Tạo mục tiêu + sinh lộ trình AI
    GET  /api/v1/goals/              — Lấy danh sách goals của học sinh
    GET  /api/v1/goals/{goal_id}     — Chi tiết 1 goal
    PATCH /api/v1/goals/{goal_id}    — Cập nhật trạng thái goal
    GET  /api/v1/goals/{goal_id}/plans — Lấy danh sách study_plans của goal
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.schemas.study_goal import (
    StudyGoalCreate,
    StudyGoalUpdate,
    StudyGoalResponse,
    StudyGoalDraftCreate,
    StudyGoalConfirm
)
from app.schemas.study_plan import StudyPlanResponse
from app.services.goal_service import (
    create_goal_and_schedule_plans,
    generate_goal_plan_draft,
    confirm_goal_plan_draft
)

router = APIRouter()


# ── POST /goals/ — Tạo mục tiêu + AI sinh lộ trình ──────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mục tiêu học tập và để AI sinh lộ trình",
    description="""
Học sinh nhập môn học, điểm mong muốn, deadline và lịch rảnh.
AI (Gemini) sẽ tự động sinh lộ trình học chia theo tuần và lưu vào `study_plans`.

**Input mẫu:**
```json
{
  "subject_id": 1,
  "target_score": 8,
  "deadline": "2026-08-20",
  "available_schedule": {"mon": true, "tue": false, "wed": true, "thu": true, "fri": false, "sat": true, "sun": false}
}
```
    """
)
def create_goal(
    body: StudyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Kiểm tra môn học tồn tại
    subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={body.subject_id}."
        )

    # Gọi service: tạo goal + gọi AI sinh study_plans
    try:
        result = create_goal_and_schedule_plans(
            db=db,
            student=current_user,
            subject_obj=subject,
            target_score=body.target_score,
            deadline=body.deadline,
            available_schedule=body.available_schedule
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi AI sinh lộ trình học: {str(e)}"
        )

    goal = result["goal"]
    plans = result["plans"]

    return {
        "message": "Tạo mục tiêu và lộ trình học thành công!",
        "goal": {
            "id": goal.id,
            "title": goal.title,
            "subject_id": goal.subject_id,
            "target_score": float(goal.target_score),
            "deadline": str(goal.deadline),
            "status": goal.status,
            "created_at": str(goal.created_at)
        },
        "total_weeks": result["total_weeks"],
        "total_plans": result["total_plans"],
        "plans_preview": [
            {
                "title": p.title,
                "study_date": str(p.study_date),
                "start_time": str(p.start_time),
                "end_time": str(p.end_time),
                "status": p.status
            }
            for p in plans[:5]  # Preview 5 task đầu tiên
        ]
    }


# ── POST /goals/draft — Tạo bản nháp / Tinh chỉnh lộ trình nháp ─────
@router.post(
    "/draft",
    status_code=status.HTTP_200_OK,
    summary="Tạo bản nháp hoặc thảo luận tinh chỉnh lộ trình học tập nháp",
    description="""
Gửi yêu cầu lập lộ trình nháp (không truyền session_id) hoặc gửi tin nhắn chỉnh sửa lộ trình nháp (kèm session_id và user_message).
Kết quả trả về là session_id và chi tiết lộ trình nháp do AI đề xuất.
    """
)
async def create_or_update_goal_draft(
    body: StudyGoalDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Kiểm tra môn học tồn tại
    subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={body.subject_id}."
        )

    try:
        result = await generate_goal_plan_draft(
            student=current_user,
            subject_obj=subject,
            target_score=body.target_score,
            deadline=body.deadline,
            user_message=body.user_message,
            session_id=body.session_id,
            available_schedule=body.available_schedule,
            db=db
        )
        return {
            "message": "Sinh lộ trình nháp thành công!",
            "session_id": result["session_id"],
            "plan": result["plan"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý lộ trình nháp: {str(e)}"
        )


# ── POST /goals/confirm — Xác nhận lưu chính thức lộ trình vào MySQL ──
@router.post(
    "/confirm",
    status_code=status.HTTP_201_CREATED,
    summary="Xác nhận lưu chính thức lộ trình nháp từ MongoDB vào MySQL",
    description="""
Chốt bản lộ trình cuối cùng trong phiên chat MongoDB (session_id) để lưu chính thức vào bảng study_goals & study_plans trong MySQL.
    """
)
async def confirm_goal_draft(
    body: StudyGoalConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Kiểm tra môn học
    subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={body.subject_id}."
        )

    try:
        result = await confirm_goal_plan_draft(
            db=db,
            student=current_user,
            subject_obj=subject,
            session_id=body.session_id,
            target_score=body.target_score,
            deadline=body.deadline,
            available_schedule=body.available_schedule
        )
        
        goal = result["goal"]
        plans = result["plans"]

        return {
            "message": "Xác nhận và lưu lộ trình học tập chính thức thành công!",
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "subject_id": goal.subject_id,
                "target_score": float(goal.target_score),
                "deadline": str(goal.deadline),
                "status": goal.status,
                "created_at": str(goal.created_at)
            },
            "total_weeks": result["total_weeks"],
            "total_plans": result["total_plans"],
            "plans_preview": [
                {
                    "title": p.title,
                    "study_date": str(p.study_date),
                    "start_time": str(p.start_time),
                    "end_time": str(p.end_time),
                    "status": p.status
                }
                for p in plans[:5]  # Preview 5 task đầu
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xác nhận và lưu lộ trình học tập: {str(e)}"
        )


# ── GET /goals/ — Lấy danh sách goals của học sinh ───────────
@router.get(
    "/",
    response_model=List[StudyGoalResponse],
    summary="Lấy danh sách mục tiêu học tập của học sinh"
)
def get_my_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    goals = (
        db.query(StudyGoal)
        .filter(StudyGoal.student_id == current_user.id)
        .order_by(StudyGoal.created_at.desc())
        .all()
    )
    return goals


# ── GET /goals/{goal_id} — Chi tiết 1 goal ───────────────────
@router.get(
    "/{goal_id}",
    response_model=StudyGoalResponse,
    summary="Xem chi tiết một mục tiêu học tập"
)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mục tiêu học tập."
        )
    return goal


# ── PATCH /goals/{goal_id} — Cập nhật trạng thái goal ────────
@router.patch(
    "/{goal_id}",
    response_model=StudyGoalResponse,
    summary="Cập nhật trạng thái mục tiêu học tập"
)
def update_goal(
    goal_id: int,
    body: StudyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mục tiêu học tập."
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


# ── GET /goals/{goal_id}/plans — Lấy study_plans của goal ────
@router.get(
    "/{goal_id}/plans",
    response_model=List[StudyPlanResponse],
    summary="Xem lịch học chi tiết của một mục tiêu"
)
def get_goal_plans(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Kiểm tra goal thuộc về học sinh này
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mục tiêu học tập."
        )

    plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.goal_id == goal_id)
        .order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc())
        .all()
    )
    return plans
