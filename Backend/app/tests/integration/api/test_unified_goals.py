from datetime import date
from unittest.mock import MagicMock, patch

from fastapi import status

from app.api.deps import get_current_student, get_db
from app.database.redis import get_redis
from app.main import app

# ── 1. TEST RATE LIMITING ───────────────────────────────────────────────────


@patch("app.api.v1.unified_goals.generate_unified_draft")
def test_rate_limiting_on_draft_api(
    mock_generate_draft, test_client, mock_student, mock_db
):
    mock_generate_draft.return_value = {
        "plan": {
            "weeks": [],
            "daily_schedule": [],
            "curriculum_materials": [],
            "quizzes": [],
        },
    }

    app.dependency_overrides[get_current_student] = lambda: mock_student
    app.dependency_overrides[get_db] = lambda: mock_db

    request_payload = {
        "subject_id": 1,
        "target_score": 8.5,
        "deadline": str(date(2026, 8, 30)),
        "available_schedule": {},
    }

    for _ in range(5):
        response = test_client.post("/api/v1/goals/unified/draft", json=request_payload)
        assert response.status_code == status.HTTP_200_OK

    response = test_client.post("/api/v1/goals/unified/draft", json=request_payload)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Tần suất gọi quá nhanh" in response.json()["detail"]


# ── 2. TEST IDEMPOTENCY LOCK ───────────────────────────────────────────────


@patch("app.api.v1.unified_goals.confirm_unified_draft")
def test_idempotency_lock_on_confirm_api(
    mock_confirm_draft, test_client, mock_student, mock_db
):
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
        "subject_id": 1,
        "target_score": 8.5,
        "deadline": str(date(2026, 8, 30)),
        "available_schedule": {},
        "plan": {
            "weeks": [],
            "daily_schedule": [],
            "curriculum_materials": [],
            "quizzes": [],
        },
    }

    response = test_client.post("/api/v1/goals/unified/confirm", json=request_payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["total_plans"] == 10

    redis_client = get_redis()
    redis_client.set(f"lock:confirm:{mock_student.id}:1", "locked", ex=10)

    response = test_client.post("/api/v1/goals/unified/confirm", json=request_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Yêu cầu xác nhận lộ trình đang được xử lý" in response.json()["detail"]
