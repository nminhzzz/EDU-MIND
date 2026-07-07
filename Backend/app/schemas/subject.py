"""
Pydantic schemas cho Subject — Giai đoạn 4.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(..., description="Tên môn học")
    code: str = Field(..., description="Mã môn học duy nhất (UK)")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về môn học")


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên môn học mới")
    code: Optional[str] = Field(None, description="Mã môn học mới (phải duy nhất)")
    description: Optional[str] = Field(None, description="Mô tả mới")


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
