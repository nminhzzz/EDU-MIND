"""
Pydantic schemas cho Quiz và Question Bank — Giai đoạn 3.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuizOptionSchema(BaseModel):
    key: str = Field(description="Ký tự lựa chọn, vd: A, B, C, D hoặc True, False")
    value: str = Field(description="Nội dung lựa chọn")


class QuestionBankResponse(BaseModel):
    id: int
    subject_id: int
    topic: Optional[str] = None
    difficulty: str
    question_text: str
    options: Optional[List[QuizOptionSchema]] = None
    # Ẩn correct_answer và explanation khi học sinh xem đề (chỉ trả về khi xem kết quả / teacher xem)
    created_by: Optional[int] = None
    embedding_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionBankDetailResponse(QuestionBankResponse):
    correct_answer: str
    explanation: Optional[str] = None


class QuizCreateRequest(BaseModel):
    classroom_id: int = Field(description="ID lớp học để giao đề thi")
    subject_id: int = Field(description="ID môn học")
    topic: str = Field(description="Chủ đề cần kiểm tra")
    difficulty: str = Field(default="medium", description="Độ khó: easy, medium, hard")
    total_questions: int = Field(default=5, description="Số lượng câu hỏi cần tạo")
    question_type: str = Field(default="mcq", description="Loại câu hỏi: mcq hoặc true_false")


class QuizResponse(BaseModel):
    id: int
    classroom_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    title: str
    difficulty: str
    total_questions: int
    generated_by_ai: bool
    created_at: datetime
    questions: Optional[List[QuestionBankResponse]] = None

    class Config:
        from_attributes = True


class QuizDetailResponse(QuizResponse):
    """Chi tiết đề thi kèm đáp án và giải thích (cho giáo viên hoặc sau khi học sinh nộp bài)."""
    questions: Optional[List[QuestionBankDetailResponse]] = None
