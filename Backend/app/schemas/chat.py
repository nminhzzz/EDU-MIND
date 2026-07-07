from pydantic import BaseModel
from typing import Optional, List


class TutorSessionCreate(BaseModel):
    subject_id: int
    title: Optional[str] = "Trò chuyện cùng Gia sư ảo"


class TutorMessageSend(BaseModel):
    session_id: str
    content: str


class TutorSessionResponse(BaseModel):
    session_id: str
    student_id: int
    subject_id: int
    title: str
    chat_summary: str
    created_at: str
    updated_at: str


class TutorMessageResponse(BaseModel):
    role: str
    content: str


class TutorChatResponse(BaseModel):
    reply: str
    history: List[TutorMessageResponse]
