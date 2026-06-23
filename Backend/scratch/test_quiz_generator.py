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

from app.agents.quiz_generator.agent import generate_quiz

def test_quiz_generator():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("--- Khởi chạy Quiz Generator Agent (Gemini) ---")
    subject = "Triết học Mác - Lênin"
    topic = "Vật chất và ý thức (Chương 2)"
    difficulty = "medium"
    total_questions = 3
    question_type = "mcq"

    print(f"Môn học: {subject}")
    print(f"Chủ đề: {topic}")
    print(f"Độ khó: {difficulty}")
    print(f"Số lượng câu hỏi: {total_questions}")
    print(f"Loại: {question_type}")
    print("\nAI đang soạn đề thi kiểm tra, vui lòng đợi...")

    try:
        quiz = generate_quiz(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
            question_type=question_type
        )
        print("\n=== ĐỀ THI DO AI SOẠN THẢO (JSON THỰC TẾ) ===")
        print(json.dumps(quiz.model_dump(), indent=2, ensure_ascii=False))
        print("\nSUCCESS: Đề thi đã được tạo và validate thành công với Pydantic schema!")
    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi khi chạy Agent: {e}")

if __name__ == "__main__":
    test_quiz_generator()
