# ============================================================
# Models __init__.py
# Export tất cả SQLAlchemy models để Alembic autogenerate
# phát hiện đúng tất cả bảng khi chạy `alembic revision --autogenerate`
# ============================================================

# Base (phải import trước để metadata được khởi tạo)
from app.models.base import Base

# ── MySQL Models ─────────────────────────────────────────────
from app.models.user import User
from app.models.student_preference import StudentPreference
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.classroom_chat_message import ClassroomChatMessage
from app.models.classroom_chat_read_cursor import ClassroomChatReadCursor
from app.models.study_document import StudyDocument
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.study_plan_progress import StudyPlanProgress
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.notification import Notification

# ── MongoDB Models (Pydantic — không dùng SQLAlchemy) ────────
from app.models.mongo import (
    ChatSession,
    ChatMessage,
    StudyMaterialEmbedding,
)

__all__ = [
    # SQLAlchemy Base
    "Base",
    # MySQL
    "User",
    "StudentPreference",
    "Subject",
    "Classroom",
    "ClassroomStudent",
    "ClassroomChatMessage",
    "ClassroomChatReadCursor",
    "StudyDocument",
    "StudyGoal",
    "StudyPlan",
    "StudyPlanProgress",
    "Quiz",
    "QuizAttempt",
    "LearningAnalytic",
    "Notification",
    # MongoDB
    "ChatSession",
    "ChatMessage",
    "StudyMaterialEmbedding",
]
