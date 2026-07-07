from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


# ── Response từng study plan trả về cho client ───────────────
class StudyPlanResponse(BaseModel):
    id: int
    student_id: int
    goal_id: int
    subject_id: Optional[int] = None
    title: str
    task_description: Optional[str] = None
    rag_content: Optional[str] = None
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
