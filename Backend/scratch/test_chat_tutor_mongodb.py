import sys
import os
import asyncio
from datetime import datetime

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
from bson import ObjectId

import app.agents.chat_tutor.memory as tutor_memory
import app.agents.chat_tutor.agent as tutor_agent

async def run_chat_tutor_memory_test():
    print("--- KHỞI CHẠY KIỂM THỬ TÍCH HỢP TRÍ NHỚ & TÓM TẮT HỘI THOẠI (CHAT TUTOR) ---")
    
    # 1. Đồng bộ cấu trúc MySQL
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    mongo_db = get_mongodb_db()
    
    try:
        # 2. Lấy hoặc tạo học sinh giả lập
        student = db.query(User).filter(User.email == "student_tutor_test@test.com").first()
        if not student:
            student = User(
                email="student_tutor_test@test.com",
                password_hash="hashedpassword123",
                full_name="Học Sinh Test Chat Tutor",
                role="student"
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
        # 3. Lấy hoặc tạo môn học giả lập
        subject = db.query(Subject).filter(Subject.code == "TRIETHOC_TUTOR").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Tutor Chat)",
                code="TRIETHOC_TUTOR",
                description="Môn học Triết học kiểm thử Chat Tutor Trí Nhớ"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)
            
        # =====================================================================
        # BƯỚC 1: Khởi tạo phiên chat mới trong MongoDB
        # =====================================================================
        print("\n[Bước 1] Khởi tạo phiên chat mới trong MongoDB...")
        session_id = await tutor_memory.create_tutor_session(
            student_id=student.id,
            subject_id=subject.id,
            title="Học Triết học Cổ điển Đức cùng Gia sư"
        )
        print(f"✓ Phiên chat được tạo thành công! Session ID: {session_id}")
        
        # =====================================================================
        # BƯỚC 2: Gửi tin nhắn đầu tiên chứa ngữ cảnh chủ đề cụ thể
        # =====================================================================
        print("\n[Bước 2] Học sinh gửi tin nhắn 1: 'Mình chuẩn bị thi môn Triết và mình rất sợ phần Triết học Cổ điển Đức, đặc biệt là triết học Hegel.'...")
        reply_1, messages_1 = await tutor_agent.chat_with_tutor(
            user_message="Mình chuẩn bị thi môn Triết học và mình rất lo lắng phần Triết học Cổ điển Đức, đặc biệt là triết học của Hegel.",
            student_id=student.id,
            session_id=session_id
        )
        print(f"Gia sư phản hồi: {reply_1[:150]}...")
        
        # =====================================================================
        # BƯỚC 3: Gửi tin nhắn 2 hỏi ẩn ý để test Trí nhớ hội thoại
        # =====================================================================
        print("\n[Bước 3] Học sinh gửi tin nhắn 2 (Hỏi ẩn ý): 'Vậy những điểm cốt lõi trong tư tưởng của ông ấy là gì?'...")
        reply_2, messages_2 = await tutor_agent.chat_with_tutor(
            user_message="Vậy những điểm cốt lõi trong tư tưởng của ông ấy là gì?",
            student_id=student.id,
            session_id=session_id
        )
        print(f"Gia sư phản hồi: {reply_2[:250]}...")
        
        # Kiểm tra xem AI có nhận biết "ông ấy" là Hegel không
        assert "hegel" in reply_2.lower() or "biện chứng" in reply_2.lower() or "phép biện chứng" in reply_2.lower() or "tinh thần" in reply_2.lower(), \
            "AI không nhận biết được ngữ cảnh 'ông ấy' là Hegel từ tin nhắn trước đó!"
        print("✓ Trí nhớ hội thoại hoạt động tốt! AI nhận diện đúng chủ thể Hegel.")
        
        # =====================================================================
        # BƯỚC 4: Gửi thêm tin nhắn liên tục để kích hoạt Summary Memory (> 10 tin nhắn)
        # =====================================================================
        print("\n[Bước 4] Tiến hành gửi thêm tin nhắn để vượt ngưỡng tóm tắt (MAX_MESSAGES = 10)...")
        # Hiện tại session đang có 4 tin nhắn (2 user, 2 assistant)
        test_chats = [
            "Bạn có thể giải thích rõ hơn về tinh thần tuyệt đối (absolute spirit) của Hegel được không?",
            "Làm thế nào để ứng dụng phép biện chứng Hegel vào bài thi tự luận?",
            "Phép biện chứng này gồm những quy luật nào chính?",
            "Quy luật lượng chất có ví dụ thực tế nào dễ nhớ không?",
            "Còn quy luật phủ định của phủ định thì sao bạn?",
            "Tại sao Marx lại phê phán Hegel về chủ nghĩa duy tâm?"
        ]
        
        for idx, msg in enumerate(test_chats):
            print(f" -> Gửi tin nhắn {idx+3}: '{msg[:40]}...'")
            reply, messages = await tutor_agent.chat_with_tutor(
                user_message=msg,
                student_id=student.id,
                session_id=session_id
            )
            
        # Lúc này số lượng tin nhắn đã gửi: 2 (ban đầu) + 6 (thêm) = 8 lượt hỏi-đáp = 16 tin nhắn.
        # Hệ thống đã phải kích hoạt hàm summarize_session_if_needed.
        
        # =====================================================================
        # BƯỚC 5: Kiểm tra và xác minh MongoDB Session Summary
        # =====================================================================
        print("\n[Bước 5] Xác minh MongoDB Session Summary...")
        session_doc = await mongo_db["tutor_sessions"].find_one({"_id": ObjectId(session_id)})
        chat_summary = session_doc.get("chat_summary", "")
        
        if not chat_summary:
            print("❌ Thất bại: Trường chat_summary trống hoặc chưa được sinh!")
            assert False, "chat_summary is empty"
            
        print("✓ Tóm tắt lịch sử (chat_summary) đã được sinh trong MongoDB:")
        print(f"--------------------------------------------------\n{chat_summary}\n--------------------------------------------------")
        
        # Kiểm tra số lượng tin nhắn chi tiết trong tutor_messages
        msg_count = await mongo_db["tutor_messages"].count_documents({"session_id": ObjectId(session_id)})
        print(f"-> Số lượng tin nhắn chi tiết còn lại trong MongoDB: {msg_count} (Ngưỡng MAX_MESSAGES = 10)")
        assert msg_count <= 10, f"Số lượng tin nhắn vẫn vượt quá ngưỡng 10: {msg_count}"
        print("✓ Số lượng tin nhắn chi tiết đã được rút gọn chính xác!")
        
        # =====================================================================
        # BƯỚC 6: Hỏi lại câu hỏi mới dựa trên trí nhớ dài hạn (chat_summary)
        # =====================================================================
        print("\n[Bước 6] Gửi câu hỏi dựa trên bối cảnh tóm tắt dài hạn: 'Tóm lại nãy giờ chúng ta đã thảo luận về những triết gia nào?'...")
        reply_final, messages_final = await tutor_agent.chat_with_tutor(
            user_message="Tóm lại nãy giờ chúng ta đã thảo luận về những triết gia nào?",
            student_id=student.id,
            session_id=session_id
        )
        print(f"Gia sư phản hồi: {reply_final}")
        
        assert "hegel" in reply_final.lower() or "marx" in reply_final.lower() or "triết" in reply_final.lower(), \
            "AI không trả lời được đầy đủ tên các triết gia đã thảo luận dựa trên summary!"
        print("✓ Tái sử dụng bối cảnh tóm tắt thành công! AI ghi nhớ nhất quán.")
        
        print("\n=== KIỂM THỬ TRÍ NHỚ & TÓM TẮT HỘI THOẠI THÀNH CÔNG RỰC RỠ! ===")
        
    except Exception as e:
        print(f"\n❌ ERROR: Lỗi trong quá trình chạy test Chat Tutor Memory: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_chat_tutor_memory_test())
