from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


# ── Tạo mới study plan (dùng bởi plan_repository & services) ─
class StudyPlanCreate(BaseModel):
    student_id: int
    goal_id: int
    title: str
    task_description: Optional[str] = None
    rag_content: Optional[str] = None
    lesson_summary: Optional[str] = None
    generation_status: str = "not_started"
    lesson_status: str = "not_started"
    quiz_status: str = "not_started"
    generation_error: Optional[str] = None
    generation_attempts: int = 0
    generation_started_at: Optional[datetime] = None
    generation_finished_at: Optional[datetime] = None
    study_date: date
    start_time: time
    end_time: time
    ai_generated: bool = False
    status: str = "todo"


# ── Response từng study plan trả về cho client ───────────────
class StudyPlanResponse(BaseModel):
    id: int
    student_id: int
    goal_id: int
    subject_id: Optional[int] = None
    title: str
    task_description: Optional[str] = None
    rag_content: Optional[str] = None
    lesson_summary: Optional[str] = None
    generation_status: str
    lesson_status: str
    quiz_status: str
    generation_error: Optional[str] = None
    generation_attempts: int
    generation_started_at: Optional[datetime] = None
    generation_finished_at: Optional[datetime] = None
    study_date: date
    start_time: time
    end_time: time
    ai_generated: bool
    status: str  # "todo" | "doing" | "done"
    created_at: datetime

    class Config:
        from_attributes = True


# ── Cập nhật trạng thái task ─────────────────────────────────
class StudyPlanUpdate(BaseModel):
    status: Optional[str] = None  # "todo" | "doing" | "done"
    title: Optional[str] = None
    task_description: Optional[str] = None
    rag_content: Optional[str] = None
    study_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
