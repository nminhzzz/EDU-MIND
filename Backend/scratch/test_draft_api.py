from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_draft():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "student_test@edumind.com", "password": "studentpassword"},
    )
    print(f"Login response status: {login_res.status_code}")
    if login_res.status_code != 200:
        print("Login failed!")
        print(login_res.text)
        return

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. CALLING /goals/unified/draft ---")
    payload = {
        "subject_id": 1,
        "target_score": 9,
        "deadline": "2026-08-18",
        "user_message": "Tập trung nhiều bài kiểm tra, giảm giờ học tuần đầu, tôi yếu lập trình hướng đối tượng...",
    }

    try:
        res = client.post("/api/v1/goals/unified/draft", json=payload, headers=headers)
        print(f"Response status: {res.status_code}")
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_draft()
