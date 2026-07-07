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

from app.agents.goal_planner.agent import generate_goal_plan


def test_goal_planner():
    # Kiểm tra xem API Key đã được thiết lập chưa
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if (
        not gemini_key
        or gemini_key == "your_gemini_api_key_here"
        or gemini_key.strip() == ""
    ):
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        print(
            "Vui lòng điền API Key thực tế của bạn vào file .env và chạy lại script này."
        )
        return

    print("--- Khởi chạy Goal Planner Agent (Gemini) ---")
    subject = "Triết học Mác - Lênin"
    target_score = 8.5
    current_level = "Trung bình"
    deadline = "2026-08-20"

    print(f"Môn học: {subject}")
    print(f"Điểm mục tiêu: {target_score}")
    print(f"Học lực hiện tại: {current_level}")
    print(f"Hạn chót: {deadline}")
    print("\nAI đang thiết lập lộ trình học tập, vui lòng đợi...")

    try:
        from datetime import datetime

        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()

        plan = generate_goal_plan(
            subject=subject,
            target_score=target_score,
            current_level=current_level,
            deadline=deadline_date,
        )
        print("\n=== LỘ TRÌNH HỌC TẬP DO AI TẠO RA (JSON THỰC TẾ) ===")
        # In đẹp JSON kết quả
        print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))
        print(
            "\nSUCCESS: Lộ trình đã được tạo và validate thành công với Pydantic schema!"
        )
    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi khi chạy Agent: {e}")


if __name__ == "__main__":
    test_goal_planner()
