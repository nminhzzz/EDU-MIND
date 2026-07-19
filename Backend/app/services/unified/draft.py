"""
Unified goal draft generation — AI roadmap planning.
"""

from datetime import date
from typing import Any, Dict

from fastapi import HTTPException, status

from app.agents.roadmap_planner import generate_unified_plan
from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db
from app.models.subject import Subject
from app.models.user import User
from app.services.unified.validators import load_student_preferences

logger = get_logger(__name__)


async def generate_unified_draft(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
) -> Dict[str, Any]:
    """
    Sinh lộ trình hợp nhất.
    """
    db_mongo = get_mongodb_db()

    study_hours_per_day, preferred_time_vn, off_days, available_schedule = (
        load_student_preferences(student.id)
    )

    current_date = date.today().strftime("%Y-%m-%d")
    try:
        plan = await generate_unified_plan(
            subject=subject_obj.name,
            target_score=target_score,
            deadline=deadline,
            student_id=student.id,
            subject_id=subject_obj.id,
            study_hours_per_day=study_hours_per_day,
            preferred_time=preferred_time_vn,
            off_days=off_days,
            current_date=current_date,
            available_schedule=available_schedule,
            db_mongo=db_mongo,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    return {"plan": plan}
