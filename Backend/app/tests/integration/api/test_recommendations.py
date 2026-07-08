from datetime import datetime
from unittest.mock import patch

from fastapi import status

from app.api.deps import get_current_student, get_current_user, get_db
from app.main import app
from app.models.ai_recommendation_review import AIRecommendationReview

# ── 1. TEST GET STUDENT RECOMMENDATIONS ──────────────────────────────────────


@patch("app.api.v1.recommendations.get_student_recommendations")
def test_get_student_recommendations_api(
    mock_get_recommendations, test_client, mock_student, mock_db
):
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

    app.dependency_overrides[get_current_student] = lambda: mock_student
    app.dependency_overrides[get_db] = lambda: mock_db

    response = test_client.get("/api/v1/recommendations/my-recommendations")

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


@patch("app.api.v1.recommendations.get_student_recommendations")
def test_get_student_recommendations_forbidden_for_teacher(
    mock_get_recommendations, test_client, mock_teacher, mock_db
):
    app.dependency_overrides[get_current_user] = lambda: mock_teacher
    app.dependency_overrides[get_db] = lambda: mock_db
    if get_current_student in app.dependency_overrides:
        del app.dependency_overrides[get_current_student]

    response = test_client.get("/api/v1/recommendations/my-recommendations")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    mock_get_recommendations.assert_not_called()
