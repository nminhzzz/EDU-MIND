from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class AdminUserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., min_length=6, description="Mật khẩu (tối thiểu 6 ký tự)")
    full_name: Optional[str] = Field(None, description="Họ và tên")
    role: str = Field("student", description="Vai trò: student, teacher, admin")
    grade: Optional[str] = Field(None, description="Khối lớp (nếu là học sinh)")

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None)
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = Field(None)
    role: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    grade: Optional[str] = Field(None)

class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    grade: Optional[str] = None

    class Config:
        from_attributes = True

class AdminAnalyticsResponse(BaseModel):
    total_students: int
    total_teachers: int
    total_admins: int
    total_classrooms: int
    total_active_goals: int
    total_study_plans: int
    total_quizzes: int
