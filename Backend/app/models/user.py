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
    grade = Column(
        Enum(
            "grade_6",
            "grade_7",
            "grade_8",
            "grade_9",
            "grade_10",
            "grade_11",
            "grade_12",
            "uni_year_1",
            "uni_year_2",
            "uni_year_3",
            "uni_year_4",
            name="student_grade",
        ),
        nullable=True,
    )

    role = Column(
        Enum("student", "teacher", "admin", name="user_roles"),
        nullable=False,
        default="student",
    )

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    preference = relationship(
        "StudentPreference",
        back_populates="student",
        uselist=False,  # 1-1
        cascade="all, delete-orphan",
    )
    classrooms_teaching = relationship("Classroom", back_populates="teacher")
    classroom_memberships = relationship("ClassroomStudent", back_populates="student")
    study_goals = relationship(
        "StudyGoal", foreign_keys="StudyGoal.student_id", back_populates="student"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
