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
    score: Optional[float] = Field(None, description="Điểm số câu tự luận (thang 10)")
    feedback: Optional[str] = Field(None, description="Nhận xét chi tiết từ AI Grader")
    essay_file_path: Optional[str] = Field(None, description="Đường dẫn file bài làm đã tải lên")


class QuizAttemptCreate(BaseModel):
    answers: List[QuizAttemptAnswer] = Field(
        description="Danh sách đáp án học sinh đã làm"
    )
    duration_seconds: int = Field(description="Thời gian làm bài tính bằng giây")
    tab_violations_count: int = Field(0, description="Số lần học sinh thoát tab hoặc làm việc riêng")
    essay_file_path: Optional[str] = Field(None, description="Đường dẫn file bài làm tự luận của học sinh")


class AIAssessmentResponse(BaseModel):
    overall_feedback: str = Field(description="Lời phê tổng thể cá nhân hóa từ AI Tutor")
    strengths: List[str] = Field(default_factory=list, description="Danh sách điểm mạnh / chủ đề đã nắm vững")
    weaknesses: List[str] = Field(default_factory=list, description="Danh sách lỗ hổng kiến thức cần ôn tập lại")
    recommendation: Optional[str] = Field(None, description="Gợi ý bước học tiếp theo")


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    answers: List[QuizAttemptAnswerResponse]
    score: float
    correct_count: int
    wrong_count: int
    duration_seconds: int
    tab_violations_count: int
    submitted_at: datetime
    ai_assessment: Optional[AIAssessmentResponse] = Field(None, description="Đánh giá & Lời phê từ AI Tutor")

    class Config:
        from_attributes = True

