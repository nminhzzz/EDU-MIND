from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.user import StudentGrade

# Roles allowed for self-registration — admin accounts must be seeded manually.
_ALLOWED_ROLES = {"student", "teacher"}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"
    grade: Optional[StudentGrade] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in _ALLOWED_ROLES:
            raise ValueError(
                f"Role '{v}' không được phép tự đăng ký. "
                f"Chỉ chấp nhận: {', '.join(sorted(_ALLOWED_ROLES))}."
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
