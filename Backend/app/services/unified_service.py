"""
Backward-compatible re-exports — prefer app.services.unified.
"""

from app.services.unified import (  # noqa: F401
    confirm_unified_draft,
    generate_materials_and_quizzes_for_plans_bg,
    generate_unified_draft,
    get_active_goal_for_subject,
    validate_goal_deadline,
)
