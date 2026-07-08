from datetime import date, time
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.core.enums import GoalStatus, PlanStatus
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.study_plan_progress import StudyPlanProgress
from app.repositories.base import BaseRepository
from app.schemas.study_plan import StudyPlanCreate, StudyPlanUpdate


class PlanRepository(BaseRepository[StudyPlan, StudyPlanCreate, StudyPlanUpdate]):
    """Repository for the study_plans table."""

    def get_for_student(
        self, db: Session, plan_id: int, student_id: int
    ) -> Optional[StudyPlan]:
        """Return a plan owned by the student, or None."""
        return (
            db.query(StudyPlan)
            .options(joinedload(StudyPlan.goal))
            .filter(StudyPlan.id == plan_id, StudyPlan.student_id == student_id)
            .first()
        )

    def list_for_student(
        self,
        db: Session,
        student_id: int,
        *,
        goal_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        active_goals_only: bool = False,
    ) -> List[StudyPlan]:
        """Return study plans for a student with optional filters."""
        if goal_id is not None:
            query = (
                db.query(StudyPlan)
                .options(joinedload(StudyPlan.goal))
                .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.goal_id == goal_id,
            )
            )
        elif active_goals_only:
            query = (
                db.query(StudyPlan)
                .options(joinedload(StudyPlan.goal))
                .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
                .filter(
                    StudyPlan.student_id == student_id,
                    StudyGoal.status == GoalStatus.ACTIVE,
                )
            )
        else:
            query = (
                db.query(StudyPlan)
                .options(joinedload(StudyPlan.goal))
                .filter(StudyPlan.student_id == student_id)
            )

        if status_filter:
            query = query.filter(StudyPlan.status == status_filter)
        if start_date:
            query = query.filter(StudyPlan.study_date >= start_date)
        if end_date:
            query = query.filter(StudyPlan.study_date <= end_date)

        return query.order_by(
            StudyPlan.study_date.asc(), StudyPlan.start_time.asc()
        ).all()

    def list_today_for_active_goals(
        self, db: Session, student_id: int, today: date
    ) -> List[StudyPlan]:
        """Return today's plans for a student under active goals."""
        return (
            db.query(StudyPlan)
            .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
            .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.study_date == today,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .all()
        )

    def count_for_active_goals(self, db: Session, student_id: int) -> int:
        """Return total plans linked to a student's active goals."""
        return (
            db.query(StudyPlan)
            .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
            .filter(
                StudyPlan.student_id == student_id,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .count()
        )

    def count_done_for_active_goals(self, db: Session, student_id: int) -> int:
        """Return completed plans linked to a student's active goals."""
        return (
            db.query(StudyPlan)
            .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
            .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.status == PlanStatus.DONE,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .count()
        )

    def get_next_todo_for_active_goals(
        self, db: Session, student_id: int, today: date
    ) -> Optional[StudyPlan]:
        """Return the next pending plan on or after today for active goals."""
        return (
            db.query(StudyPlan)
            .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
            .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.study_date >= today,
                StudyPlan.status == PlanStatus.TODO,
                StudyGoal.status == GoalStatus.ACTIVE,
            )
            .order_by(StudyPlan.study_date, StudyPlan.start_time)
            .first()
        )

    def list_by_goal(self, db: Session, goal_id: int) -> List[StudyPlan]:
        """Return all plans for a goal ordered by date and start time."""
        return (
            db.query(StudyPlan)
            .filter(StudyPlan.goal_id == goal_id)
            .order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc())
            .all()
        )

    def upsert_progress_for_status(
        self,
        db: Session,
        plan: StudyPlan,
        student_id: int,
        status_val: str,
        completed_at,
    ) -> None:
        """Create or update progress tracking when plan status changes (no commit)."""
        if status_val == PlanStatus.DOING:
            percent = 50.0
        elif status_val == PlanStatus.DONE:
            percent = 100.0
        else:
            percent = 0.0

        progress = self.get_progress(db, plan.id)
        if not progress:
            db.add(
                StudyPlanProgress(
                    study_plan_id=plan.id,
                    student_id=student_id,
                    completion_percent=percent,
                    completed_at=completed_at if status_val == PlanStatus.DONE else None,
                )
            )
            return

        progress.completion_percent = percent
        progress.completed_at = (
            completed_at if status_val == PlanStatus.DONE else None
        )

    def get_progress(
        self, db: Session, study_plan_id: int
    ) -> Optional[StudyPlanProgress]:
        """Return progress tracking for a study plan, if it exists."""
        return (
            db.query(StudyPlanProgress)
            .filter(StudyPlanProgress.study_plan_id == study_plan_id)
            .first()
        )

    def count_all(self, db: Session) -> int:
        """Return the total number of study plans."""
        return db.query(StudyPlan).count()

    def get_by_goal_and_student(
        self, db: Session, goal_id: int, student_id: int
    ) -> List[StudyPlan]:
        """Return all plans for a goal owned by a student."""
        return (
            db.query(StudyPlan)
            .filter(StudyPlan.goal_id == goal_id, StudyPlan.student_id == student_id)
            .all()
        )

    def save_rag_content(
        self, db: Session, plan: StudyPlan, rag_content: str
    ) -> None:
        """Persist generated lecture content on a plan (caller commits)."""
        plan.rag_content = rag_content
        db.add(plan)

    def mark_completed(
        self,
        db: Session,
        plan: StudyPlan,
        student_id: int,
        completed_at,
    ) -> None:
        """Mark a study plan as done and upsert its progress record (no commit)."""
        plan.status = PlanStatus.DONE
        db.add(plan)

        progress = self.get_progress(db, plan.id)
        if not progress:
            db.add(
                StudyPlanProgress(
                    study_plan_id=plan.id,
                    student_id=student_id,
                    completion_percent=100.0,
                    completed_at=completed_at,
                )
            )
        else:
            progress.completion_percent = 100.0
            progress.completed_at = completed_at

    def stage_review_plan(
        self,
        db: Session,
        *,
        student_id: int,
        goal_id: int,
        title: str,
        task_description: str,
        study_date: date,
        start_time: time,
        end_time: time,
    ) -> StudyPlan:
        """Stage an AI review follow-up plan in the current session (no commit)."""
        db_plan = StudyPlan(
            student_id=student_id,
            goal_id=goal_id,
            title=title,
            task_description=task_description,
            study_date=study_date,
            start_time=start_time,
            end_time=end_time,
            ai_generated=True,
            status=PlanStatus.TODO,
        )
        db.add(db_plan)
        return db_plan


plan_repository = PlanRepository(StudyPlan)
