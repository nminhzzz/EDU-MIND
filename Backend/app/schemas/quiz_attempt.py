"""
Pydantic schemas cho Quiz Attempt (Lượt làm bài) — Giai đoạn 3.
"""
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class QuizAttemptAnswer(BaseModel):
    question_bank_id: int = Field(description="ID của câu hỏi trong kho câu hỏi")
    answer: str = Field(description="Đáp án học sinh chọn, vd: A, B, C, D hoặc True, False")


class QuizAttemptCreate(BaseModel):
    answers: List[QuizAttemptAnswer] = Field(description="Danh sách đáp án học sinh đã làm")
    duration_seconds: int = Field(description="Thời gian làm bài tính bằng giây")


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    answers: List[QuizAttemptAnswer]
    score: float
    correct_count: int
    wrong_count: int
    duration_seconds: int
    submitted_at: datetime

    class Config:
        from_attributes = True
