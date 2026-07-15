"""
Giai đoạn 3 — Fix quiz_generator/schemas.py:
  + Đổi tên QuizResponseSchema → QuizResponse (agent.py đang import tên này)
  + Thêm QuizOption model rõ ràng
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QuizOption(BaseModel):
    key: str = Field(
        description="Ký tự đại diện: 'A', 'B', 'C', 'D' hoặc 'True'/'False'"
    )
    value: str = Field(description="Nội dung chi tiết của lựa chọn")


class QuizQuestionItem(BaseModel):
    question_text: str = Field(description="Nội dung câu hỏi")
    question_type: str = Field(description="'mcq', 'true_false', hoặc 'essay'")
    options: Optional[List[QuizOption]] = Field(default=None, description="Danh sách các lựa chọn trả lời (bỏ qua nếu là tự luận)")
    correct_answer: str = Field(
        description="Đáp án đúng khớp với key (trắc nghiệm) hoặc Đáp án mẫu chi tiết (tự luận)"
    )
    explanation: str = Field(description="Giải thích đáp án hoặc tiêu chí chấm điểm tự luận")
    difficulty: str = Field(description="'easy', 'medium', hoặc 'hard'")


class QuizResponse(BaseModel):
    """Output chính từ Quiz Generator Agent."""

    title: str = Field(description="Tiêu đề đề thi")
    questions: List[QuizQuestionItem] = Field(description="Danh sách câu hỏi")
