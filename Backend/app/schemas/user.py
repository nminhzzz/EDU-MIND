from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class StudentGrade(str, Enum):
    # Cấp 2
    GRADE_6 = "grade_6"
    GRADE_7 = "grade_7"
    GRADE_8 = "grade_8"
    GRADE_9 = "grade_9"
    # Cấp 3
    GRADE_10 = "grade_10"
    GRADE_11 = "grade_11"
    GRADE_12 = "grade_12"
    # Đại học
    UNI_YEAR_1 = "uni_year_1"
    UNI_YEAR_2 = "uni_year_2"
    UNI_YEAR_3 = "uni_year_3"
    UNI_YEAR_4 = "uni_year_4"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    grade: Optional[StudentGrade] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    grade: Optional[StudentGrade] = None
