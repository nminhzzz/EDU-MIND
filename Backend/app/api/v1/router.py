"""
Aggregate all API v1 routers into a single router.
"""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.classrooms import router as classrooms_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.quizzes import router as quizzes_router
from app.api.v1.study_documents import router as documents_router
from app.api.v1.study_goals import router as goals_router
from app.api.v1.study_plans import router as plans_router
from app.api.v1.subjects import router as subjects_router
from app.api.v1.unified_goals import router as unified_goals_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(goals_router, prefix="/goals", tags=["Goal Planner"])
api_router.include_router(unified_goals_router, prefix="/goals", tags=["Unified Goal Planner"])
api_router.include_router(plans_router, prefix="/plans", tags=["Daily Planner"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["Shared Uploads"])
api_router.include_router(documents_router, prefix="/documents", tags=["Document Bank"])
api_router.include_router(quizzes_router, prefix="/quizzes", tags=["AI Quiz Generator"])
api_router.include_router(classrooms_router, prefix="/classrooms", tags=["Classrooms"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(chat_router, prefix="/chat", tags=["AI Tutor Chat"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["System Analytics"])
