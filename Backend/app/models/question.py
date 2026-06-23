import datetime
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Question(Base):
    """
    Bảng junction (nhiều-nhiều) giữa Quiz và QuestionBank.
    Mỗi bản ghi đại diện cho một câu hỏi được chọn từ kho vào một đề thi cụ thể.
    Thiết kế này cho phép tái sử dụng câu hỏi trên nhiều đề thi khác nhau.
    """
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id = Column(
        BigInteger,
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False
    )
    question_bank_id = Column(
        BigInteger,
        ForeignKey("question_bank.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    question_bank_item = relationship("QuestionBank", back_populates="quiz_questions")
