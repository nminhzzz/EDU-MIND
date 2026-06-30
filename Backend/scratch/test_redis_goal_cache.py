import sys
import os
import asyncio
import time
import json
from datetime import datetime, date, timedelta

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
from app.database.redis import redis_client
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan

import app.services.goal_service as goal_service

async def run_redis_cache_test():
    print("--- KHỞI CHẠY KIỂM THỬ TÍCH HỢP REDIS CACHE CHO GOAL PLANNER ---")
    
    # Check if redis connection works
    try:
        redis_client.ping()
        print("-> Đã kết nối thành công tới Redis!")
    except Exception as e:
        print(f"ERROR: Không thể kết nối tới Redis: {e}")
        return

    # 1. Đồng bộ cấu trúc MySQL
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Tạo học sinh giả lập
        student = db.query(User).filter(User.email == "student_redis_test@test.com").first()
        if not student:
            student = User(
                email="student_redis_test@test.com",
                password_hash="hashedpassword123",
                full_name="Học Sinh Test Redis",
                role="student"
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
        # 3. Tạo môn học giả lập
        subject = db.query(Subject).filter(Subject.code == "TRIETHOC_REDIS").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Redis)",
                code="TRIETHOC_REDIS",
                description="Môn học Triết học kiểm thử Redis Cache"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)

        test_deadline = (date.today() + timedelta(days=14))
        
        # =====================================================================
        # BƯỚC 1: Sinh lộ trình nháp và lưu MongoDB + Redis
        # =====================================================================
        print("\n[Bước 1] Khởi tạo sinh lộ trình học nháp lần đầu môn Triết học...")
        draft_result = await goal_service.generate_goal_plan_draft(
            student=student,
            subject_obj=subject,
            target_score=8.5,
            deadline=test_deadline,
            db=db
        )
        
        session_id = draft_result["session_id"]
        print(f"-> Tạo thành công phiên chat, Session ID: {session_id}")
        
        # =====================================================================
        # BƯỚC 2: Kiểm tra Cache tồn tại và TTL trong Redis
        # =====================================================================
        print("\n[Bước 2] Kiểm tra key trong Redis Cache...")
        cache_key = f"goal_draft:{session_id}"
        cached_val = redis_client.get(cache_key)
        ttl = redis_client.ttl(cache_key)
        
        if not cached_val:
            print("❌ Thất bại: Không tìm thấy key trong Redis Cache!")
            assert False, "Redis Cache Key does not exist"
            
        print("✓ Key tồn tại trong Redis Cache!")
        print(f"-> TTL của key: {ttl} giây (Mong muốn: ~1800 giây)")
        assert ttl > 1700, f"TTL is not correct: {ttl}"
        
        # Parse và xác minh cấu trúc dữ liệu lưu trong Redis
        cached_data = json.loads(cached_val)
        print("✓ Dữ liệu JSON trong cache hợp lệ!")
        print(f"-> Học sinh ID: {cached_data['student_id']}")
        print(f"-> Môn học ID: {cached_data['subject_id']}")
        print(f"-> Điểm mục tiêu: {cached_data['target_score']}")
        print(f"-> Deadline: {cached_data['deadline']}")
        print(f"-> Số lượng nhiệm vụ học tập: {len(cached_data['plans'])}")
        
        # =====================================================================
        # BƯỚC 3: Xác nhận chốt lưu (Confirm) và đo lường thời gian xử lý nhanh
        # =====================================================================
        print("\n[Bước 3] Xác nhận lộ trình học tập từ cache...")
        t_start = time.perf_counter()
        confirm_result = await goal_service.confirm_goal_plan_draft(
            db=db,
            student=student,
            subject_obj=subject,
            session_id=session_id,
            target_score=8.5,
            deadline=test_deadline
        )
        t_end = time.perf_counter()
        duration_ms = (t_end - t_start) * 1000
        print(f"✓ Confirm thành công! Thời gian xử lý: {duration_ms:.2f} ms")
        print(f"-> Đã tạo StudyGoal ID trong MySQL: {confirm_result['goal'].id}")
        print(f"-> Tổng số plans đã lưu MySQL: {confirm_result['total_plans']} tasks")
        
        # =====================================================================
        # BƯỚC 4: Xác minh xóa cache sau khi confirm
        # =====================================================================
        print("\n[Bước 4] Xác minh cache đã bị xóa khỏi Redis sau khi confirm...")
        post_confirm_val = redis_client.get(cache_key)
        if post_confirm_val:
            print("❌ Thất bại: Key cache vẫn tồn tại trong Redis!")
            assert False, "Redis Cache Key was not deleted after confirm"
        print("✓ Xác nhận key cache đã bị xóa hoàn toàn khỏi Redis!")

        # Dọn dẹp dữ liệu MySQL của test vừa rồi để test fallback sạch sẽ
        db.query(StudyPlan).filter(StudyPlan.goal_id == confirm_result['goal'].id).delete()
        db.query(StudyGoal).filter(StudyGoal.id == confirm_result['goal'].id).delete()
        db.commit()

        # =====================================================================
        # BƯỚC 5: Kiểm tra cơ chế Fallback (Xóa cache Redis và gọi Confirm)
        # =====================================================================
        print("\n[Bước 5] Kiểm tra cơ chế Fallback sang MongoDB...")
        
        # Sinh nháp mới để tạo cache mới
        draft_result_fallback = await goal_service.generate_goal_plan_draft(
            student=student,
            subject_obj=subject,
            target_score=8.5,
            deadline=test_deadline,
            db=db
        )
        session_id_fallback = draft_result_fallback["session_id"]
        cache_key_fallback = f"goal_draft:{session_id_fallback}"
        
        # Giả lập cache bị xóa/hết hạn bằng cách delete key khỏi Redis
        print("-> Tiến hành xóa key cache khỏi Redis để giả lập hết hạn...")
        redis_client.delete(cache_key_fallback)
        
        # Gọi confirm và kiểm tra xem có fallback sang MongoDB thành công không
        print("-> Tiến hành gọi Confirm...")
        t_start_fallback = time.perf_counter()
        confirm_result_fallback = await goal_service.confirm_goal_plan_draft(
            db=db,
            student=student,
            subject_obj=subject,
            session_id=session_id_fallback,
            target_score=8.5,
            deadline=test_deadline
        )
        t_end_fallback = time.perf_counter()
        duration_ms_fallback = (t_end_fallback - t_start_fallback) * 1000
        
        print(f"✓ Confirm fallback thành công! Thời gian xử lý: {duration_ms_fallback:.2f} ms")
        print(f"-> Đã tạo StudyGoal ID mới trong MySQL (qua fallback): {confirm_result_fallback['goal'].id}")
        print(f"-> Tổng số plans đã lưu MySQL (qua fallback): {confirm_result_fallback['total_plans']} tasks")
        
        # Dọn dẹp dữ liệu test trong MySQL
        db.query(StudyPlan).filter(StudyPlan.goal_id == confirm_result_fallback['goal'].id).delete()
        db.query(StudyGoal).filter(StudyGoal.id == confirm_result_fallback['goal'].id).delete()
        db.commit()
        
        print("\n=== KIỂM THỬ THÀNH CÔNG RỰC RỠ! ===")
        
    except Exception as e:
        print(f"\n❌ ERROR: Lỗi trong quá trình chạy test Redis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_redis_cache_test())
