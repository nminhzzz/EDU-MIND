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
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.schemas.study_goal import StudyGoalUpdate, StudyGoalResponse
from app.schemas.study_plan import StudyPlanResponse

router = APIRouter()


# ── GET /goals/ — Lấy danh sách goals của học sinh ───────────
@router.get(
    "/",
    response_model=List[StudyGoalResponse],
    summary="Lấy danh sách mục tiêu học tập của học sinh",
)
def get_my_goals(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_student)
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
    summary="Xem chi tiết một mục tiêu học tập",
)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mục tiêu học tập.",
        )
    return goal


# ── PATCH /goals/{goal_id} — Cập nhật trạng thái goal ────────
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
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mục tiêu học tập.",
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
    summary="Xem lịch học chi tiết của một mục tiêu",
)
def get_goal_plans(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
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
            detail="Không tìm thấy mục tiêu học tập.",
        )

    plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.goal_id == goal_id)
        .order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc())
        .all()
    )
    return plans


# ── DELETE /goals/{goal_id} — Xóa lộ trình và toàn bộ dữ liệu liên quan ──
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
    goal = (
        db.query(StudyGoal)
        .filter(StudyGoal.id == goal_id, StudyGoal.student_id == current_user.id)
        .first()
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lộ trình học tập để xóa.",
        )

    try:
        from app.models.quiz import Quiz
        from app.models.quiz_attempt import QuizAttempt

        # 1. Tìm các study_plan_ids liên kết với goal này
        plan_ids = [p.id for p in goal.study_plans]
        if plan_ids:
            # Tìm tất cả quizzes liên kết với các plans này
            quizzes = db.query(Quiz).filter(Quiz.study_plan_id.in_(plan_ids)).all()
            quiz_ids = [q.id for q in quizzes]
            if quiz_ids:
                # Xóa các quiz attempts trước để tránh lỗi khóa ngoại
                db.query(QuizAttempt).filter(QuizAttempt.quiz_id.in_(quiz_ids)).delete(
                    synchronize_session=False
                )
                # Xóa các quizzes
                db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).delete(
                    synchronize_session=False
                )

        # 2. Xóa study_goal (SQLAlchemy cascade sẽ tự động xóa study_plans)
        db.delete(goal)
        db.commit()
        return {
            "message": "Đã xóa lộ trình học tập và toàn bộ dữ liệu liên quan thành công!"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa lộ trình: {str(e)}",
        )
