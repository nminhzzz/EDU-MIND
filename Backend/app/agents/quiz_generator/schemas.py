"""
Giai đoạn 3 — Fix quiz_generator/schemas.py:
  + Đổi tên QuizResponseSchema → QuizResponse (agent.py đang import tên này)
  + Thêm QuizOption model rõ ràng
"""

from pydantic import BaseModel, Field
from typing import List


class QuizOption(BaseModel):
    key: str = Field(
        description="Ký tự đại diện: 'A', 'B', 'C', 'D' hoặc 'True'/'False'"
    )
    value: str = Field(description="Nội dung chi tiết của lựa chọn")


class QuizQuestionItem(BaseModel):
    question_text: str = Field(description="Nội dung câu hỏi")
    question_type: str = Field(description="'mcq' hoặc 'true_false'")
    options: List[QuizOption] = Field(description="Danh sách các lựa chọn trả lời")
    correct_answer: str = Field(
        description="Đáp án đúng khớp với key, vd: 'A' hoặc 'True'"
    )
    explanation: str = Field(description="Giải thích tại sao đáp án đó đúng")
    difficulty: str = Field(description="'easy', 'medium', hoặc 'hard'")


class QuizResponse(BaseModel):
    """Output chính từ Quiz Generator Agent."""

    title: str = Field(description="Tiêu đề đề thi")
    questions: List[QuizQuestionItem] = Field(description="Danh sách câu hỏi")
