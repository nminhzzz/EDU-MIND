"""
Script kiem tra cu phap (syntax check) cua tat ca models.
Chi kiem tra import - khong ket noi database that.

Chay bang: python scratch/verify_models.py (tu thu muc Backend)
"""
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set bien moi truong (khong ket noi that, chi de models khoi tao)
os.environ.setdefault("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/learning_db")
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017/chat_db")

print("Kiem tra import MySQL models (SQLAlchemy)...")

from app.models.user import User
from app.models.student_preference import StudentPreference
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.study_plan_progress import StudyPlanProgress
from app.models.study_document import StudyDocument
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.notification import Notification

print("Kiem tra import MongoDB Pydantic models...")

from app.models.mongodb_models import (
    ChatSession, ChatMessage, StudyMaterialEmbedding
)

print()
print("=" * 50)
print("KET QUA KIEM TRA CU PHAP")
print("=" * 50)

mysql_models = [
    ("users",                    "User"),
    ("student_preferences",      "StudentPreference"),
    ("subjects",                 "Subject"),
    ("classrooms",               "Classroom"),
    ("classroom_students",       "ClassroomStudent"),
    ("study_goals",              "StudyGoal"),
    ("study_plans",              "StudyPlan"),
    ("study_plan_progress",      "StudyPlanProgress"),
    ("study_documents",          "StudyDocument"),
    ("quizzes",                  "Quiz"),
    ("quiz_attempts",            "QuizAttempt"),
    ("learning_analytics",       "LearningAnalytic"),
    ("ai_recommendation_reviews","AIRecommendationReview"),
    ("notifications",            "Notification"),
]

print(f"\nMySQL Tables ({len(mysql_models)} bang):")
for table, model in mysql_models:
    print(f"  [OK] {table:35s} <- {model}")

mongo_models = [
    "ChatSession", "ChatMessage", "StudyMaterialEmbedding"
]
print(f"\nMongoDB Collections ({len(mongo_models)} collections):")
for m in mongo_models:
    print(f"  [OK] {m}")

print("\nTat ca models import thanh cong! (khong co loi cu phap)")
print("De tao bang that: chay alembic revision --autogenerate roi alembic upgrade head")
