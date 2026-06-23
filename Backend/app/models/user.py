import datetime
from sqlalchemy import Column, BigInteger, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    role = Column(
        Enum("student", "teacher", "admin", name="user_roles"),
        nullable=False,
        default="student"
    )

    # Ví dụ: "Lớp 12", "Đại học năm 1"
    grade = Column(String(50), nullable=True)

    learning_level = Column(
        Enum("weak", "average", "good", "excellent", name="learning_levels"),
        nullable=True
    )

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    preference = relationship(
        "StudentPreference",
        back_populates="student",
        uselist=False,  # 1-1
        cascade="all, delete-orphan"
    )
    classrooms_teaching = relationship("Classroom", back_populates="teacher")
    classroom_memberships = relationship("ClassroomStudent", back_populates="student")
    study_goals = relationship("StudyGoal", foreign_keys="StudyGoal.student_id", back_populates="student")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
