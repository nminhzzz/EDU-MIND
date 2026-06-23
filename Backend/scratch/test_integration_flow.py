import sys
import os
from datetime import datetime, date, timedelta

# Thêm Backend vào sys.path để import được app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env thủ công
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

# Cấu hình SQLite local để chạy test độc lập không cần bật MySQL server
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger

@compiles(BigInteger, "sqlite")
def compile_bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"

db_file = os.path.join(os.path.dirname(__file__), "test_db.sqlite")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file}"

engine_sqlite = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite)

# Override SessionLocal của MySQL bằng SQLite cho việc chạy test này
import app.services.goal_service as goal_service
# Trỏ SessionLocal trong file repository về SessionLocalTest của SQLite
import app.repositories.base as repo_base
import app.database.mysql as db_mysql

# Import các models để Sqlite tạo bảng
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz

# Tạo tất cả các bảng trong SQLite
Base.metadata.create_all(bind=engine_sqlite)

def run_integration_test():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("--- KHỞI CHẠY KIỂM THỬ TÍCH HỢP AI & DATABASE (SQLITE LOCAL) ---")
    
    db = SessionLocalTest()
    try:
        # 1. Tạo dữ liệu giả lập User (Học sinh) & Subject (Môn học) trước để thỏa mãn khóa ngoại
        student = db.query(User).filter(User.email == "student@test.com").first()
        if not student:
            student = User(
                id=1,
                email="student@test.com",
                password_hash="mockhash",
                full_name="Nguyễn Văn A",
                role="student",
                grade="Đại học năm 1",
                learning_level="average"
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        subject = db.query(Subject).filter(Subject.code == "TRIETHOC01").first()
        if not subject:
            subject = Subject(
                id=1,
                name="Triết học Mác - Lênin",
                code="TRIETHOC01",
                description="Môn học Triết học cơ bản"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)

        # Thiết lập deadline cách ngày hôm nay đúng 2 tuần (để lộ trình ngắn gọn, tiết kiệm token khi test)
        test_deadline = (date.today() + timedelta(days=14)).strftime("%Y-%m-%d")

        print(f"Khởi tạo lộ trình học 2 tuần cho Học sinh: {student.full_name}")
        print(f"Môn học: {subject.name} - Hạn chót: {test_deadline}")
        print("\nĐang gọi AI lên lộ trình và lưu vào Database...")

        # 2. Gọi Service xử lý chính
        result = goal_service.create_goal_and_schedule_plans(
            db=db,
            student_id=student.id,
            subject_id=subject.id,
            subject_name=subject.name,
            target_score=9.0,
            deadline=test_deadline,
            current_level=student.learning_level
        )

        print("\n=======================================================")
        print("   🎉 KẾT QUẢ TÍCH HỢP THÀNH CÔNG (DỮ LIỆU ĐÃ LƯU DB)  ")
        print("=======================================================")
        print(f"1. Đã lưu StudyGoal ID: {result['goal_id']}")
        print(f"2. Mục tiêu điểm: {result['target_score']}")
        print(f"3. Tổng số tuần AI tính toán: {result['total_weeks']} tuần")
        print(f"4. Tổng số nhiệm vụ ngày đã lưu vào study_plans: {result['total_tasks_scheduled']} tasks")
        
        # 3. Truy vấn trực tiếp từ SQLite xem dữ liệu có thực sự được lưu không
        db_goal = db.query(StudyGoal).filter(StudyGoal.id == result['goal_id']).first()
        print(f"\n[Database Query] Kiểm tra bảng study_goals:")
        print(f"  - Title: {db_goal.title}")
        print(f"  - Target Score: {db_goal.target_score}")
        print(f"  - Deadline: {db_goal.deadline}")
        
        db_plans = db.query(StudyPlan).filter(StudyPlan.goal_id == db_goal.id).all()
        print(f"\n[Database Query] Kiểm tra bảng study_plans (Lịch học chi tiết từng ngày):")
        for i, plan in enumerate(db_plans, 1):
            print(f"  Task {i}: [{plan.study_date}] ({plan.start_time} - {plan.end_time}) -> {plan.title}")
            print(f"          Mô tả: {plan.task_description}")
            print(f"          AI sinh: {plan.ai_generated} | Trạng thái: {plan.status}")
            print("-" * 60)

    except Exception as e:
        print(f"\nERROR: Lỗi tích hợp: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_integration_test()
