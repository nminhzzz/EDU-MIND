import sys
import os
import asyncio
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
from app.database.redis import get_redis_client
from app.database.mongodb import get_mongodb_db
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.student_preference import StudentPreference

from app.services.unified_service import generate_unified_draft, confirm_unified_draft


async def run_unified_flow_test():
    print("=== KHỞI CHẠY KIỂM THỬ TÍCH HỢP HỢP NHẤT (UNIFIED GOAL PLANNER) ===")

    # 1. Kết nối Redis, MongoDB, MySQL
    redis_client = get_redis_client()
    try:
        redis_client.ping()
        print("✓ Đã kết nối thành công tới Redis Cache!")
    except Exception as e:
        print(f"❌ ERROR: Không thể kết nối tới Redis: {e}")
        return

    db_mongo = get_mongodb_db()
    print("✓ Đã kết nối thành công tới MongoDB!")

    # 2. Đồng bộ MySQL
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("✓ Đã kết nối thành công tới MySQL!")

    try:
        # 3. Tạo/lấy học sinh test
        student = (
            db.query(User).filter(User.email == "unified_student_test@test.com").first()
        )
        if not student:
            student = User(
                email="unified_student_test@test.com",
                password_hash="hashedpassword123",
                full_name="Học Sinh Test Hợp Nhất",
                role="student",
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"-> Đã tạo học sinh test mới ID={student.id}")
        else:
            print(f"-> Học sinh test đã tồn tại ID={student.id}")

        # Cài đặt sở thích rảnh để kiểm định thời khóa biểu
        pref = (
            db.query(StudentPreference)
            .filter(StudentPreference.student_id == student.id)
            .first()
        )
        if not pref:
            pref = StudentPreference(
                student_id=student.id,
                study_hours_per_day=2,
                preferred_study_time="evening",
                available_schedule={
                    "mon": {"morning": True, "afternoon": False, "evening": True},
                    "tue": {"morning": True, "afternoon": True, "evening": True},
                    "wed": {"morning": False, "afternoon": True, "evening": True},
                    "thu": {"morning": True, "afternoon": False, "evening": True},
                    "fri": {"morning": True, "afternoon": True, "evening": False},
                    "sat": {"morning": False, "afternoon": False, "evening": False},
                    "sun": {"morning": False, "afternoon": False, "evening": False},
                },
            )
            db.add(pref)
            db.commit()
            print("-> Đã thiết lập sở thích học tập: Học 2h/ngày từ T2-T6, nghỉ T7-CN.")

        # 4. Tạo/lấy môn học test
        subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Unified)",
                code="MACLENIN_UNIFIED",
                description="Môn học Triết học phục vụ kiểm thử Unified Flow",
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)
            print(f"-> Đã tạo môn học test mới ID={subject.id}")
        else:
            print(f"-> Môn học test đã tồn tại ID={subject.id}")

        # Seeding dữ liệu tài liệu MongoDB RAG nếu rỗng
        coll = db_mongo["study_material_embeddings"]
        count = await coll.count_documents({"subject_id": subject.id})
        if count == 0:
            await coll.insert_many(
                [
                    {
                        "subject_id": subject.id,
                        "topic": "Chương 1: Triết học và vai trò của triết học trong đời sống xã hội",
                        "content": "Triết học ra đời từ hoạt động thực tiễn, đáp ứng nhu cầu nhận thức thế giới. Đối tượng của triết học thay đổi qua các thời kỳ lịch sử.",
                        "embedding": [0.0] * 4096,  # Mock embedding cho test
                    },
                    {
                        "subject_id": subject.id,
                        "topic": "Chương 2: Vật chất và Ý thức",
                        "content": "Vật chất là phạm trù triết học dùng để chỉ thực tại khách quan. Ý thức là sự phản ánh năng động, sáng tạo thế giới khách quan vào bộ não người.",
                        "embedding": [0.0] * 4096,
                    },
                ]
            )
            print("-> Đã seed dữ liệu mẫu giáo trình vào MongoDB để test RAG.")

        test_deadline = date.today() + timedelta(days=14)

        # =====================================================================
        # BƯỚC 1: Sinh lộ trình nháp (Unified Draft)
        # =====================================================================
        print("\n[Bước 1] Gọi Service sinh lộ trình hợp nhất nháp (Unified Plan)...")
        draft_result = await generate_unified_draft(
            student=student,
            subject_obj=subject,
            target_score=8.0,
            deadline=test_deadline,
            user_message="Hãy lập cho tôi một lộ trình học hiệu quả.",
            session_id=None,
        )

        session_id = draft_result["session_id"]
        plan = draft_result["plan"]

        print(f"✓ Sinh bản nháp thành công! Session ID: {session_id}")
        print(f"-> Số tuần học: {len(plan.weeks)}")
        print(f"-> Số ngày học chi tiết: {len(plan.daily_schedule)}")
        print(f"-> Số giáo trình RAG tìm được: {len(plan.curriculum_materials)}")
        print(f"-> Số bài kiểm tra sinh ra: {len(plan.quizzes)}")

        # Kiểm tra chi tiết định dạng
        assert len(plan.weeks) > 0, "Không có lộ trình tuần!"
        assert len(plan.daily_schedule) > 0, "Không có thời khóa biểu ngày!"
        assert len(plan.quizzes) > 0, "Không sinh đề thi trắc nghiệm!"

        print("\n--- Chi tiết thời khóa biểu (3 ngày đầu): ---")
        for day in plan.daily_schedule[:3]:
            print(
                f"  * {day.date} ({day.start_time} - {day.end_time}): {day.task} ({day.description})"
            )

        print("\n--- Câu hỏi trắc nghiệm đầu tiên (Quiz 1 - Q1): ---")
        first_quiz = plan.quizzes[0]
        print(f"Bài thi: {first_quiz.title}")
        if first_quiz.questions:
            q = first_quiz.questions[0]
            print(f"  * Câu hỏi: {q.question_text}")
            print(f"  * Các phương án:")
            for opt in q.options:
                print(f"    - {opt.key}: {opt.value}")
            print(f"  * Đáp án đúng: {q.correct_answer}")
            print(f"  * Giải thích: {q.explanation}")

        # Kiểm tra Redis Cache
        cache_key = f"unified_draft:{session_id}"
        cached_data = redis_client.get(cache_key)
        assert cached_data is not None, "Lộ trình nháp không được lưu vào Redis Cache!"
        print("\n✓ Đã xác minh lộ trình nháp được lưu vào Redis thành công.")

        # =====================================================================
        # BƯỚC 2: Tinh chỉnh lộ trình nháp (Unified Refinement)
        # =====================================================================
        print(
            "\n[Bước 2] Học sinh phản hồi tinh chỉnh: 'Hãy thêm nhiều câu hỏi trắc nghiệm giải thích chi tiết hơn'..."
        )
        refine_result = await generate_unified_draft(
            student=student,
            subject_obj=subject,
            target_score=8.0,
            deadline=test_deadline,
            user_message="Hãy thêm nhiều câu hỏi trắc nghiệm giải thích chi tiết hơn.",
            session_id=session_id,
        )
        refined_plan = refine_result["plan"]
        print(
            f"✓ Tinh chỉnh thành công! Số câu hỏi của Quiz đầu: {len(refined_plan.quizzes[0].questions)}"
        )

        # =====================================================================
        # BƯỚC 3: Xác nhận lưu chính thức (Unified Confirm)
        # =====================================================================
        print("\n[Bước 3] Xác nhận lưu chính thức lộ trình vào MySQL...")
        confirm_result = await confirm_unified_draft(
            db=db,
            student=student,
            subject_obj=subject,
            session_id=session_id,
            target_score=8.0,
            deadline=test_deadline,
        )

        print("✓ Xác nhận thành công!")
        print(f"-> Số ngày học được tạo: {confirm_result['total_plans']}")
        print(f"-> Số đề thi trắc nghiệm được tạo: {confirm_result['total_quizzes']}")

        # Xác minh trong MySQL DB
        db_goal = (
            db.query(StudyGoal)
            .filter(
                StudyGoal.student_id == student.id, StudyGoal.subject_id == subject.id
            )
            .first()
        )
        assert db_goal is not None, "Mục tiêu học tập chưa được lưu!"
        print(
            f"✓ MySQL StudyGoal: ID={db_goal.id}, Target Score={db_goal.target_score}"
        )

        db_plans_count = (
            db.query(StudyPlan).filter(StudyPlan.goal_id == db_goal.id).count()
        )
        assert (
            db_plans_count == confirm_result["total_plans"]
        ), "Số lịch học MySQL không khớp!"
        print(f"✓ MySQL StudyPlans: Tìm thấy {db_plans_count} nhiệm vụ lịch học.")

        db_quiz = db.query(Quiz).filter(Quiz.subject_id == subject.id).first()
        assert db_quiz is not None, "Đề thi trắc nghiệm chưa được lưu!"
        print(f"✓ MySQL Quiz: Tìm thấy đề thi ID={db_quiz.id}, Title='{db_quiz.title}'")

        db_qb_questions_count = len(db_quiz.questions) if db_quiz.questions else 0
        print(f"✓ MySQL Questions trong đề thi: {db_qb_questions_count} câu hỏi.")
        assert db_qb_questions_count > 0, "Đề thi không có câu hỏi nào!"

        # Kiểm tra Redis Cache bị xóa sau khi confirm
        cached_data_after = redis_client.get(cache_key)
        assert (
            cached_data_after is None
        ), "Redis Cache chưa được giải phóng sau khi confirm!"
        print("✓ Đã xác minh Redis Cache được xóa sạch sau khi confirm.")

        print(
            "\n🎉🎉 CHÚC MỪNG! TẤT CẢ KIỂM THỬ HỢP NHẤT ĐÃ THÀNH CÔNG VƯỢT TRỘI! 🎉🎉"
        )

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_unified_flow_test())
