import sys
import os
from datetime import datetime, date, timedelta

# Thêm Backend vào sys.path để import được app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env thủ công để thiết lập biến môi trường (chỉ set nếu chưa tồn tại)
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

from sqlalchemy import create_engine
from app.database.mysql import engine, SessionLocal
from app.models.base import Base

# Import các models để SQLAlchemy tạo bảng trong MySQL
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.notification import Notification

import app.services.goal_service as goal_service

def run_mysql_test():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("--- KHỞI CHẠY KIỂM THỬ TÍCH HỢP AI & DATABASE MYSQL THỰC TẾ ---")
    
    # 1. Tạo các bảng trong MySQL (Nếu chưa tồn tại)
    try:
        print("Đang kết nối tới MySQL và đồng bộ cấu trúc bảng...")
        Base.metadata.create_all(bind=engine)
        print("Đồng bộ cấu trúc bảng thành công!")
    except Exception as e:
        print(f"\nERROR: Không thể kết nối tới MySQL hoặc tạo bảng: {e}")
        print("Vui lòng kiểm tra lại cấu hình DATABASE_URL trong file .env và chắc chắn MySQL đã hoạt động.")
        return

    db = SessionLocal()
    try:
        # 2. Tạo học sinh giả lập trong MySQL (Để MySQL tự sinh khóa chính)
        student = db.query(User).filter(User.email == "student_mysql@test.com").first()
        if not student:
            student = User(
                email="student_mysql@test.com",
                password_hash="hashedpassword123",
                full_name="Nguyễn Văn A (MySQL)",
                role="student",
                grade="Đại học năm 1",
                learning_level="average"
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"Đã tạo học sinh mới trong MySQL, ID: {student.id}")
        else:
            print(f"Học sinh đã tồn tại trong MySQL, ID: {student.id}")

        # 3. Tạo môn học giả lập
        subject = db.query(Subject).filter(Subject.code == "TRIETHOC_MYSQL").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin",
                code="TRIETHOC_MYSQL",
                description="Môn học Triết học cơ bản"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)
            print(f"Đã tạo môn học mới trong MySQL, ID: {subject.id}")
        else:
            print(f"Môn học đã tồn tại trong MySQL, ID: {subject.id}")

        # 3.1 Tạo dữ liệu học lực mẫu (Learning Analytics) môn Triết học để kiểm thử AI Agent Tool Calling
        analytic = db.query(LearningAnalytic).filter(
            LearningAnalytic.student_id == student.id,
            LearningAnalytic.subject_id == subject.id
        ).first()
        if not analytic:
            analytic = LearningAnalytic(
                student_id=student.id,
                subject_id=subject.id,
                average_score=4.5,
                quizzes_completed=3,
                weak_topics=["Vật chất", "Ý thức"],
                strong_topics=["Khái quát lịch sử Triết học"],
                ai_feedback="Học lực trung bình yếu. Cần ôn tập kỹ các phạm trù Vật chất và Ý thức."
            )
            db.add(analytic)
            db.commit()
            db.refresh(analytic)
            print(f"Đã tạo dữ liệu học lực mẫu (Learning Analytics) trong MySQL, ID: {analytic.id}")
        else:
            analytic.average_score = 4.5
            analytic.weak_topics = ["Vật chất", "Ý thức"]
            analytic.strong_topics = ["Khái quát lịch sử Triết học"]
            db.commit()
            print("Đã đồng bộ dữ liệu học lực mẫu của học sinh (Điểm TB: 4.5, Phần yếu: Vật chất, Ý thức).")

        # Đặt hạn chót cách hôm nay 2 tuần để AI lập lịch ngắn gọn
        test_deadline = (date.today() + timedelta(days=14)).strftime("%Y-%m-%d")

        print(f"\nAI đang lập lộ trình học môn '{subject.name}' cho học sinh '{student.full_name}'...")
        print(f"Mục tiêu: 9.0 điểm | Hạn chót: {test_deadline}")
        
        # 4. Kích hoạt Service điều phối AI
        test_deadline_date = datetime.strptime(test_deadline, "%Y-%m-%d").date()
        result = goal_service.create_goal_and_schedule_plans(
            db=db,
            student=student,
            subject_obj=subject,
            target_score=9.0,
            deadline=test_deadline_date
        )

        print("\n=======================================================")
        print("   🎉 KẾT QUẢ TÍCH HỢP THÀNH CÔNG (DỮ LIỆU ĐÃ LƯU MYSQL)  ")
        print("=======================================================")
        print(f"1. Đã lưu StudyGoal ID vào MySQL: {result['goal'].id}")
        print(f"2. Điểm số mục tiêu: {result['goal'].target_score}")
        print(f"3. Lộ trình được chia làm: {result['total_weeks']} tuần")
        print(f"4. Tổng số lịch học ngày được lưu vào MySQL: {len(result['plans'])} tasks")
        
        # Truy vấn kiểm tra lại dữ liệu trong MySQL để xác thực
        db_goal = db.query(StudyGoal).filter(StudyGoal.id == result['goal'].id).first()
        db_plans = db.query(StudyPlan).filter(StudyPlan.goal_id == db_goal.id).all()
        
        print(f"\n[MySQL Query] Dữ liệu thực tế vừa lưu trong bảng study_plans:")
        for i, plan in enumerate(db_plans, 1):
            print(f"  Task {i}: [{plan.study_date}] ({plan.start_time} - {plan.end_time}) -> {plan.title}")
            print(f"          Mô tả: {plan.task_description}")
            print("-" * 60)

    except Exception as e:
        print(f"\nERROR: Lỗi trong quá trình chạy test tích hợp MySQL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_mysql_test()
