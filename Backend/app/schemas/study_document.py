"""
Pydantic schemas cho StudyDocument (Ngân hàng tài liệu học tập).
"""

from datetime import datetime
from pydantic import BaseModel, Field


class StudyDocumentCreate(BaseModel):
    subject_id: int = Field(..., description="ID môn học của tài liệu")
    title: str = Field(..., description="Tiêu đề tài liệu")


class StudyDocumentResponse(BaseModel):
    id: int
    subject_id: int
    created_by: int
    title: str
    file_path: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True
