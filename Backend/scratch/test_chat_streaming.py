import sys
import os
import asyncio

# Thêm Backend vào sys.path để import được app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env thủ công để thiết lập biến môi trường
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                key_clean = key.strip()
                val_clean = val.strip()
                if key_clean not in os.environ or not os.environ[key_clean].strip():
                    os.environ[key_clean] = val_clean

from sqlalchemy.orm import Session
from app.database.mysql import engine, SessionLocal
from app.database.mongodb import get_mongodb_db
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
import app.agents.chat_tutor.memory as tutor_memory
from app.agents.chat_tutor.agent import chat_with_tutor_stream

async def run_chat_streaming_test():
    print("=== KHỞI CHẠY KIỂM THỬ REALTIME STREAMING (CHAT TUTOR) ===")

    # 1. Đồng bộ DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    mongo_db = get_mongodb_db()

    try:
        # 2. Tạo/lấy học sinh test
        student = db.query(User).filter(User.email == "streaming_student_test@test.com").first()
        if not student:
            student = User(
                email="streaming_student_test@test.com",
                password_hash="hashedpassword123",
                full_name="Học Sinh Test Streaming",
                role="student"
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"-> Đã tạo học sinh test ID={student.id}")
        else:
            print(f"-> Học sinh test đã tồn tại ID={student.id}")

        # 3. Tạo/lấy môn học test
        subject = db.query(Subject).filter(Subject.code == "MACLENIN_STREAM").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Streaming)",
                code="MACLENIN_STREAM",
                description="Môn học Triết học phục vụ kiểm thử Chat Streaming"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)
            print(f"-> Đã tạo môn học test ID={subject.id}")
        else:
            print(f"-> Môn học test đã tồn tại ID={subject.id}")

        # 4. Khởi tạo phiên chat trong MongoDB
        session_id = await tutor_memory.create_tutor_session(
            student_id=student.id,
            subject_id=subject.id,
            title="Học Triết học Marx Realtime Streaming"
        )
        print(f"-> Đã tạo phiên chat mới trong MongoDB, Session ID: {session_id}")

        # 5. Gửi câu hỏi và stream phản hồi
        prompt = "Hãy giải thích ngắn gọn quy luật phủ định của phủ định trong triết học Mác-Lênin."
        print(f"\n[User]: {prompt}\n")
        print("[Gia sư] (Streaming...): ", end="", flush=True)

        full_reply = []
        # Gọi chat_with_tutor_stream nhận từng token
        async for token in chat_with_tutor_stream(
            user_message=prompt,
            student_id=student.id,
            session_id=session_id
        ):
            print(token, end="", flush=True)
            full_reply.append(token)
            await asyncio.sleep(0.001)

        print("\n\n✓ Stream kết thúc thành công!")
        reply_text = "".join(full_reply)
        assert len(reply_text) > 0, "Không nhận được phản hồi nào từ gia sư!"

        # 6. Kiểm định lưu trữ trong MongoDB
        chat_summary, messages = await tutor_memory.get_tutor_history(session_id)
        assert len(messages) >= 2, "Hội thoại không được lưu vào MongoDB!"
        print(f"✓ MongoDB History: Tìm thấy {len(messages)} tin nhắn trong phiên chat.")
        print(f"  * Tin nhắn cuối của Gia sư lưu trong MongoDB: {messages[-1]['content'][:80]}...")

        print("\n🎉🎉 CHÚC MỪNG! THỬ NGHIỆM CHAT SSE STREAMING ĐÃ HOÀN TOÀN THÀNH CÔNG! 🎉🎉")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_chat_streaming_test())
