from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from typing import List

from app.database.mysql import get_db
from app.models.user import User
from app.models.subject import Subject
from app.services.goal_service import create_goal_and_schedule_plans
from app.services.plan_service import generate_and_save_daily_plans

router = APIRouter()

# Schema yêu cầu từ Frontend cho Goal Planner
class GoalPlannerRequest(BaseModel):
    subject: str
    target_score: float
    deadline: date
    current_level: str

# Schema phản hồi về Frontend cho Goal Planner
class TaskResponse(BaseModel):
    title: str
    study_date: date

class GoalPlannerResponseSchema(BaseModel):
    goal_id: int
    title: str
    target_score: float
    deadline: date
    total_weeks: int
    tasks_created: List[TaskResponse]

# Schema yêu cầu từ Frontend cho Daily Planner
class DailyPlannerRequest(BaseModel):
    goal_id: int
    study_hours_per_day: float
    preferred_time: str
    off_days: List[str]

# Schema phản hồi về Frontend cho Daily Planner
class DailyTaskResponse(BaseModel):
    date: date
    start_time: str
    end_time: str
    task: str

class DailyPlannerResponseSchema(BaseModel):
    goal_id: int
    study_hours_per_day: float
    preferred_time: str
    off_days: List[str]
    schedule_created: List[DailyTaskResponse]

@router.post("/generate-goal-plan", response_model=GoalPlannerResponseSchema)
def generate_and_save_goal_plan(
    request: GoalPlannerRequest,
    db: Session = Depends(get_db)
):
    # 1. Tìm hoặc tạo học sinh mặc định để tránh lỗi khóa ngoại MySQL
    student = db.query(User).filter(User.role == "student").first()
    if not student:
        student = User(
            email="student_default@test.com",
            password_hash="hashedpassword123",
            full_name="Học sinh mặc định",
            role="student",
            grade="Lớp 12",
            learning_level="average",
            is_active=True
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    # 2. Tìm hoặc tạo môn học
    subject_clean = request.subject.strip()
    subject_obj = db.query(Subject).filter(Subject.name == subject_clean).first()
    if not subject_obj:
        import unicodedata
        subject_code = "".join(
            c for c in unicodedata.normalize("NFD", subject_clean.upper())
            if unicodedata.category(c) != "Mn"
        ).replace(" ", "")
        
        subject_obj = Subject(
            name=subject_clean,
            code=subject_code or "SUB_DEFAULT",
            description=f"Môn học {subject_clean}"
        )
        db.add(subject_obj)
        db.commit()
        db.refresh(subject_obj)

    # 3. Gọi Service nghiệp vụ để điều phối sinh lộ trình qua AI và lưu DB
    try:
        result = create_goal_and_schedule_plans(
            db=db,
            student=student,
            subject_obj=subject_obj,
            target_score=request.target_score,
            deadline=request.deadline,
            current_level=request.current_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thực hiện lập lộ trình: {str(e)}")

    db_goal = result["goal"]
    created_tasks = result["plans"]
    total_weeks = result["total_weeks"]

    return GoalPlannerResponseSchema(
        goal_id=db_goal.id,
        title=db_goal.title,
        target_score=float(db_goal.target_score),
        deadline=db_goal.deadline,
        total_weeks=total_weeks,
        tasks_created=[
            TaskResponse(title=t.title, study_date=t.study_date)
            for t in created_tasks
        ]
    )

@router.post("/generate-daily-plan", response_model=DailyPlannerResponseSchema)
def generate_and_save_daily_plan_endpoint(
    request: DailyPlannerRequest,
    db: Session = Depends(get_db)
):
    try:
        created_plans = generate_and_save_daily_plans(
            db=db,
            goal_id=request.goal_id,
            study_hours_per_day=request.study_hours_per_day,
            preferred_time=request.preferred_time,
            off_days=request.off_days
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi sắp xếp lịch học ngày: {str(e)}")
        
    return DailyPlannerResponseSchema(
        goal_id=request.goal_id,
        study_hours_per_day=request.study_hours_per_day,
        preferred_time=request.preferred_time,
        off_days=request.off_days,
        schedule_created=[
            DailyTaskResponse(
                date=p.study_date,
                start_time=p.start_time.strftime("%H:%M"),
                end_time=p.end_time.strftime("%H:%M"),
                task=p.title
            )
            for p in created_plans
        ]
    )
