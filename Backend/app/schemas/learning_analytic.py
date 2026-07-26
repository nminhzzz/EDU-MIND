"""
Pydantic schemas for Learning Analytics and Teacher Evaluation Overrides.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TopicScoreItem(BaseModel):
    topic: str
    score: float


class LearningAnalyticResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    average_score: float
    quizzes_completed: int
    weak_topics: List[Dict[str, Any]] = []
    strong_topics: List[Dict[str, Any]] = []
    ai_feedback: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LearningAnalyticUpdate(BaseModel):
    ai_feedback: Optional[str] = Field(None, description="Lời nhận xét đánh giá")
    weak_topics: Optional[List[Dict[str, Any]]] = Field(None, description="Danh sách chủ đề yếu")
    strong_topics: Optional[List[Dict[str, Any]]] = Field(None, description="Danh sách chủ đề mạnh")
