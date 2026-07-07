"""
MongoDB Collection Schemas (Pydantic Models) - Simplified Version
=================================================================
Các schema này đại diện cho cấu trúc dữ liệu lưu trong MongoDB (Motor / AsyncIO).
Không dùng SQLAlchemy — chỉ dùng Pydantic để validate và serialize.

Collections:
    - chat_sessions             : Quản lý phiên hội thoại Chat Tutor
    - chat_messages             : Chi tiết tin nhắn theo từng phiên (Memory hội thoại)
    - study_material_embeddings : Vector embeddings tài liệu học (RAG Vector Store)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


# ─── Helper: ObjectId tương thích với Pydantic v2 ───────────────────────────────
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"ObjectId không hợp lệ: {v}")
        return str(v)


# ─── 1. CHAT_SESSIONS ───────────────────────────────────────────────────────
class ChatSession(BaseModel):
    """
    Phiên hội thoại giữa học sinh và AI Chat Tutor.
    Một học sinh có thể mở nhiều phiên khác nhau theo từng môn học.
    """

    id: Optional[str] = Field(default=None, alias="_id")

    # ID học sinh (tham chiếu sang MySQL users.id)
    student_id: int

    # Lớp học liên quan (tùy chọn, giúp AI hiểu ngữ cảnh)
    classroom_id: Optional[int] = None

    # Tiêu đề phiên chat
    title: str = "Phiên hội thoại mới"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 2. CHAT_MESSAGES ───────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    """
    Một tin nhắn đơn lẻ trong phiên chat.
    Lưu trữ theo chuỗi để AI đọc làm bộ nhớ ngữ cảnh hội thoại.
    """

    id: Optional[str] = Field(default=None, alias="_id")

    # Tham chiếu đến ChatSession._id
    session_id: str

    # "user" (học sinh) hoặc "assistant" (AI)
    role: str

    # Nội dung tin nhắn (Markdown)
    content: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 3. STUDY_MATERIAL_EMBEDDINGS (RAG VECTOR STORE) ─────────────────────────
class StudyMaterialEmbedding(BaseModel):
    """
    Mảnh tài liệu học tập cùng Vector Embedding tương ứng phục vụ RAG.
    """

    id: Optional[str] = Field(default=None, alias="_id")

    # Tham chiếu sang MySQL subjects.id
    subject_id: int

    # Chủ đề / chương của tài liệu
    topic: str

    # Nội dung văn bản mảnh tài liệu
    content: str

    # Mảng vector số thực biểu diễn ngữ nghĩa (tương thích NVIDIA NIM)
    embedding: List[float]

    # Các metadata bổ sung (số trang, tên tài liệu gốc...)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
