import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    # Mã môn học duy nhất: TOAN01, VATLY12, TRIETHOC01
    code = Column(String(50), unique=True, nullable=False, index=True)

    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    classrooms = relationship("Classroom", back_populates="subject")
    study_goals = relationship("StudyGoal", back_populates="subject")
    documents = relationship("StudyDocument", back_populates="subject", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="subject")
    learning_analytics = relationship("LearningAnalytic", back_populates="subject")
