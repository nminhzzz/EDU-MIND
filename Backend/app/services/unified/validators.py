"""
Validation helpers and shared utilities for the unified goal workflow.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.database.mysql import SessionLocal
from app.models.study_goal import StudyGoal
from app.repositories.goal_repository import goal_repository
from app.repositories.student_preference_repository import student_preference_repository

TIME_MAP: Dict[str, str] = {
    "morning": "buổi sáng",
    "afternoon": "buổi chiều",
    "evening": "buổi tối",
}


def validate_goal_deadline(subject_name: str, target_score: float, deadline: date) -> None:
    """
    Raise ValueError when the deadline or target score is infeasible.
    Call this before creating or updating a study goal.
    """
    today = date.today()
    if deadline < today:
        raise ValueError("Hạn chót không được nằm trong quá khứ.")

    days_left = (deadline - today).days
    if days_left < 3:
        raise ValueError(
            f"Hạn chót quá ngắn! Lộ trình học tập cho môn '{subject_name}' cần tối thiểu 3 ngày. "
            "Vui lòng lùi ngày hạn chót xa hơn."
        )

    if target_score >= 8.0 and days_left < 5:
        raise ValueError(
            f"Mục tiêu điểm số quá cao ({target_score}/10) cho khoảng thời gian học quá ngắn "
            f"({days_left} ngày). Vui lòng lùi hạn chót (tối thiểu 5 ngày) hoặc giảm điểm mục tiêu."
        )


def load_student_preferences(student_id: int) -> Tuple[float, str, List[str], Any]:
    """
    Load StudentPreference for the given student from MySQL and derive:
    - study_hours_per_day
    - preferred_time (Vietnamese label)
    - off_days (list of day-of-week keys with no availability)
    - available_schedule (raw dict or None)

    Opens its own short-lived session via context manager to avoid leaking
    the caller's session or creating unmanaged sessions.
    """
    with SessionLocal() as db:
        pref = student_preference_repository.get_by_student(db, student_id)

    study_hours_per_day = 2.0
    preferred_time_key = "evening"
    off_days: List[str] = ["sun"]
    available_schedule = None

    if pref:
        study_hours_per_day = float(pref.study_hours_per_day or 2.0)
        preferred_time_key = pref.preferred_study_time or "evening"
        available_schedule = pref.available_schedule

        if available_schedule:
            off_days = [
                day
                for day, slots in available_schedule.items()
                if not (
                    any(slots.get(s) for s in ("morning", "afternoon", "evening"))
                    if isinstance(slots, dict)
                    else bool(slots)
                )
            ]

    preferred_time_vn = TIME_MAP.get(preferred_time_key, "buổi tối")
    return study_hours_per_day, preferred_time_vn, off_days, available_schedule


def get_active_goal_for_subject(
    db: Session, student_id: int, subject_id: int
) -> Optional[StudyGoal]:
    """Backward-compatible wrapper — delegates to goal_repository."""
    return goal_repository.get_active_for_subject(db, student_id, subject_id)
