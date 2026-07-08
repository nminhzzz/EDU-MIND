"""
Application middleware.
Currently provides: HTTP request/response logging with duration tracking.
"""

import time

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every incoming request and its response status + duration.
    Skips health-check endpoints to reduce noise.
    """

    _SKIP_PATHS = {"/", "/health"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self._SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


def register_middleware(app: FastAPI) -> None:
    """Attach all custom middleware to the FastAPI application."""
    app.add_middleware(RequestLoggingMiddleware)
