from pydantic import BaseModel, Field
from typing import List, Optional


class WeeklyPlan(BaseModel):
    week: int = Field(description="Số thứ tự của tuần, ví dụ: 1, 2...")
    tasks: List[str] = Field(description="Danh sách các nhiệm vụ học tập trong tuần")


class DailyScheduleTask(BaseModel):
    date: str = Field(description="Ngày học định dạng YYYY-MM-DD")
    start_time: str = Field(description="Giờ bắt đầu định dạng HH:MM")
    end_time: str = Field(description="Giờ kết thúc định dạng HH:MM")
    task: str = Field(description="Nhiệm vụ học tập cụ thể")
    description: str = Field(
        description="Mô tả chi tiết nội dung học tập hoặc nhiệm vụ cần hoàn thành"
    )


class CurriculumMaterial(BaseModel):
    topic: str = Field(description="Chủ đề của tài liệu học tập")
    content: str = Field(description="Tóm tắt nội dung chính của tài liệu học tập")


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


class UnifiedQuiz(BaseModel):
    title: str = Field(description="Tiêu đề bài kiểm tra trắc nghiệm")
    questions: List[QuizQuestionItem] = Field(description="Danh sách câu hỏi kiểm tra")


class UnifiedGoalPlanResponse(BaseModel):
    weeks: List[WeeklyPlan] = Field(description="Lộ trình học tập chia theo từng tuần")
    daily_schedule: List[DailyScheduleTask] = Field(
        description="Thời khóa biểu chi tiết hàng ngày rải đều theo lịch rảnh"
    )
    curriculum_materials: Optional[List[CurriculumMaterial]] = Field(
        default=[], description="Danh sách các tài liệu học tập tham khảo (RAG Context)"
    )
    quizzes: Optional[List[UnifiedQuiz]] = Field(
        default=[],
        description="Các bài kiểm tra trắc nghiệm thử tương ứng với lộ trình",
    )
