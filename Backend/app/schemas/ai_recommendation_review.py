"""
Pydantic schemas cho AI Recommendation Review (HITL) — Giai đoạn 4.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class AIRecommendationReviewResponse(BaseModel):
    id: int
    student_id: int
    teacher_id: Optional[int] = None
    recommendation: str
    teacher_feedback: Optional[str] = None
    status: str  # "pending", "approved", "rejected"
    created_at: datetime
    student: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class AIRecommendationReviewUpdate(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$", description="Trạng thái mới: approved hoặc rejected")
    teacher_feedback: Optional[str] = Field(None, description="Ý kiến phản hồi từ giáo viên")
