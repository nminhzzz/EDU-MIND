import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base


class QuestionBank(Base):
    """
    Kho câu hỏi dùng chung của toàn hệ thống.
    Tách biệt với bảng `questions` (junction) để tái sử dụng câu hỏi
    trên nhiều đề thi khác nhau và phục vụ RAG/Embedding.
    """
    __tablename__ = "question_bank"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )

    # Chủ đề / chương: ví dụ "Chương 2: Vật chất và ý thức"
    topic = Column(String(255), nullable=True)

    difficulty = Column(
        Enum("easy", "medium", "hard", name="qb_difficulty"),
        nullable=False,
        default="medium"
    )

    question_text = Column(Text, nullable=False)

    # Danh sách đáp án MCQ: [{"key": "A", "value": "..."}, ...]
    options = Column(JSON, nullable=True)

    # Đáp án đúng: "A", "B", "C", "D" hoặc "True"/"False"
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=True)

    # Người tạo câu hỏi (giáo viên hoặc AI)
    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # ID vector embedding trong ChromaDB / Pinecone (phục vụ RAG)
    embedding_id = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    subject = relationship("Subject", foreign_keys=[subject_id])
    creator = relationship("User", foreign_keys=[created_by])
    quiz_questions = relationship("Question", back_populates="question_bank_item")
