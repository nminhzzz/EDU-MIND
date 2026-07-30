"""
Pydantic schemas cho Quiz sinh bởi AI — Giai đoạn 3 & 4.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.quiz_attempt import QuizAttemptResponse


class QuizOptionSchema(BaseModel):
    key: str = Field(description="Ký tự lựa chọn, vd: A, B, C, D hoặc True, False")
    value: str = Field(description="Nội dung lựa chọn")


class QuestionItemStudentResponse(BaseModel):
    """Câu hỏi trả về cho học sinh làm bài (không lộ đáp án)."""

    question_text: str = Field(default="", description="Nội dung câu hỏi")
    question_type: Optional[str] = Field(default="mcq", description="Loại câu hỏi: mcq hoặc essay")
    options: Optional[List[QuizOptionSchema]] = Field(default=[], description="Danh sách các lựa chọn")


class QuestionItemDetailResponse(QuestionItemStudentResponse):
    """Câu hỏi kèm đáp án và giải thích (cho giáo viên hoặc sau khi học sinh nộp bài)."""

    correct_answer: Optional[str] = Field(default="", description="Đáp án đúng hoặc đáp án mẫu")
    explanation: Optional[str] = Field(default="", description="Giải thích lý thuyết")


class ClassroomQuizCreateRequest(BaseModel):
    subject_id: int = Field(description="ID môn học")
    topic: Optional[str] = Field(None, description="Chủ đề kiến thức cần kiểm tra")
    document_id: Optional[int] = Field(None, description="ID tài liệu đã upload trên hệ thống")
    document_ids: Optional[List[int]] = Field(None, description="Danh sách ID tài liệu chọn để sinh đề")
    custom_prompt: Optional[str] = Field(None, description="Yêu cầu/chỉ thị riêng của giáo viên cho AI")
    difficulty: str = Field(default="medium", description="Độ khó: easy, medium, hard")
    total_questions: int = Field(default=5, description="Số lượng câu hỏi cần tạo")
    deadline: Optional[datetime] = Field(None, description="Hạn chót nộp bài (ISO-8601)")
    time_limit_minutes: Optional[int] = Field(default=30, description="Thời gian làm bài tính bằng phút")
    max_tab_violations: Optional[int] = Field(default=3, description="Số lần vi phạm chuyển tab tối đa")
    include_essay: bool = Field(default=False, description="Có bao gồm câu hỏi tự luận không")
    essay_count: int = Field(default=2, description="Số lượng câu hỏi tự luận muốn tạo")


class QuizResponse(BaseModel):
    id: int
    student_id: Optional[int] = None
    subject_id: int
    study_plan_id: Optional[int] = None
    classroom_id: Optional[int] = None
    document_id: Optional[int] = None
    title: str
    difficulty: str
    total_questions: int
    generated_by_ai: bool
    deadline: Optional[datetime] = None
    time_limit_minutes: Optional[int] = 30
    max_tab_violations: Optional[int] = 3
    created_at: datetime
    questions: List[QuestionItemStudentResponse]

    class Config:
        from_attributes = True


class QuizDetailResponse(BaseModel):
    id: int
    student_id: Optional[int] = None
    subject_id: int
    study_plan_id: Optional[int] = None
    classroom_id: Optional[int] = None
    document_id: Optional[int] = None
    title: str
    difficulty: str
    total_questions: int
    generated_by_ai: bool
    deadline: Optional[datetime] = None
    time_limit_minutes: Optional[int] = 30
    max_tab_violations: Optional[int] = 3
    created_at: datetime
    questions: List[QuestionItemDetailResponse]
    latest_attempt: Optional[QuizAttemptResponse] = None

    class Config:
        from_attributes = True


class QuestionItemUpdateRequest(BaseModel):
    question_text: str = Field(description="Nội dung câu hỏi")
    question_type: str = Field(default="mcq", description="Loại câu hỏi: mcq hoặc essay")
    options: List[QuizOptionSchema] = Field(default=[], description="Danh sách các lựa chọn")
    correct_answer: str = Field(description="Đáp án đúng hoặc đáp án mẫu")
    explanation: Optional[str] = Field(None, description="Giải thích đáp án")


class QuizUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Tiêu đề bài kiểm tra")
    difficulty: Optional[str] = Field(None, description="Độ khó")
    deadline: Optional[datetime] = Field(None, description="Hạn chót nộp bài")
    questions: Optional[List[QuestionItemUpdateRequest]] = Field(None, description="Danh sách câu hỏi đã chỉnh sửa")

