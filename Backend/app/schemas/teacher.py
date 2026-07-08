"""
Teacher-specific request/response schemas.
StudyDocumentCreate lives in schemas/study_document.py — import from there.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TeacherClassroomStudentResponse(BaseModel):
    student_id: int
    email: str
    full_name: Optional[str] = None
    total_goals: int = 0
    completed_goals: int = 0
    total_attempts: int = 0
    average_score: Optional[float] = None


class TeacherQuizCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề bài kiểm tra/bài tập")
    difficulty: str = Field("medium", description="Độ khó: easy, medium, hard")
    subject_id: int = Field(..., description="ID môn học")
    classroom_id: int = Field(..., description="ID lớp học gán bài tập")
    questions: List[Dict[str, Any]] = Field(
        ..., description="Danh sách các câu hỏi của bài tập"
    )
