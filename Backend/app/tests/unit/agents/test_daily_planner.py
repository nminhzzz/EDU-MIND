import json
import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from app.agents.roadmap_planner.agent import (
    normalize_roadmap_keys,
    get_manually_busy_dates,
    get_busy_weekdays,
    format_available_schedule,
    generate_unified_plan,
)
from app.schemas.unified_goal import UnifiedGoalPlanResponse
from app.services.unified.validators import prune_roadmap_history

# ── 1. UNIT TESTS: NORMALIZE ROADMAP KEYS ──────────────────────────────────


def test_normalize_roadmap_keys_camel_and_kebab():
    input_data = {
        "weeks": [{"week": 1, "tasks": ["Task 1"]}],
        "daily_schedule": [
            {
                "date": "2026-07-06",
                "startTime": "08:00",
                "end-time": "10:00",
                "taskName": "Learn OOP",
                "desc": "Detail description",
            }
        ],
    }

    expected = {
        "weeks": [{"week": 1, "tasks": ["Task 1"]}],
        "daily_schedule": [
            {
                "date": "2026-07-06",
                "start_time": "08:00",
                "end_time": "10:00",
                "task": "Learn OOP",
                "description": "Detail description",
            }
        ],
    }

    assert normalize_roadmap_keys(input_data) == expected


def test_normalize_roadmap_keys_alternative_fields():
    input_data = {"title": "Short Title", "taskdescription": "Long Desc"}
    expected = {"task": "Short Title", "description": "Long Desc"}
    assert normalize_roadmap_keys(input_data) == expected


# ── 2. UNIT TESTS: GET MANUALLY BUSY DATES ─────────────────────────────────


def test_get_manually_busy_dates_tomorrow_and_day_after():
    current_date = "2026-07-06"  # Monday
    user_message = "Ngày mai em bận đi thi, ngày kia em bận đi ăn cưới"

    busy_dates = get_manually_busy_dates(
        user_message=user_message, history=None, current_date=current_date
    )

    # Tomorrow is 2026-07-07, Day after tomorrow is 2026-07-08
    assert "2026-07-07" in busy_dates
    assert "2026-07-08" in busy_dates


def test_get_manually_busy_dates_vietnamese_pattern():
    current_date = "2026-07-06"
    user_message = "em bận ngày 15/7 và nghỉ ngày 20-7"

    busy_dates = get_manually_busy_dates(
        user_message=user_message, history=None, current_date=current_date
    )

    assert "2026-07-15" in busy_dates
    assert "2026-07-20" in busy_dates


def test_get_manually_busy_dates_range():
    current_date = "2026-07-06"
    user_message = "em bận từ ngày 15/7 đến ngày 18/7"

    busy_dates = get_manually_busy_dates(
        user_message=user_message, history=None, current_date=current_date
    )

    assert "2026-07-15" in busy_dates
    assert "2026-07-16" in busy_dates
    assert "2026-07-17" in busy_dates
    assert "2026-07-18" in busy_dates
    assert "2026-07-19" not in busy_dates


def test_get_manually_busy_dates_year_wrap():
    current_date = "2026-12-25"
    user_message = "em bận ngày 5/1"

    busy_dates = get_manually_busy_dates(
        user_message=user_message, history=None, current_date=current_date
    )

    # Dec 25, 2026 -> 5/1 resolves to Jan 5, 2027
    assert "2027-01-05" in busy_dates


def test_get_busy_weekdays_thursday():
    user_message = "thứ 5 tôi bận đi chơi"
    busy = get_busy_weekdays(user_message=user_message, history=None)
    assert "thu" in busy


def test_get_busy_weekdays_from_history():
    history = [{"role": "user", "content": "thứ 5 tôi bận đi chơi"}]
    busy = get_busy_weekdays(user_message=None, history=history)
    assert "thu" in busy


