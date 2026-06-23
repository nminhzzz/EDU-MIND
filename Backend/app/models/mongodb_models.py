"""
MongoDB Collection Schemas (Pydantic Models)
============================================
Các schema này đại diện cho cấu trúc dữ liệu lưu trong MongoDB (Motor / AsyncIO).
Không dùng SQLAlchemy — chỉ dùng Pydantic để validate và serialize.

Collections:
    - chat_sessions          : Quản lý phiên hội thoại Chat Tutor
    - chat_messages          : Chi tiết tin nhắn theo từng phiên
    - ai_logs                : Log Input/Output của tất cả AI Agents
    - ai_recommendations     : Đề xuất học tập do AI sinh ra
    - study_material_embeddings : Vector embeddings tài liệu học (RAG)
    - learning_events        : Tracking sự kiện học tập của học sinh
    - generated_quizzes      : Đề thi nháp do AI tạo (chưa lưu MySQL)
    - agent_memory           : Bộ nhớ ngắn/dài hạn của Agent (LangGraph State)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


# ─── Helper: ObjectId compat với Pydantic v2 ───────────────────────────────
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
    Phiên hội thoại giữa học sinh và Chat Tutor Agent.
    Một học sinh có thể mở nhiều phiên (ví dụ: theo môn học).
    """
    id: Optional[str] = Field(default=None, alias="_id")

    # ID học sinh (tham chiếu sang MySQL users.id)
    student_id: int
    
    # Lớp học liên quan (tùy chọn, giúp AI hiểu ngữ cảnh)
    classroom_id: Optional[int] = None

    # Tiêu đề phiên chat (AI tự sinh hoặc user đặt)
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
    Lưu theo chuỗi để phục vụ Conversation Memory của Agent.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    # Tham chiếu ChatSession._id
    session_id: str

    # "user" hoặc "assistant"
    role: str

    # Nội dung tin nhắn (text, markdown, hoặc JSON nếu structured)
    content: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 3. AI_LOGS ─────────────────────────────────────────────────────────────
class AILog(BaseModel):
    """
    Log chi tiết từng lần gọi AI Agent.
    Dùng để giám sát, debug và fine-tune prompt.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    # Tên agent: "goal_planner", "quiz_generator", "chat_tutor", ...
    agent_name: str

    # ID học sinh liên quan (NULL nếu là tác vụ hệ thống)
    student_id: Optional[int] = None

    # Dữ liệu đầu vào gửi cho Agent
    input: Dict[str, Any]

    # Dữ liệu đầu ra nhận từ Agent
    output: Dict[str, Any]

    # Thời gian thực thi (giây)
    execution_time: float

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 4. AI_RECOMMENDATIONS ──────────────────────────────────────────────────
class AIRecommendation(BaseModel):
    """
    Đề xuất học tập từ RecommendationAgent.
    Lưu tại đây trước khi giáo viên phê duyệt (HITL) qua MySQL AIRecommendationReview.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    student_id: int

    # Agent nào sinh ra đề xuất: "recommender", "analytics_agent", ...
    source_agent: str

    # Danh sách đề xuất cụ thể:
    # [{"topic": "Chương 2", "action": "Ôn lại lý thuyết", "priority": "high"}]
    recommendations: List[Dict[str, Any]]

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 5. STUDY_MATERIAL_EMBEDDINGS ───────────────────────────────────────────
class StudyMaterialEmbedding(BaseModel):
    """
    Vector embeddings của tài liệu học tập (phục vụ RAG).
    Mỗi document là một đoạn text đã được encode thành vector.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    # Tham chiếu sang MySQL subjects.id
    subject_id: int

    # Chủ đề / chương của tài liệu
    topic: str

    # Nội dung text gốc (chunk)
    content: str

    # Vector embedding (list of floats, ví dụ: 1536 chiều với text-embedding-3-small)
    embedding: List[float]

    # Metadata bổ sung: nguồn tài liệu, trang, tác giả, ...
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 6. LEARNING_EVENTS ─────────────────────────────────────────────────────
class LearningEvent(BaseModel):
    """
    Tracking sự kiện học tập real-time của học sinh.
    Phục vụ phân tích hành vi và kích hoạt AI Recommendations.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    student_id: int

    # Loại sự kiện: "quiz_completed", "plan_done", "goal_created",
    #               "login", "study_session_started", "study_session_ended"
    event_type: str

    # Dữ liệu ngữ cảnh của sự kiện (tùy event_type)
    # Ví dụ quiz_completed: {"quiz_id": 5, "score": 8.5, "duration": 300}
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 7. GENERATED_QUIZZES ───────────────────────────────────────────────────
class GeneratedQuiz(BaseModel):
    """
    Đề thi nháp được QuizGeneratorAgent sinh ra từ QuestionBank + RAG.
    Lưu tạm tại MongoDB trước khi giáo viên xem xét và lưu chính thức vào MySQL.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    student_id: int

    # Tham chiếu sang MySQL subjects.id
    subject_id: int

    # Danh sách câu hỏi đã sinh:
    # [{"question": "...", "options": [...], "correct_answer": "A", "explanation": "..."}]
    questions: List[Dict[str, Any]]

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── 8. AGENT_MEMORY ────────────────────────────────────────────────────────
class AgentMemory(BaseModel):
    """
    Bộ nhớ trạng thái của AI Agent (LangGraph persistent state).
    Lưu mục tiêu hiện tại, tiến độ và ngữ cảnh để Agent hoạt động
    liên tục qua nhiều phiên mà không mất thông tin.
    """
    id: Optional[str] = Field(default=None, alias="_id")

    student_id: int

    # Mục tiêu hiện tại mà Agent đang theo dõi
    goal: str

    # Tóm tắt tiến độ: "Đã hoàn thành 3/5 tuần, điểm trung bình 7.5"
    progress: str

    # Ngữ cảnh bổ sung: lịch học, điểm số, sở thích, ...
    context: Dict[str, Any] = Field(default_factory=dict)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
