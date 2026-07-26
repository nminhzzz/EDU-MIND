import json
from unittest.mock import patch
import pytest

from app.agents.analytics.agent import evaluate_learning_performance
from app.agents.analytics.schemas import LearningAnalyticsResponse


@patch("app.agents.analytics.agent.generate_content_deepseek")
def test_evaluate_learning_performance_success(mock_generate):
    mock_analytics_json = {
        "weak_topics": [
            {"topic": "Kế thừa trong Java", "score": 4.0},
            {"topic": "Ngoại lệ Exception", "score": 4.5},
        ],
        "strong_topics": [
            {"topic": "Cú pháp cơ bản", "score": 9.0},
            {"topic": "Mảng 1 chiều", "score": 8.5},
        ],
        "learning_trend": "improving",
        "ai_feedback": "Học sinh nắm vững cú pháp cơ bản nhưng cần luyện tập thêm phần Kế thừa.",
    }
    mock_generate.return_value = json.dumps(mock_analytics_json)

    attempts_history = [
        {
            "topic": "OOP Java",
            "score": 6.0,
            "is_passed": False,
            "ai_assessment": {
                "strengths": ["Cú pháp"],
                "weaknesses": ["Kế thừa"],
            },
        },
        {
            "topic": "Exception Handling",
            "score": 8.0,
            "is_passed": True,
            "ai_assessment": {
                "strengths": ["Mảng 1 chiều"],
                "weaknesses": ["Ngoại lệ Exception"],
            },
        },
    ]

    result = evaluate_learning_performance(
        subject_name="Lập trình Java",
        attempts_history=attempts_history,
    )

    assert isinstance(result, LearningAnalyticsResponse)
    assert result.weak_topics[0].topic == "Kế thừa trong Java"
    assert result.weak_topics[0].score == 4.0
    assert result.strong_topics[0].topic == "Cú pháp cơ bản"
    assert result.learning_trend == "improving"
    assert "luyện tập thêm" in result.ai_feedback
    mock_generate.assert_called_once()
