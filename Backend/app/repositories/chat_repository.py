from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from app.database.mongodb import get_mongodb_db


async def create_chat_session(student_id: int, title: str) -> str:
    """
    Tạo một phiên chat mới trong MongoDB.
    """
    db = get_mongodb_db()
    session = {
        "student_id": student_id,
        "title": title,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db["chat_sessions"].insert_one(session)
    return str(result.inserted_id)


async def get_chat_messages(session_id: str) -> List[Dict[str, str]]:
    """
    Lấy toàn bộ lịch sử tin nhắn của một phiên chat theo thứ tự thời gian.
    """
    db = get_mongodb_db()
    cursor = (
        db["chat_messages"]
        .find({"session_id": ObjectId(session_id)})
        .sort("created_at", 1)
    )

    messages = []
    async for doc in cursor:
        messages.append({"role": doc["role"], "content": doc["content"]})
    return messages


async def add_chat_message(session_id: str, role: str, content: str) -> None:
    """
    Lưu một tin nhắn mới vào MongoDB.
    """
    db = get_mongodb_db()
    # 1. Lưu tin nhắn
    message = {
        "session_id": ObjectId(session_id),
        "role": role,
        "content": content,
        "created_at": datetime.utcnow(),
    }
    await db["chat_messages"].insert_one(message)

    # 2. Cập nhật thời gian updated_at của session
    await db["chat_sessions"].update_one(
        {"_id": ObjectId(session_id)}, {"$set": {"updated_at": datetime.utcnow()}}
    )


async def get_last_assistant_message(session_id: str) -> Optional[str]:
    """
    Lấy nội dung tin nhắn cuối cùng của AI (role='assistant' hoặc role='model')
    để phục vụ việc parse lộ trình lưu vào MySQL.
    """
    db = get_mongodb_db()
    cursor = (
        db["chat_messages"]
        .find(
            {
                "session_id": ObjectId(session_id),
                "role": {"$in": ["assistant", "model"]},
            }
        )
        .sort("created_at", -1)
        .limit(1)
    )

    async for doc in cursor:
        return doc["content"]
    return None
