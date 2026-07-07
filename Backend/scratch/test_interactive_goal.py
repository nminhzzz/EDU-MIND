import sys
import os
import asyncio
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
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.learning_analytic import LearningAnalytic

import app.services.goal_service as goal_service


async def run_interactive_test():
    print("--- KHỞI CHẠY KIỂM THỬ TÍCH HỢP CONTEXT MEMORY (MONGODB) ---")

    # 1. Đồng bộ cấu trúc MySQL
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. Tạo học sinh giả lập
        student = (
            db.query(User).filter(User.email == "student_interactive@test.com").first()
        )
        if not student:
            student = User(
                email="student_interactive@test.com",
                password_hash="hashedpassword123",
                full_name="Học Sinh Tương Tác",
                role="student",
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        # 3. Tạo môn học giả lập
        subject = (
            db.query(Subject).filter(Subject.code == "TRIETHOC_INTERACTIVE").first()
        )
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Tương Tác)",
                code="TRIETHOC_INTERACTIVE",
                description="Môn học Triết học kiểm thử tương tác",
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)

        # 4. Gán học lực mẫu điểm TB: 4.0, các phần yếu: Vật chất, Ý thức
        analytic = (
            db.query(LearningAnalytic)
            .filter(
                LearningAnalytic.student_id == student.id,
                LearningAnalytic.subject_id == subject.id,
            )
            .first()
        )
        if not analytic:
            analytic = LearningAnalytic(
                student_id=student.id,
                subject_id=subject.id,
                average_score=4.0,
                quizzes_completed=2,
                weak_topics=["Vật chất", "Ý thức"],
                strong_topics=["Triết học cổ điển Đức"],
                ai_feedback="Học lực trung bình yếu.",
            )
            db.add(analytic)
            db.commit()

        test_deadline = date.today() + timedelta(days=14)

        # =====================================================================
        # BƯỚC 1: Gọi sinh lộ trình nháp lần đầu
        # =====================================================================
        print("\n[Bước 1] Khởi tạo sinh lộ trình học nháp lần đầu môn Triết học...")
        draft_result_1 = await goal_service.generate_goal_plan_draft(
            student=student,
            subject_obj=subject,
            target_score=9.0,
            deadline=test_deadline,
        )

        session_id = draft_result_1["session_id"]
        plan_1 = draft_result_1["plan"]

        print(f"-> Tạo thành công phiên chat MongoDB, Session ID: {session_id}")
        print("Lộ trình nháp lần 1 (AI đề xuất ban đầu):")
        for week_plan in plan_1.weeks:
            print(f"  * Tuần {week_plan.week}:")
            for t in week_plan.tasks:
                print(f"    - {t}")

        # =====================================================================
        # BƯỚC 2: Thảo luận tinh chỉnh (Yêu cầu giảm tải Tuần 1, dồn sang Tuần 2)
        # =====================================================================
        print(
            "\n[Bước 2] Học sinh phản hồi: 'Tuần 1 mình bận thi học kỳ, bạn giảm bớt nhiệm vụ tuần 1 và chuyển bớt sang tuần 2 được không?'..."
        )

        user_feedback = "Tuần 1 mình bận thi học kỳ, bạn giảm bớt nhiệm vụ tuần 1 (chỉ cần 1-2 nhiệm vụ) và chuyển bớt các nhiệm vụ còn lại sang tuần 2 được không?"

        draft_result_2 = await goal_service.generate_goal_plan_draft(
            student=student,
            subject_obj=subject,
            target_score=9.0,
            deadline=test_deadline,
            user_message=user_feedback,
            session_id=session_id,
        )

        plan_2 = draft_result_2["plan"]
        print("Lộ trình nháp lần 2 (Đã được AI điều chỉnh dựa trên lịch sử chat):")
        for week_plan in plan_2.weeks:
            print(f"  * Tuần {week_plan.week}:")
            for t in week_plan.tasks:
                print(f"    - {t}")

        # =====================================================================
        # BƯỚC 3: Xác nhận lưu chính thức lộ trình nháp lần 2 vào MySQL
        # =====================================================================
        print("\n[Bước 3] Xác nhận lưu lộ trình nháp cuối cùng vào MySQL...")
        confirm_result = await goal_service.confirm_goal_plan_draft(
            db=db,
            student=student,
            subject_obj=subject,
            session_id=session_id,
            target_score=9.0,
            deadline=test_deadline,
        )

        print(f"-> Đã tạo StudyGoal ID trong MySQL: {confirm_result['goal'].id}")
        print(f"-> Tổng số plans đã lưu MySQL: {confirm_result['total_plans']} tasks")

        # 5. Truy vấn MySQL kiểm chứng dữ liệu thực tế
        db_plans = (
            db.query(StudyPlan)
            .filter(StudyPlan.goal_id == confirm_result["goal"].id)
            .order_by(StudyPlan.study_date.asc())
            .all()
        )
        print("\n[MySQL Verification] Các nhiệm vụ thực tế được lưu trong study_plans:")
        for p in db_plans:
            print(f"  [{p.study_date}] -> {p.title}")

    except Exception as e:
        print(f"\nERROR: Lỗi trong quá trình chạy test tương tác: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_interactive_test())
