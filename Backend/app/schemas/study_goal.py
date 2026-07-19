from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any


# ── Request tạo mục tiêu (từ client gửi lên) ─────────────────
class StudyGoalCreate(BaseModel):
    subject_id: int
    target_score: float = Field(
        ..., ge=0, le=10, description="Điểm mục tiêu (thang 10)"
    )
    deadline: date
    # Lịch rảnh của học sinh: {"mon": true, "tue": false, "wed": true, ...}
    available_schedule: Optional[Dict[str, Any]] = None


# ── Cập nhật trạng thái mục tiêu ────────────────────────────
class StudyGoalUpdate(BaseModel):
    title: Optional[str] = None
    target_score: Optional[float] = Field(None, ge=0, le=10)
    deadline: Optional[date] = None
    status: Optional[str] = None  # "active" | "completed" | "cancelled"


# ── Response trả về cho client ───────────────────────────────
class StudyGoalResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    title: str
    target_score: float
    deadline: date
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


from app.schemas.unified_goal import UnifiedGoalPlanResponse

# ── Request tạo bản nháp / tinh chỉnh lộ trình nháp ───────────
class StudyGoalDraftCreate(BaseModel):
    subject_id: int
    target_score: float = Field(
        ..., ge=0, le=10, description="Điểm mục tiêu (thang 10)"
    )
    deadline: date
    available_schedule: Optional[Dict[str, Any]] = None


# ── Request xác nhận và lưu chính thức lộ trình ──────────────
class StudyGoalConfirm(BaseModel):
    subject_id: int
    target_score: float = Field(..., ge=0, le=10)
    deadline: date
    available_schedule: Optional[Dict[str, Any]] = None
    plan: UnifiedGoalPlanResponse = Field(
        ..., description="Lộ trình học tập chi tiết đã chỉnh sửa thủ công"
    )

