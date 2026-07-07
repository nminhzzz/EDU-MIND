"""
Repository cho LearningAnalytic — Giai đoạn 4.
"""

from pydantic import BaseModel
from app.repositories.base import BaseRepository
from app.models.learning_analytic import LearningAnalytic


class AnalyticRepository(BaseRepository[LearningAnalytic, BaseModel, BaseModel]):
    """
    Repository truy xuất dữ liệu cho bảng learning_analytics.
    """

    pass


analytic_repository = AnalyticRepository(LearningAnalytic)
