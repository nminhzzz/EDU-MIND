from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import StudentGrade


# ── Đăng ký ──────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"            # "student" | "teacher" | "admin"
    grade: Optional[StudentGrade] = None  # Khối lớp học (chỉ dùng cho học sinh: grade_10, grade_11, grade_12)



# ── Đăng nhập ─────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Token trả về ──────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
