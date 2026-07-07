"""
Service xử lý các nghiệp vụ liên quan đến Phê duyệt Đề xuất học tập AI (HITL) — Giai đoạn 4.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta

from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.notification import Notification
from app.repositories.ai_recommendation_review_repository import (
    ai_recommendation_review_repository,
)


def get_pending_reviews(db: Session, teacher_id: int) -> List[AIRecommendationReview]:
    """Lấy danh sách các đề xuất ôn tập đang chờ duyệt của học sinh thuộc lớp giáo viên này dạy."""
    return ai_recommendation_review_repository.get_pending_by_teacher(db, teacher_id)


def review_recommendation(
    db: Session,
    review_id: int,
    teacher_id: int,
    status: str,
    teacher_feedback: Optional[str] = None,
) -> AIRecommendationReview:
    """Giáo viên phê duyệt hoặc từ chối đề xuất ôn tập từ AI."""
    # 1. Tìm bản ghi đề xuất
    review = ai_recommendation_review_repository.get(db, review_id)
    if not review:
        raise ValueError(f"Không tìm thấy đề xuất học tập với ID={review_id}.")

    # 2. Kiểm tra quyền kiểm duyệt (học sinh của đề xuất có thuộc lớp nào của giáo viên này không)
    is_authorized = (
        db.query(ClassroomStudent)
        .join(Classroom, Classroom.id == ClassroomStudent.classroom_id)
        .filter(
            Classroom.teacher_id == teacher_id,
            ClassroomStudent.student_id == review.student_id,
        )
        .first()
        is not None
    )
    if not is_authorized:
        raise PermissionError("Bạn không có quyền phê duyệt đề xuất cho học sinh này.")

    # 3. Cập nhật trạng thái duyệt
    review.status = status
    review.teacher_feedback = teacher_feedback
    review.teacher_id = teacher_id

    # 4. Nếu phê duyệt (approved) -> Tự động tạo kế hoạch ôn tập & gửi thông báo
    if status == "approved":
        # Tìm mục tiêu học tập (StudyGoal) gần nhất của học sinh để gán task
        goal = (
            db.query(StudyGoal)
            .filter(StudyGoal.student_id == review.student_id)
            .order_by(StudyGoal.created_at.desc())
            .first()
        )

        # Nếu học sinh có mục tiêu học tập, sinh một StudyPlan tương ứng
        if goal:
            # Tạo lịch học bổ sung vào ngày mai lúc 19:00 - 20:00
            study_date = date.today() + timedelta(days=1)
            start_time = time(19, 0, 0)
            end_time = time(20, 0, 0)

            # Giới hạn tiêu đề tối đa 255 ký tự
            title_text = (
                f"[Ôn tập AI] {review.recommendation[:50]}..."
                if len(review.recommendation) > 50
                else f"[Ôn tập AI] {review.recommendation}"
            )

            db_plan = StudyPlan(
                student_id=review.student_id,
                goal_id=goal.id,
                title=title_text,
                task_description=review.recommendation,
                study_date=study_date,
                start_time=start_time,
                end_time=end_time,
                ai_generated=True,
                status="todo",
            )
            db.add(db_plan)

        # Tạo thông báo gửi cho học sinh
        db_notification = Notification(
            user_id=review.student_id,
            title="Đề xuất học tập mới được phê duyệt",
            content=f"Thầy cô đã phê duyệt một đề xuất ôn tập từ AI cho bạn: {review.recommendation[:120]}...",
            type="plan",
            is_read=False,
        )
        db.add(db_notification)

    db.commit()
    db.refresh(review)
    return review


def get_student_recommendations(
    db: Session, student_id: int
) -> List[AIRecommendationReview]:
    """Lấy danh sách các đề xuất học tập AI đã được duyệt dành cho học sinh."""
    return (
        db.query(AIRecommendationReview)
        .filter(
            AIRecommendationReview.student_id == student_id,
            AIRecommendationReview.status == "approved",
        )
        .order_by(AIRecommendationReview.created_at.desc())
        .all()
    )
