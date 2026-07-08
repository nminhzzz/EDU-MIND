"""Backward-compatible re-exports — prefer app.infrastructure.email."""

from app.infrastructure.email import (  # noqa: F401
    send_deadline_reminder_email,
    send_recommendation_approved_email,
    send_recommendation_rejected_email,
    send_welcome_email,
)
