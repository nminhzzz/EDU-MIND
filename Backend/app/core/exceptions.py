"""
Custom exception handlers for FastAPI.

Registers global handlers so that service-layer exceptions
(ValueError, PermissionError) are automatically converted to
proper HTTP responses — routers no longer need manual try/except blocks.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Service-layer validation errors → 400 Bad Request."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        """Service-layer authorization errors → 403 Forbidden."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )
