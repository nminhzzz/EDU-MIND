import sys
import os

# Thêm Backend vào sys.path để có thể import app
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

from app.agents.chat_tutor.agent import chat_with_tutor

def main():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("==================================================")
    print("   🤖 CHÀO MỪNG BẠN ĐẾN VỚI GIA SƯ ẢO HỌC TẬP 🤖   ")
    print("      (Nhập 'exit' hoặc 'quit' để thoát)          ")
    print("==================================================")
    
    history = []
    while True:
        try:
            # Nhập câu hỏi từ bàn phím
            user_input = input("\nBạn: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("\nGia sư: Tạm biệt bạn! Chúc bạn học tập tốt.")
                break
                
            if not user_input.strip():
                continue
                
            print("Gia sư đang suy nghĩ...")
            
            # Gọi Agent xử lý kèm theo lịch sử trò chuyện (history)
            reply, history = chat_with_tutor(user_input, history)
            
            print(f"\nGia sư: {reply}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"\nĐã xảy ra lỗi: {e}")

if __name__ == "__main__":
    main()
