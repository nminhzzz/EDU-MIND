"""Repository for student preference records."""

from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.student_preference import StudentPreference
from app.repositories.base import BaseRepository


class StudentPreferenceRepository(
    BaseRepository[StudentPreference, BaseModel, BaseModel]
):
    """Data access for the student_preferences table."""

    def get_by_student(
        self, db: Session, student_id: int
    ) -> Optional[StudentPreference]:
        """Return preferences for a student, if configured."""
        return (
            db.query(StudentPreference)
            .filter(StudentPreference.student_id == student_id)
            .first()
        )

    def upsert(
        self,
        db: Session,
        *,
        student_id: int,
        study_hours_per_day: int,
        preferred_study_time: str,
        available_schedule: dict,
    ) -> StudentPreference:
        """Create or update a student's preferences in the current session (no commit)."""
        pref = self.get_by_student(db, student_id)
        if not pref:
            pref = StudentPreference(
                student_id=student_id,
                study_hours_per_day=study_hours_per_day,
                preferred_study_time=preferred_study_time,
                available_schedule=available_schedule,
            )
            db.add(pref)
            return pref

        pref.study_hours_per_day = study_hours_per_day
        pref.preferred_study_time = preferred_study_time
        pref.available_schedule = available_schedule
        return pref


student_preference_repository = StudentPreferenceRepository(StudentPreference)