def test_get_busy_weekdays_accumulates_multiple_refinements():
    history = [
        {"role": "user", "content": "Lập lộ trình Java"},
        {"role": "assistant", "content": "{...}"},
        {"role": "user", "content": "thứ 5 tôi bận đi chơi"},
        {"role": "assistant", "content": "{...}"},
        {"role": "user", "content": "thứ 7 tôi cũng bận"},
    ]
    pruned = prune_roadmap_history(history)
    busy = get_busy_weekdays(user_message=None, history=pruned)
    assert "thu" in busy
    assert "sat" in busy


def test_prune_roadmap_history_keeps_all_user_refinements():
    history = [
        {"role": "user", "content": "Lập lộ trình Java"},
        {"role": "assistant", "content": "draft v1"},
        {"role": "user", "content": "thứ 5 tôi bận"},
        {"role": "assistant", "content": "draft v2"},
        {"role": "user", "content": "thứ 7 cũng bận"},
    ]
    pruned = prune_roadmap_history(history)
    user_contents = [m["content"] for m in pruned if m["role"] == "user"]
    assert user_contents == [
        "Lập lộ trình Java",
        "thứ 5 tôi bận",
        "thứ 7 cũng bận",
    ]
    assert pruned[1]["content"] == "draft v2"


# ── 3. UNIT TESTS: FORMAT AVAILABLE SCHEDULE ───────────────────────────────


def test_format_available_schedule_full_days():
    schedule = {"mon": True, "wed": True}
    result = format_available_schedule(schedule)
    assert "Thứ 2 (Cả ngày)" in result
    assert "Thứ 4 (Cả ngày)" in result


def test_format_available_schedule_slots():
    schedule = {
        "tue": {
            "morning": True,
            "morning_start": "08:00",
            "morning_end": "11:00",
            "evening": True,
        }
    }
    result = format_available_schedule(schedule)
    assert "Thứ 3" in result
    assert "Sáng (08:00-11:00)" in result
    assert "Tối" in result


def test_format_available_schedule_empty():
    assert format_available_schedule(None) == "Linh hoạt tất cả các ngày"
    assert format_available_schedule({}) == "Linh hoạt tất cả các ngày"


# ── 4. INTEGRATION TESTS (MOCKED LLM & DB) ────────────────────────────────


@patch("app.agents.roadmap_planner.agent.generate_content_nvidia")
@patch("app.agents.roadmap_planner.agent.get_student_analytics_db")
@patch("app.agents.roadmap_planner.agent.get_recent_attempts_db")
@patch("app.agents.roadmap_planner.agent.vector_search_materials")
@pytest.mark.asyncio
async def test_generate_unified_plan_success(
    mock_vector_search,
    mock_recent_attempts,
    mock_student_analytics,
    mock_generate_content,
):
    # Mock DB queries
    mock_vector_search.return_value = [
        {"topic": "Java Basics", "content": "OOP inheritance concepts"}
    ]
    mock_student_analytics.return_value = {
        "average_score": 7.5,
        "quizzes_completed": 3,
        "weak_topics": ["Inheritance"],
        "strong_topics": ["Variables"],
        "ai_feedback": "Good progress",
    }
    mock_recent_attempts.return_value = []

    # Mock NVIDIA LLM Response
    mock_llm_json = """
    {
      "weeks": [{"week": 1, "tasks": ["Học về kế thừa"]}],
      "daily_schedule": [
        {"date": "2026-07-06", "start_time": "08:00", "end_time": "10:00", "task": "Học Kế thừa", "description": "Tìm hiểu Java class inheritance"}
      ],
      "curriculum_materials": [],
      "quizzes": []
    }
    """
    mock_generate_content.return_value = mock_llm_json

    result = await generate_unified_plan(
        subject="Java",
        target_score=8.0,
        deadline=date.fromisoformat("2026-07-13"),  # 7 days
        student_id=1,
        subject_id=1,
        study_hours_per_day=2.0,
        preferred_time="morning",
        off_days=["sat", "sun"],
        current_date="2026-07-06",
        available_schedule={
            "mon": True,
            "tue": True,
            "wed": True,
            "thu": True,
            "fri": True,
        },
        history=None,
        db_mongo=None,
    )

    assert isinstance(result, UnifiedGoalPlanResponse)
    assert len(result.weeks) == 1
    assert len(result.daily_schedule) == 1
    assert result.daily_schedule[0].task == "Học Kế thừa"
    assert result.daily_schedule[0].date == "2026-07-06"


