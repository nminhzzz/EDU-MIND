from app.repositories.base import BaseRepository
from app.models.study_plan import StudyPlan
from app.schemas.study_plan import StudyPlanCreate, StudyPlanUpdate


class PlanRepository(BaseRepository[StudyPlan, StudyPlanCreate, StudyPlanUpdate]):
    """
    Repository thao tác cơ sở dữ liệu cho bảng study_plans.
    """

    pass


plan_repository = PlanRepository(StudyPlan)
