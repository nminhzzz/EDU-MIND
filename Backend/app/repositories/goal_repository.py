from app.repositories.base import BaseRepository
from app.models.study_goal import StudyGoal
from app.schemas.study_goal import StudyGoalCreate, StudyGoalUpdate

class GoalRepository(BaseRepository[StudyGoal, StudyGoalCreate, StudyGoalUpdate]):
    """
    Repository thao tác cơ sở dữ liệu cho bảng study_goals.
    """
    pass

goal_repository = GoalRepository(StudyGoal)