@patch("app.agents.roadmap_planner.agent.generate_content_nvidia")
@patch("app.agents.roadmap_planner.agent.get_student_analytics_db")
@patch("app.agents.roadmap_planner.agent.get_recent_attempts_db")
@pytest.mark.asyncio
async def test_generate_unified_plan_excludes_busy_weekday(
    mock_recent_attempts,
    mock_student_analytics,
    mock_generate_content,
):
    mock_student_analytics.return_value = {
        "average_score": 7.0,
        "quizzes_completed": 1,
        "weak_topics": [],
        "strong_topics": [],
        "ai_feedback": "",
    }
    mock_recent_attempts.return_value = []

    tasks = [f"Task {i}" for i in range(1, 8)]
    schedule_items = [
        {
            "date": "2026-07-08",
            "start_time": "18:00",
            "end_time": "20:00",
            "task": task,
            "description": task,
        }
        for task in tasks
    ]
    mock_generate_content.return_value = json.dumps(
        {
            "weeks": [{"week": 1, "tasks": tasks}],
            "daily_schedule": schedule_items,
            "curriculum_materials": [],
            "quizzes": [],
        }
    )

    history = [{"role": "user", "content": "thứ 5 tôi bận đi chơi"}]

    result = await generate_unified_plan(
        subject="Java",
        target_score=8.5,
        deadline=date.fromisoformat("2026-07-29"),
        student_id=1,
        subject_id=1,
        study_hours_per_day=2.0,
        preferred_time="evening",
        off_days=["sat", "sun"],
        current_date="2026-07-08",
        available_schedule=None,
        history=history,
        db_mongo=None,
    )

    for day in result.daily_schedule:
        assert date.fromisoformat(day.date).strftime("%a").lower() != "thu"


@patch("app.agents.roadmap_planner.agent.generate_content_nvidia")
@patch("app.agents.roadmap_planner.agent.get_student_analytics_db")
@patch("app.agents.roadmap_planner.agent.get_recent_attempts_db")
@pytest.mark.asyncio
async def test_generate_unified_plan_constraint_violation(
    mock_recent_attempts,
    mock_student_analytics,
    mock_generate_content,
):
    mock_student_analytics.return_value = {
        "average_score": 5.0,
        "quizzes_completed": 0,
        "weak_topics": [],
        "strong_topics": [],
        "ai_feedback": "",
    }
    mock_recent_attempts.return_value = []

    mock_llm_json = """
    {
      "weeks": [{"week": 1, "tasks": ["Task 1", "Task 2", "Task 3"]}],
      "daily_schedule": [
        {"date": "2026-07-06", "start_time": "08:00", "end_time": "10:00", "task": "Task 1", "description": ""},
        {"date": "2026-07-07", "start_time": "08:00", "end_time": "10:00", "task": "Task 2", "description": ""},
        {"date": "2026-07-08", "start_time": "08:00", "end_time": "10:00", "task": "Task 3", "description": ""}
      ],
      "curriculum_materials": [],
      "quizzes": []
    }
    """
    mock_generate_content.return_value = mock_llm_json

    # off_days chứa tất cả các ngày trong tuần -> Sẽ không tìm thấy ngày trống khả dụng nào
    with pytest.raises(ValueError) as excinfo:
        await generate_unified_plan(
            subject="Java",
            target_score=8.0,
            deadline=date.fromisoformat("2026-07-07"),
            student_id=1,
            subject_id=1,
            study_hours_per_day=2.0,
            preferred_time="morning",
            off_days=["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            current_date="2026-07-06",
            available_schedule={"mon": True},
            history=None,
            db_mongo=None,
        )

    assert "Không tìm thấy đủ ngày học trống trong lịch rảnh của bạn" in str(
        excinfo.value
    )
