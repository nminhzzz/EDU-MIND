import sys
import os
import json

# Thêm Backend vào sys.path để có thể import thư mục app
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

from app.agents.daily_planner.agent import generate_daily_plan

def test_daily_planner():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("--- Khởi chạy Daily Study Planner Agent (Gemini) ---")
    
    # Giả lập tham số lập lịch
    weekly_tasks = [
        "Học chương 1: Khái luận về Triết học Mác - Lênin",
        "Làm Quiz trắc nghiệm ôn tập chương 1",
        "Đọc trước chương 2: Bản chất của thế giới quan và phương pháp luận"
    ]
    subject = "Triết học Mác - Lênin"
    target_score = 8.5
    days_left = 30
    study_hours_per_day = 2.0
    preferred_time = "buổi tối"
    off_days = ["Chủ nhật"]
    current_date = "2026-06-22"

    print(f"Môn học: {subject}")
    print(f"Nhiệm vụ tuần: {weekly_tasks}")
    print(f"Học: {study_hours_per_day} giờ/ngày")
    print(f"Khung giờ: {preferred_time}")
    print(f"Ngày nghỉ: {off_days}")
    print("\nAI đang phân chia lịch học chi tiết từng ngày, vui lòng đợi...")

    try:
        plan = generate_daily_plan(
            subject=subject,
            target_score=target_score,
            days_left=days_left,
            weekly_plans_list=weekly_tasks,
            study_hours_per_day=study_hours_per_day,
            preferred_time=preferred_time,
            off_days=off_days,
            current_date=current_date
        )
        print("\n=== THỜI KHÓA BIỂU CHI TIẾT TỪNG NGÀY (JSON THỰC TẾ) ===")
        print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))
        print("\nSUCCESS: Thời khóa biểu đã được lập và validate thành công với Pydantic schema!")
    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi khi chạy Agent: {e}")

if __name__ == "__main__":
    test_daily_planner()
