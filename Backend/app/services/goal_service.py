"""
Study goal use cases — list, read, update, delete, and plan listing.
"""

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.database.unit_of_work import commit_or_rollback
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.repositories.goal_repository import goal_repository
from app.repositories.plan_repository import plan_repository
from app.repositories.quiz_repository import quiz_repository
from app.schemas.study_goal import StudyGoalUpdate


def list_student_goals(db: Session, student_id: int) -> List[StudyGoal]:
    """Return all study goals for a student."""
    return goal_repository.list_by_student(db, student_id)


def get_student_goal(db: Session, goal_id: int, student_id: int) -> StudyGoal:
    """Return one study goal owned by the student."""
    goal = goal_repository.get_for_student(db, goal_id, student_id)
    if not goal:
        raise ValueError("Không tìm thấy mục tiêu học tập.")
    return goal


def update_student_goal(
    db: Session, goal_id: int, student_id: int, body: StudyGoalUpdate
) -> StudyGoal:
    """Update fields on a student's study goal."""
    goal = get_student_goal(db, goal_id, student_id)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    commit_or_rollback(db)
    db.refresh(goal)
    return goal


def list_goal_plans(db: Session, goal_id: int, student_id: int) -> List[StudyPlan]:
    """Return ordered study plans for a goal after verifying ownership."""
    get_student_goal(db, goal_id, student_id)
    return plan_repository.list_by_goal(db, goal_id)


def delete_student_goal(db: Session, goal_id: int, student_id: int) -> Dict[str, Any]:
    """Delete a goal and related quizzes; study plans cascade via ORM."""
    goal = goal_repository.get_for_student(db, goal_id, student_id)
    if not goal:
        raise ValueError("Không tìm thấy lộ trình học tập để xóa.")

    plan_ids = [plan.id for plan in goal.study_plans]
    quiz_repository.delete_linked_to_plans(db, plan_ids)
    db.delete(goal)
    commit_or_rollback(db)

    return {
        "message": "Đã xóa lộ trình học tập và toàn bộ dữ liệu liên quan thành công!"
    }
