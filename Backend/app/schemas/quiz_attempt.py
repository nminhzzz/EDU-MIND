"""
Pydantic schemas cho Quiz Attempt (Lượt làm bài) — Giai đoạn 3 & 4.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class QuizAttemptAnswer(BaseModel):
    question_index: int = Field(description="Chỉ mục câu hỏi trong đề (0-indexed)")
    answer: str = Field(
        description="Đáp án học sinh chọn, vd: A, B, C, D hoặc True, False"
    )


class QuizAttemptAnswerResponse(QuizAttemptAnswer):
    is_correct: Optional[bool] = Field(None, description="Kết quả đúng hay sai")


class QuizAttemptCreate(BaseModel):
    answers: List[QuizAttemptAnswer] = Field(
        description="Danh sách đáp án học sinh đã làm"
    )
    duration_seconds: int = Field(description="Thời gian làm bài tính bằng giây")


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    answers: List[QuizAttemptAnswerResponse]
    score: float
    correct_count: int
    wrong_count: int
    duration_seconds: int
    submitted_at: datetime

    class Config:
        from_attributes = True
