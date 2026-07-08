from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import GoalStatus
from app.models.study_goal import StudyGoal
from app.repositories.base import BaseRepository
from app.schemas.study_goal import StudyGoalCreate, StudyGoalUpdate


class GoalRepository(BaseRepository[StudyGoal, StudyGoalCreate, StudyGoalUpdate]):
    """Repository for the study_goals table."""

    def list_by_student(self, db: Session, student_id: int) -> List[StudyGoal]:
        """Return all goals for a student, most recent first."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.student_id == student_id)
            .order_by(StudyGoal.created_at.desc())
            .all()
        )

    def get_for_student(
        self, db: Session, goal_id: int, student_id: int
    ) -> Optional[StudyGoal]:
        """Return a goal owned by the student, or None."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.id == goal_id, StudyGoal.student_id == student_id)
            .first()
        )

    def get_active_for_subject(
        self, db: Session, student_id: int, subject_id: int
    ) -> Optional[StudyGoal]:
        """
        Return the most recently created active goal for a student's subject,
        or None if no active goal exists.
        """
        return (
            db.query(StudyGoal)
            .filter(
                StudyGoal.student_id == student_id,
                StudyGoal.subject_id == subject_id,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .order_by(StudyGoal.created_at.desc())
            .first()
        )

    def count_active(self, db: Session) -> int:
        """Return the number of active study goals."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.status == GoalStatus.ACTIVE)
            .count()
        )

    def count_active_for_student(self, db: Session, student_id: int) -> int:
        """Return the number of active study goals for a student."""
        return (
            db.query(StudyGoal)
            .filter(
                StudyGoal.student_id == student_id,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .count()
        )

    def cancel_active_for_subject(
        self, db: Session, student_id: int, subject_id: int
    ) -> None:
        """Mark all active goals for a student's subject as cancelled (no commit)."""
        db.query(StudyGoal).filter(
            StudyGoal.student_id == student_id,
            StudyGoal.subject_id == subject_id,
            StudyGoal.status == GoalStatus.ACTIVE,
        ).update({StudyGoal.status: GoalStatus.CANCELLED}, synchronize_session=False)

    def get_latest_for_student(
        self, db: Session, student_id: int
    ) -> Optional[StudyGoal]:
        """Return the most recently created goal for a student."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.student_id == student_id)
            .order_by(StudyGoal.created_at.desc())
            .first()
        )

    def count_for_student(self, db: Session, student_id: int) -> int:
        """Return the total number of study goals for a student."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.student_id == student_id)
            .count()
        )

    def count_completed_for_student(self, db: Session, student_id: int) -> int:
        """Return the number of completed study goals for a student."""
        return (
            db.query(StudyGoal)
            .filter(
                StudyGoal.student_id == student_id,
                StudyGoal.status == GoalStatus.COMPLETED,
            )
            .count()
        )


goal_repository = GoalRepository(StudyGoal)
