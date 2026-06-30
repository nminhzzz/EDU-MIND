from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class StudyDocumentCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề tài liệu học tập")
    file_path: str = Field(..., description="Đường dẫn tệp (Cloudinary hoặc URL local)")
    file_type: str = Field(..., description="Định dạng tệp: pdf, docx, txt, md...")
    subject_id: int = Field(..., description="ID môn học liên kết")

class StudyDocumentResponse(BaseModel):
    id: int
    title: str
    file_path: str
    file_type: str
    subject_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

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
    # Cấu trúc câu hỏi tự soạn dạng danh sách
    questions: List[Dict[str, Any]] = Field(..., description="Danh sách các câu hỏi của bài tập")
