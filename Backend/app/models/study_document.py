import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudyDocument(Base):
    __tablename__ = "study_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )
    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)  # Lưu link Cloudinary hoặc đường dẫn local
    file_type = Column(String(50), nullable=False)      # pdf, docx, txt, md...
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
