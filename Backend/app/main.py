"""
Điểm khởi chạy FastAPI — AI Learning Assistant Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router

app = FastAPI(
    title="AI Learning Assistant Platform",
    description="Nền tảng học tập thông minh hỗ trợ bởi AI (Llama 3.1 8B).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from app.core.config import settings

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Đăng ký API v1 ───────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def root():
    return {"status": "ok", "message": "AI Learning Assistant Platform đang chạy!"}


@app.get("/health", tags=["Health Check"])
def health():
    return {"status": "healthy"}
