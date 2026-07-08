"""
Application-wide string enumerations.

All members inherit from str so they compare equal to their raw string values
and are stored as plain strings in MySQL — no schema changes or migrations needed.

    UserRole.STUDENT == "student"                        # True
    "student" in {UserRole.STUDENT, UserRole.ADMIN}      # True
    StudyGoal.status == GoalStatus.ACTIVE                # valid SQLAlchemy filter
"""

from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlanStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NotificationType(str, Enum):
    PLAN = "plan"
    SCORE = "score"
    QUIZ = "quiz"
    SYSTEM = "system"
