"""
Student preference use cases.
"""

from sqlalchemy.orm import Session

from app.database.unit_of_work import commit_or_rollback
from app.models.student_preference import StudentPreference
from app.repositories.student_preference_repository import student_preference_repository
from app.schemas.student_preference import StudentPreferenceBase


def get_student_preferences(db: Session, student_id: int) -> StudentPreference:
    """Return preferences for a student."""
    pref = student_preference_repository.get_by_student(db, student_id)
    if not pref:
        raise ValueError(
            "Học sinh chưa cấu hình lịch học và thời gian học ưa thích."
        )
    return pref


def upsert_student_preferences(
    db: Session, student_id: int, body: StudentPreferenceBase
) -> StudentPreference:
    """Create or update a student's schedule preferences."""
    pref = student_preference_repository.upsert(
        db,
        student_id=student_id,
        study_hours_per_day=body.study_hours_per_day,
        preferred_study_time=body.preferred_study_time.value,
        available_schedule=body.available_schedule,
    )
    commit_or_rollback(db)
    db.refresh(pref)
    return pref
