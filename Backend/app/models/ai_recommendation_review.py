import datetime
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base


class AIRecommendationReview(Base):
    """
    Lưu trữ kết quả phân tích AI và vòng phê duyệt HITL (Human-in-the-Loop)
    của giáo viên trước khi đề xuất được gửi đến học sinh.
    """
    __tablename__ = "ai_recommendation_reviews"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Học sinh nhận đề xuất
    student_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Giáo viên phê duyệt (NULL nếu chưa được phân công)
    teacher_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Nội dung đề xuất do AI sinh ra
    recommendation = Column(Text, nullable=False)

    # Phản hồi / ghi chú của giáo viên khi duyệt
    teacher_feedback = Column(Text, nullable=True)

    status = Column(
        Enum("pending", "approved", "rejected", name="review_status"),
        nullable=False,
        default="pending"
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
