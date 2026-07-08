"""
Chat Tutor memory management — MongoDB-backed session storage with
sliding-window summarisation to keep context within LLM token limits.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from bson import ObjectId

from app.infrastructure.ai import generate_content_nvidia
from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db

logger = get_logger(__name__)

MAX_MESSAGES = 10
MESSAGES_TO_SUMMARIZE = 6

_NOW = lambda: datetime.now(timezone.utc)  # noqa: E731


async def create_tutor_session(
    student_id: int, subject_id: int, title: str = "Trò chuyện cùng Gia sư ảo"
) -> str:
    """Create a new Chat Tutor session in MongoDB and return its ID."""
    db = get_mongodb_db()
    now = _NOW()
    result = await db["tutor_sessions"].insert_one(
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "title": title,
            "chat_summary": "",
            "created_at": now,
            "updated_at": now,
        }
    )
    return str(result.inserted_id)


async def get_tutor_sessions(
    student_id: int, subject_id: Optional[int] = None
) -> List[Dict]:
    """Return all sessions for a student, optionally filtered by subject."""
    db = get_mongodb_db()
    query: Dict = {"student_id": student_id}
    if subject_id is not None:
        query["subject_id"] = subject_id

    sessions = []
    async for doc in db["tutor_sessions"].find(query).sort("updated_at", -1):
        sessions.append(
            {
                "session_id": str(doc["_id"]),
                "student_id": doc["student_id"],
                "subject_id": doc["subject_id"],
                "title": doc["title"],
                "chat_summary": doc.get("chat_summary", ""),
                "created_at": doc["created_at"].isoformat(),
                "updated_at": doc["updated_at"].isoformat(),
            }
        )
    return sessions


async def get_tutor_history(session_id: str) -> Tuple[str, List[Dict[str, str]]]:
    """Return (chat_summary, recent_messages) for the given session."""
    db = get_mongodb_db()

    session = await db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
    if not session:
        return "", []

    chat_summary: str = session.get("chat_summary", "")

    messages: List[Dict[str, str]] = []
    async for doc in (
        db["tutor_messages"]
        .find({"session_id": ObjectId(session_id)})
        .sort("created_at", 1)
    ):
        messages.append({"role": doc["role"], "content": doc["content"]})

    return chat_summary, messages


async def add_tutor_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the session and update the session timestamp."""
    db = get_mongodb_db()
    now = _NOW()
    await db["tutor_messages"].insert_one(
        {
            "session_id": ObjectId(session_id),
            "role": role,
            "content": content,
            "created_at": now,
        }
    )
    await db["tutor_sessions"].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updated_at": now}},
    )


async def summarize_session_if_needed(session_id: str) -> None:
    """
    When message count exceeds MAX_MESSAGES, summarise the oldest
    MESSAGES_TO_SUMMARIZE messages via NVIDIA NIM and delete them.
    This keeps the context window manageable while preserving conversation context.
    """
    db = get_mongodb_db()

    msg_count = await db["tutor_messages"].count_documents(
        {"session_id": ObjectId(session_id)}
    )
    if msg_count <= MAX_MESSAGES:
        return

    session = await db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
    if not session:
        return

    current_summary: str = session.get("chat_summary", "")

    messages_to_sum = []
    ids_to_delete = []
    async for doc in (
        db["tutor_messages"]
        .find({"session_id": ObjectId(session_id)})
        .sort("created_at", 1)
        .limit(MESSAGES_TO_SUMMARIZE)
    ):
        messages_to_sum.append(f"{doc['role']}: {doc['content']}")
        ids_to_delete.append(doc["_id"])

    if not messages_to_sum:
        return

    conversation_text = "\n".join(messages_to_sum)
    if current_summary:
        prompt = (
            f"Tóm tắt bối cảnh cũ trước đó:\n{current_summary}\n\n"
            f"Các tin nhắn hội thoại mới diễn ra tiếp theo:\n{conversation_text}\n\n"
            "Hãy gộp và cập nhật một tóm tắt hội thoại mới, ngắn gọn, súc tích bằng tiếng Việt, "
            "ghi nhận đầy đủ các thông tin cốt lõi (chủ đề thảo luận, kiến thức học sinh gặp khó khăn, "
            "lời khuyên của gia sư). Không cần lời chào hay dẫn dắt, chỉ trả về đoạn tóm tắt."
        )
    else:
        prompt = (
            f"Các tin nhắn hội thoại cần tóm tắt:\n{conversation_text}\n\n"
            "Hãy tạo một đoạn tóm tắt ngắn gọn, súc tích bằng tiếng Việt về cuộc hội thoại trên, "
            "nêu rõ chủ đề thảo luận, kiến thức học sinh gặp khó khăn và lời khuyên của gia sư. "
            "Chỉ trả về đoạn tóm tắt."
        )

    try:
        new_summary = generate_content_nvidia(
            messages=[{"role": "user", "content": prompt}],
            system_instruction="Bạn là trợ lý ảo phân tích hội thoại.",
            temperature=0.3,
        )

        await db["tutor_sessions"].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"chat_summary": new_summary, "updated_at": _NOW()}},
        )
        logger.info(
            "Summarised %d messages for session %s (summary: %d chars).",
            MESSAGES_TO_SUMMARIZE,
            session_id,
            len(new_summary),
        )

        await db["tutor_messages"].delete_many({"_id": {"$in": ids_to_delete}})
        logger.debug("Deleted %d old messages from tutor_messages.", len(ids_to_delete))

    except Exception as exc:
        logger.warning("Failed to summarise tutor session %s: %s", session_id, exc)


async def verify_session_owner(session_id: str, student_id: int) -> bool:
    """Return True if the session exists and belongs to the given student."""
    db = get_mongodb_db()
    try:
        session = await db["tutor_sessions"].find_one(
            {"_id": ObjectId(session_id), "student_id": student_id}
        )
        return session is not None
    except Exception:
        return False


async def delete_tutor_session(session_id: str, student_id: int) -> bool:
    """Delete a session and all its messages. Returns False if not found/authorised."""
    db = get_mongodb_db()

    session = await db["tutor_sessions"].find_one(
        {"_id": ObjectId(session_id), "student_id": student_id}
    )
    if not session:
        return False

    await db["tutor_messages"].delete_many({"session_id": ObjectId(session_id)})
    await db["tutor_sessions"].delete_one({"_id": ObjectId(session_id)})
    return True
