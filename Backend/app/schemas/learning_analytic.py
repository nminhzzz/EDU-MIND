"""
Pydantic schemas for the LearningAnalytic model.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TopicPerformance(BaseModel):
    """Represents a weak or strong topic identified by the AI analytics agent."""
    topic: str
    average_score: Optional[float] = None
    note: Optional[str] = None


from app.schemas.subject import SubjectResponse


class LearningAnalyticResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    subject: Optional[SubjectResponse] = None
    average_score: float
    quizzes_completed: int
    weak_topics: List[Dict[str, Any]] = []
    strong_topics: List[Dict[str, Any]] = []
    ai_feedback: Optional[str] = None

    class Config:
        from_attributes = True
