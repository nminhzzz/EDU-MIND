import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.api.deps import get_current_student, get_db
from app.models.user import User
from app.models.ai_recommendation_review import AIRecommendationReview

# Tạo TestClient cho FastAPI
client = TestClient(app)


@pytest.fixture
def mock_student():
    student = User(
        id=999,
        email="test_student_rec@edumind.vn",
        full_name="Student Test Rec",
        role="student",
        is_active=True,
    )
    return student


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


# ── 1. TEST GET STUDENT RECOMMENDATIONS ──────────────────────────────────────


@patch("app.api.v1.recommendations.get_student_recommendations")
def test_get_student_recommendations_api(
    mock_get_recommendations, mock_student, mock_db
):
    # Mock kết quả trả về từ service
    rec1 = AIRecommendationReview(
        id=1,
        student_id=999,
        teacher_id=10,
        recommendation="Hãy ôn tập kỹ khái niệm kế thừa lớp cha, lớp con và override phương thức.",
        teacher_feedback="Lưu ý làm thêm bài tập thực hành.",
        status="approved",
        created_at=datetime(2026, 7, 7, 12, 0, 0),
    )

    mock_get_recommendations.return_value = [rec1]

    # Override dependencies
    app.dependency_overrides[get_current_student] = lambda: mock_student
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/recommendations/my-recommendations")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert (
        data[0]["recommendation"]
        == "Hãy ôn tập kỹ khái niệm kế thừa lớp cha, lớp con và override phương thức."
    )
    assert data[0]["status"] == "approved"
    assert data[0]["teacher_feedback"] == "Lưu ý làm thêm bài tập thực hành."

    # Xóa overrides
    app.dependency_overrides.clear()


@patch("app.api.v1.recommendations.get_student_recommendations")
def test_get_student_recommendations_forbidden_for_teacher(
    mock_get_recommendations, mock_db
):
    # Giáo viên truy cập vào API của học sinh -> Phải bị chặn (HTTP 403 Forbidden)
    mock_teacher = User(
        id=10, email="teacher@edumind.vn", role="teacher", is_active=True
    )

    app.dependency_overrides[get_current_student] = (
        None  # Giả lập dependency injection thất bại / ném lỗi
    )
    app.dependency_overrides[get_db] = lambda: mock_db

    # Ở đây get_current_student trong auth sẽ ném lỗi 403 Forbidden nếu role là teacher
    # Nhưng vì ta override, cách tốt nhất là test trực tiếp với user có role teacher
    # FastAPI's dependency injection của get_current_student:
    # def get_current_student(current_user: User = Depends(get_current_user)):
    #     if current_user.role not in ("student", "admin"): raise HTTPException(403)

    from app.api.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_teacher
    # Xóa override get_current_student để nó chạy qua hàm kiểm duyệt role thật
    if get_current_student in app.dependency_overrides:
        del app.dependency_overrides[get_current_student]

    response = client.get("/api/v1/recommendations/my-recommendations")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    app.dependency_overrides.clear()
