"""
Tổng hợp tất cả API routers của v1 vào một router duy nhất.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.study_goals import router as goals_router

api_router = APIRouter()

# ── Auth: Đăng ký / Đăng nhập ────────────────────────────────
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["🔐 Auth"]
)

# ── Giai đoạn 1: AI Goal Planner ─────────────────────────────
api_router.include_router(
    goals_router,
    prefix="/goals",
    tags=["🎯 Goal Planner"]
)

# ── Unified AI Flow: Phase 1 + 2 + 3 ────────────────────────
from app.api.v1.unified_goals_api import router as unified_goals_router
api_router.include_router(
    unified_goals_router,
    prefix="/goals",
    tags=["🎯 Unified Goal Planner"]
)

# ── Giai đoạn 2: AI Daily Planner ────────────────────────────
from app.api.v1.study_plans import router as plans_router
api_router.include_router(
    plans_router,
    prefix="/plans",
    tags=["📅 Daily Planner"]
)

# ── Giai đoạn 3: Question Bank & RAG Quizzes ─────────────────
from app.api.v1.quizzes import router as quizzes_router
api_router.include_router(
    quizzes_router,
    prefix="/quizzes",
    tags=["📚 Question Bank & RAG"]
)

# ── Giai đoạn 4: Classrooms & AI Recommendation Reviews ──────
from app.api.v1.classrooms import router as classrooms_router
from app.api.v1.recommendations import router as recommendations_router

api_router.include_router(
    classrooms_router,
    prefix="/classrooms",
    tags=["🏫 Classrooms"]
)

api_router.include_router(
    recommendations_router,
    prefix="/recommendations",
    tags=["📋 AI Recommendation Reviews"]
)

# ── Giai đoạn 4: Subjects Management ─────────────────────────
from app.api.v1.subjects import router as subjects_router
api_router.include_router(
    subjects_router,
    prefix="/subjects",
    tags=["📚 Subjects"]
)

# Giai đoạn 4: Chat Tutor persistent memory
from app.api.v1.chat import router as chat_router
api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["💬 AI Tutor Chat"]
)

# ── Feature 5: Dashboard Realtime SSE ──────────────────────────
from app.api.v1.dashboard import router as dashboard_router
api_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["📊 Dashboard"]
)
