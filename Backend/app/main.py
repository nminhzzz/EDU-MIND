"""
FastAPI application entry point — AI Learning Assistant Platform.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(
        "Starting %s in %s mode", settings.PROJECT_NAME, settings.ENVIRONMENT.upper()
    )
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Nền tảng học tập thông minh hỗ trợ bởi AI (DeepSeek V4 Flash).",
    version="1.0.0",
    # Hide interactive docs in production to reduce attack surface
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middleware(app)
register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Local file uploads fallback (when Cloudinary is not configured)
_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if os.path.isdir(_uploads_dir):
    app.mount("/static", StaticFiles(directory=_uploads_dir), name="static")


# ── Health checks ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root() -> dict:
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is running."}


@app.get("/health", tags=["Health"])
def health() -> dict:
    """Shallow liveness probe — used by load balancers."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/health/detailed", tags=["Health"])
@app.get("/ready", tags=["Health"])
async def health_detailed(response: Response) -> dict:
    """
    Deep readiness probe — checks MySQL, MongoDB, and Redis connectivity.
    Returns individual service status so ops can pinpoint failures quickly.
    """
    results: dict[str, str] = {}

    # MySQL
    try:
        from sqlalchemy import text
        from app.database.mysql import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        results["mysql"] = "ok"
    except Exception as exc:
        logger.error("MySQL health check failed: %s", exc)
        results["mysql"] = "error"

    # Redis
    try:
        from app.database.redis import get_redis
        get_redis().ping()
        results["redis"] = "ok"
    except Exception as exc:
        logger.error("Redis health check failed: %s", exc)
        results["redis"] = "error"

    # MongoDB
    try:
        from app.database.mongodb import get_mongodb_db

        mongo_db = get_mongodb_db()
        await mongo_db.command("ping")
        results["mongodb"] = "ok"
    except Exception as exc:
        logger.error("MongoDB health check failed: %s", exc)
        results["mongodb"] = "error"

    overall = "healthy" if all(v == "ok" for v in results.values()) else "degraded"
    if overall != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": overall, **results}
