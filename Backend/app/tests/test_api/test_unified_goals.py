import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.api.deps import get_current_student, get_db
from app.models.user import User
from app.models.subject import Subject
from app.database.redis import get_redis_client

# Tạo TestClient cho FastAPI app
client = TestClient(app)

# ── Mock Objects ───────────────────────────────────────────────────────────


@pytest.fixture
def mock_student():
    student = User(
        id=999,
        email="test_student@edumind.vn",
        full_name="Student Test Limit",
        role="student",
        is_active=True,
    )
    return student


@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mock Subject Query
    subject = Subject(id=1, name="Java Programming")
    db.query().filter().first.return_value = subject
    return db


# ── CLEANUP REDIS FOR TEST ──────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clean_redis():
    redis_client = get_redis_client()
    # Xóa các key test rate limit và lock trước và sau mỗi test
    redis_client.delete("rate_limit:draft:999")
    redis_client.delete("lock:confirm:test_session_id_123")
    yield
    redis_client.delete("rate_limit:draft:999")
    redis_client.delete("lock:confirm:test_session_id_123")


# ── 1. TEST RATE LIMITING ───────────────────────────────────────────────────


@patch("app.api.v1.unified_goals_api.generate_unified_draft")
def test_rate_limiting_on_draft_api(mock_generate_draft, mock_student, mock_db):
    # Mock kết quả generate_unified_draft thành công
    mock_generate_draft.return_value = {
        "session_id": "test_session_id_123",
        "plan": {
            "weeks": [],
            "daily_schedule": [],
            "curriculum_materials": [],
            "quizzes": [],
        },
    }

    # Override dependencies
    app.dependency_overrides[get_current_student] = lambda: mock_student
    app.dependency_overrides[get_db] = lambda: mock_db

    request_payload = {
        "subject_id": 1,
        "target_score": 8.5,
        "deadline": str(date(2026, 8, 30)),
        "available_schedule": {},
    }

    # Gọi 5 lần đầu phải thành công (trả về status 200)
    for i in range(5):
        response = client.post("/api/v1/goals/unified/draft", json=request_payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["session_id"] == "test_session_id_123"

    # Gọi lần thứ 6 phải bị chặn bởi Rate Limiter (trả về status 429)
    response = client.post("/api/v1/goals/unified/draft", json=request_payload)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Tần suất tạo lộ trình quá nhanh" in response.json()["detail"]

    # Xóa overrides
    app.dependency_overrides.clear()


# ── 2. TEST IDEMPOTENCY LOCK ───────────────────────────────────────────────


@patch("app.api.v1.unified_goals_api.confirm_unified_draft")
def test_idempotency_lock_on_confirm_api(mock_confirm_draft, mock_student, mock_db):
    # Mock kết quả confirm thành công
    mock_goal = MagicMock()
    mock_goal.id = 100
    mock_goal.title = "Lộ trình Java"
    mock_goal.subject_id = 1
    mock_goal.target_score = 8.5
    mock_goal.deadline = date(2026, 8, 30)
    mock_goal.status = "active"
    mock_goal.created_at = "2026-07-06T12:00:00"

    mock_confirm_draft.return_value = {
        "goal": mock_goal,
        "total_plans": 10,
        "total_quizzes": 2,
    }

    app.dependency_overrides[get_current_student] = lambda: mock_student
    app.dependency_overrides[get_db] = lambda: mock_db

    request_payload = {
        "session_id": "test_session_id_123",
        "subject_id": 1,
        "target_score": 8.5,
        "deadline": str(date(2026, 8, 30)),
        "available_schedule": {},
    }

    # Lần đầu tiên confirm thành công (chương trình chạy, khóa được tạo và tự động xóa ở finally)
    response = client.post("/api/v1/goals/unified/confirm", json=request_payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["total_plans"] == 10

    # Giả lập tình huống khóa đang bị giữ (ví dụ request 1 đang chạy dở chưa giải phóng)
    redis_client = get_redis_client()
    redis_client.set("lock:confirm:test_session_id_123", "locked", ex=10)

    # Gửi request thứ 2 song song lúc khóa đang giữ -> Phải trả về status 400 chặn trùng lặp
    response = client.post("/api/v1/goals/unified/confirm", json=request_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Yêu cầu xác nhận lộ trình đang được xử lý" in response.json()["detail"]

    # Xóa overrides
    app.dependency_overrides.clear()
