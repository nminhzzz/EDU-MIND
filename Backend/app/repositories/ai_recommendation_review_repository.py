"""
Repository cho AIRecommendationReview — Giai đoạn 4.
"""

from typing import List
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from app.repositories.base import BaseRepository
from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.schemas.ai_recommendation_review import AIRecommendationReviewUpdate


class AIRecommendationReviewRepository(
    BaseRepository[AIRecommendationReview, BaseModel, AIRecommendationReviewUpdate]
):
    """
    Repository truy xuất dữ liệu cho bảng ai_recommendation_reviews.
    """

    def get_pending_by_teacher(
        self, db: Session, teacher_id: int
    ) -> List[AIRecommendationReview]:
        """
        Lấy danh sách các đề xuất học tập ở trạng thái pending (chờ duyệt)
        của các học sinh nằm trong các lớp học do giáo viên này phụ trách.
        """
        return (
            db.query(AIRecommendationReview)
            .options(joinedload(AIRecommendationReview.student))
            .filter(
                AIRecommendationReview.status == "pending",
                AIRecommendationReview.student_id.in_(
                    db.query(ClassroomStudent.student_id)
                    .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
                    .filter(Classroom.teacher_id == teacher_id)
                ),
            )
            .all()
        )


ai_recommendation_review_repository = AIRecommendationReviewRepository(
    AIRecommendationReview
)
