"""Shared retry policy for AI provider calls."""

from __future__ import annotations


_RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}


def is_retryable_ai_error(exc: Exception) -> bool:
    """Retry only transient transport, throttling, and provider failures."""
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
    if status_code is not None:
        try:
            return int(status_code) in _RETRYABLE_STATUS_CODES
        except (TypeError, ValueError):
            return False
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    name = type(exc).__name__.lower()
    return "timeout" in name or "connection" in name
