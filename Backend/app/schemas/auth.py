from pydantic import BaseModel, EmailStr
from typing import Optional


# ── Đăng ký ──────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"            # "student" | "teacher" | "admin"
    grade: Optional[str] = None      # "Lớp 12", "Đại học năm 1"
    learning_level: Optional[str] = None  # "weak" | "average" | "good" | "excellent"


# ── Đăng nhập ─────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Token trả về ──────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
