"""Email delivery adapters."""

from app.infrastructure.email.smtp import (
    send_deadline_reminder_email,
    send_recommendation_approved_email,
    send_recommendation_rejected_email,
    send_welcome_email,
)

__all__ = [
    "send_deadline_reminder_email",
    "send_recommendation_approved_email",
    "send_recommendation_rejected_email",
    "send_welcome_email",
]
