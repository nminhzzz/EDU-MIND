"""
Pydantic schemas cho Quiz sinh bởi AI — Giai đoạn 3 & 4.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class QuizOptionSchema(BaseModel):
    key: str = Field(description="Ký tự lựa chọn, vd: A, B, C, D hoặc True, False")
    value: str = Field(description="Nội dung lựa chọn")


class QuestionItemStudentResponse(BaseModel):
    """Câu hỏi trả về cho học sinh làm bài (không lộ đáp án)."""

    question_text: str = Field(description="Nội dung câu hỏi")
    options: List[QuizOptionSchema] = Field(description="Danh sách các lựa chọn")


class QuestionItemDetailResponse(QuestionItemStudentResponse):
    """Câu hỏi kèm đáp án và giải thích (cho giáo viên hoặc sau khi học sinh nộp bài)."""

    correct_answer: str = Field(description="Đáp án đúng (A, B, C, D hoặc True, False)")
    explanation: Optional[str] = Field(None, description="Giải thích lý thuyết")


class QuizCreateRequest(BaseModel):
    subject_id: int = Field(description="ID môn học")
    study_plan_id: Optional[int] = Field(None, description="ID bài học ngày liên quan")
    topic: str = Field(description="Chủ đề kiến thức cần kiểm tra")
    difficulty: str = Field(default="medium", description="Độ khó: easy, medium, hard")
    total_questions: int = Field(default=5, description="Số lượng câu hỏi cần tạo")


class QuizResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    study_plan_id: Optional[int] = None
    title: str
    difficulty: str
    total_questions: int
    generated_by_ai: bool
    created_at: datetime
    questions: List[QuestionItemStudentResponse]

    class Config:
        from_attributes = True


class QuizDetailResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    study_plan_id: Optional[int] = None
    title: str
    difficulty: str
    total_questions: int
    generated_by_ai: bool
    created_at: datetime
    questions: List[QuestionItemDetailResponse]

    class Config:
        from_attributes = True
