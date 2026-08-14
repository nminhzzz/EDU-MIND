"""
Backward-compatible re-exports — prefer app.services.unified.
"""

from app.services.unified import (  # noqa: F401
    confirm_unified_draft,
    generate_unified_draft,
    get_active_goal_for_subject,
    validate_goal_deadline,
)
