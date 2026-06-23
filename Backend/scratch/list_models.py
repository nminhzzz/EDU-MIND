import sys
import os

# Thêm Backend vào sys.path
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

from google import genai

def list_gemini_models():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Chưa thiết lập GEMINI_API_KEY trong .env")
        return

    print("--- Đang kết nối Gemini để kiểm tra danh sách model khả dụng... ---")
    try:
        client = genai.Client(api_key=gemini_key)
        # Sử dụng API mới của google-genai để list models
        response = client.models.list()
        print("\nCác model khả dụng cho API Key của bạn:")
        for model in response:
            print(f"- {model.name}")
    except Exception as e:
        print(f"Lỗi khi liệt kê model: {e}")

if __name__ == "__main__":
    list_gemini_models()
