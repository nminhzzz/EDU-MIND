import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bson import ObjectId
from app.database.mongodb import get_mongodb_db
from app.agents.base import get_nvidia_client, generate_content_nvidia

# Ngưỡng kích hoạt summary memory
MAX_MESSAGES = 10
MESSAGES_TO_SUMMARIZE = 6


async def create_tutor_session(
    student_id: int, subject_id: int, title: str = "Trò chuyện cùng Gia sư ảo"
) -> str:
    """
    Tạo một phiên chat mới cho Gia sư ảo trong MongoDB.
    """
    db = get_mongodb_db()
    session = {
        "student_id": student_id,
        "subject_id": subject_id,
        "title": title,
        "chat_summary": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db["tutor_sessions"].insert_one(session)
    return str(result.inserted_id)


async def get_tutor_sessions(
    student_id: int, subject_id: Optional[int] = None
) -> List[Dict]:
    """
    Lấy danh sách các phiên chat của học sinh, có thể lọc theo môn học.
    """
    db = get_mongodb_db()
    query = {"student_id": student_id}
    if subject_id is not None:
        query["subject_id"] = subject_id

    cursor = db["tutor_sessions"].find(query).sort("updated_at", -1)
    sessions = []
    async for doc in cursor:
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
    """
    Lấy chat_summary (trí nhớ dài hạn) và danh sách tin nhắn chi tiết gần nhất từ MongoDB.
    """
    db = get_mongodb_db()

    # 1. Lấy thông tin session để lấy chat_summary
    session = await db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
    if not session:
        return "", []

    chat_summary = session.get("chat_summary", "")

    # 2. Lấy danh sách tin nhắn chi tiết
    cursor = (
        db["tutor_messages"]
        .find({"session_id": ObjectId(session_id)})
        .sort("created_at", 1)
    )

    messages = []
    async for doc in cursor:
        messages.append({"role": doc["role"], "content": doc["content"]})

    return chat_summary, messages


async def add_tutor_message(session_id: str, role: str, content: str) -> None:
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
    await db["tutor_messages"].insert_one(message)

    # 2. Cập nhật thời gian updated_at của session
    await db["tutor_sessions"].update_one(
        {"_id": ObjectId(session_id)}, {"$set": {"updated_at": datetime.utcnow()}}
    )


async def summarize_session_if_needed(session_id: str) -> None:
    """
    Kiểm tra nếu số lượng tin nhắn chi tiết vượt quá MAX_MESSAGES.
    Nếu vượt quá, gọi Gemini để tóm tắt các tin nhắn cũ, cập nhật chat_summary và xóa chúng.
    """
    db = get_mongodb_db()

    # 1. Đếm số lượng tin nhắn của session
    msg_count = await db["tutor_messages"].count_documents(
        {"session_id": ObjectId(session_id)}
    )

    if msg_count <= MAX_MESSAGES:
        return

    # 2. Lấy thông tin session
    session = await db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
    if not session:
        return

    current_summary = session.get("chat_summary", "")

    # 3. Lấy ra các tin nhắn cũ cần tóm tắt (MESSAGES_TO_SUMMARIZE tin nhắn cũ nhất)
    cursor = (
        db["tutor_messages"]
        .find({"session_id": ObjectId(session_id)})
        .sort("created_at", 1)
        .limit(MESSAGES_TO_SUMMARIZE)
    )

    messages_to_sum = []
    ids_to_delete = []
    async for doc in cursor:
        messages_to_sum.append(f"{doc['role']}: {doc['content']}")
        ids_to_delete.append(doc["_id"])

    if not messages_to_sum:
        return

    # 4. Gọi NVIDIA NIM để tạo tóm tắt mới
    # Xây dựng prompt tóm tắt hội thoại
    conversation_text = "\n".join(messages_to_sum)

    prompt = "Bạn là một trợ lý ảo phân tích hội thoại. Nhiệm vụ của bạn là cập nhật tóm tắt lịch sử cuộc trò chuyện giữa Học sinh (user) và Gia sư ảo (assistant/model).\n\n"
    if current_summary:
        prompt += f"Tóm tắt bối cảnh cũ trước đó:\n{current_summary}\n\n"
        prompt += (
            f"Các tin nhắn hội thoại mới diễn ra tiếp theo:\n{conversation_text}\n\n"
        )
        prompt += "Hãy gộp và cập nhật một tóm tắt hội thoại mới, ngắn gọn, súc tích bằng tiếng Việt, ghi nhận đầy đủ các thông tin cốt lõi (chủ đề thảo luận, kiến thức học sinh gặp khó khăn, lời khuyên của gia sư). Không cần lời chào hay dẫn dắt, chỉ trả về đoạn tóm tắt."
    else:
        prompt += f"Các tin nhắn hội thoại cần tóm tắt:\n{conversation_text}\n\n"
        prompt += "Hãy tạo một đoạn tóm tắt ngắn gọn, súc tích bằng tiếng Việt về cuộc hội thoại trên, nêu rõ chủ đề thảo luận, kiến thức học sinh gặp khó khăn và lời khuyên của gia sư. Chỉ trả về đoạn tóm tắt."

    # Gọi API
    try:
        new_summary = generate_content_nvidia(
            messages=[{"role": "user", "content": prompt}],
            system_instruction="Bạn là trợ lý ảo phân tích hội thoại.",
            temperature=0.3,
        )

        # 5. Cập nhật `chat_summary` trong session
        await db["tutor_sessions"].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"chat_summary": new_summary, "updated_at": datetime.utcnow()}},
        )
        print(
            f"-> Summarized {MESSAGES_TO_SUMMARIZE} messages for tutor session {session_id}. New summary size: {len(new_summary)} chars."
        )

        # 6. Xóa các tin nhắn đã tóm tắt khỏi collection tutor_messages
        await db["tutor_messages"].delete_many({"_id": {"$in": ids_to_delete}})
        print(f"-> Deleted {len(ids_to_delete)} old messages from tutor_messages.")

    except Exception as e:
        print(f"WARNING: Lỗi khi sinh tóm tắt hội thoại bằng NVIDIA NIM: {e}")


async def delete_tutor_session(session_id: str, student_id: int) -> bool:
    """
    Xóa một phiên chat và tất cả tin nhắn liên quan khỏi MongoDB.
    """
    db = get_mongodb_db()
    # 1. Kiểm tra session có tồn tại và thuộc về student không
    session = await db["tutor_sessions"].find_one(
        {"_id": ObjectId(session_id), "student_id": student_id}
    )
    if not session:
        return False

    # 2. Xóa tất cả tin nhắn liên quan
    await db["tutor_messages"].delete_many({"session_id": ObjectId(session_id)})

    # 3. Xóa session
    await db["tutor_sessions"].delete_one({"_id": ObjectId(session_id)})
    return True
