"""
Repository cho AIRecommendationReview — Giai đoạn 4.
"""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.enums import RecommendationStatus
from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.repositories.base import BaseRepository
from app.schemas.ai_recommendation_review import AIRecommendationReviewUpdate


class AIRecommendationReviewRepository(
    BaseRepository[AIRecommendationReview, BaseModel, AIRecommendationReviewUpdate]
):
    """
    Repository truy xuất dữ liệu cho bảng ai_recommendation_reviews.
    """

    def add_pending(
        self,
        db: Session,
        *,
        student_id: int,
        teacher_id: Optional[int],
        recommendation: str,
    ) -> AIRecommendationReview:
        """Stage a pending HITL review in the current session (no commit)."""
        review = AIRecommendationReview(
            student_id=student_id,
            teacher_id=teacher_id,
            recommendation=recommendation,
            status=RecommendationStatus.PENDING,
        )
        db.add(review)
        return review

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
                AIRecommendationReview.status == RecommendationStatus.PENDING,
                AIRecommendationReview.student_id.in_(
                    db.query(ClassroomStudent.student_id)
                    .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
                    .filter(Classroom.teacher_id == teacher_id)
                ),
            )
            .order_by(AIRecommendationReview.created_at.desc())
            .all()
        )

    def get_approved_by_student(
        self, db: Session, student_id: int
    ) -> List[AIRecommendationReview]:
        """Return approved recommendations for a student, most recent first."""
        return (
            db.query(AIRecommendationReview)
            .filter(
                AIRecommendationReview.student_id == student_id,
                AIRecommendationReview.status == RecommendationStatus.APPROVED,
            )
            .order_by(AIRecommendationReview.created_at.desc())
            .all()
        )


ai_recommendation_review_repository = AIRecommendationReviewRepository(
    AIRecommendationReview
)
