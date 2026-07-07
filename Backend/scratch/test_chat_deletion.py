import requests
from app.database.mongodb import get_mongodb_db
from bson import ObjectId
import asyncio

BASE_URL = "http://127.0.0.1:8000"


async def test_chat_deletion_async():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "student_test@edumind.com", "password": "studentpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. CREATING A NEW SESSION ---")
    session_res = requests.post(
        f"{BASE_URL}/api/v1/chat/tutor/session",
        json={"subject_id": 1, "title": "Session to be deleted"},
        headers=headers,
    )
    assert session_res.status_code == 201
    session_id = session_res.json()
    print(f"Created Session ID: {session_id}")

    # Gửi tin nhắn mồi để sinh message trong DB
    msg_res = requests.post(
        f"{BASE_URL}/api/v1/chat/tutor/message",
        json={"session_id": session_id, "content": "Hello Tutor!"},
        headers=headers,
    )
    assert msg_res.status_code == 200
    print("Sent test message successfully!")

    # 3. Kiểm tra MongoDB xem session và message đã tồn tại
    db = get_mongodb_db()
    session_doc = await db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
    assert session_doc is not None
    messages_count = await db["tutor_messages"].count_documents(
        {"session_id": ObjectId(session_id)}
    )
    print(
        f"MongoDB verification before deletion: Session exists={session_doc is not None}, Messages count={messages_count}"
    )
    assert messages_count > 0

    # 4. Gửi yêu cầu DELETE xóa session
    print("\n--- 3. DELETING THE SESSION VIA API ---")
    delete_res = requests.delete(
        f"{BASE_URL}/api/v1/chat/tutor/session/{session_id}", headers=headers
    )
    print(f"DELETE status code: {delete_res.status_code}")
    assert delete_res.status_code == 200
    print(f"Response: {delete_res.json()}")

    # 5. Kiểm tra MongoDB xem session và message đã biến mất hoàn toàn
    session_doc_after = await db["tutor_sessions"].find_one(
        {"_id": ObjectId(session_id)}
    )
    messages_count_after = await db["tutor_messages"].count_documents(
        {"session_id": ObjectId(session_id)}
    )
    print(
        f"MongoDB verification after deletion: Session exists={session_doc_after is not None}, Messages count={messages_count_after}"
    )
    assert session_doc_after is None
    assert messages_count_after == 0

    print("\n🎉 ALL TESTS PASSED: CHAT DELETION WORKS PERFECTLY AND CLEANS MONGODB!")


if __name__ == "__main__":
    asyncio.run(test_chat_deletion_async())
