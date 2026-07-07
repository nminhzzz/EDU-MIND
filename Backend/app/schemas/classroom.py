"""
Pydantic schemas cho Classroom — Giai đoạn 4.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from app.schemas.user import UserResponse


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClassroomCreate(BaseModel):
    subject_id: int = Field(..., description="ID môn học")
    class_name: str = Field(..., description="Tên lớp học")
    class_code: str = Field(..., description="Mã lớp học duy nhất")
    description: Optional[str] = Field(None, description="Mô tả lớp học")


class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    description: Optional[str] = None


class ClassroomResponse(BaseModel):
    id: int
    teacher_id: int
    subject_id: int
    class_name: str
    class_code: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClassroomStudentAdd(BaseModel):
    student_email: EmailStr = Field(
        ..., description="Email của học sinh cần thêm vào lớp"
    )


class ClassroomJoin(BaseModel):
    class_code: str = Field(..., description="Mã lớp học để tham gia")


class ClassroomDetailResponse(ClassroomResponse):
    teacher: Optional[UserResponse] = None
    students: Optional[List[UserResponse]] = None
    subject: Optional[SubjectResponse] = None
