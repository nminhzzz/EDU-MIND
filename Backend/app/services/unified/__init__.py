"""
Unified goal workflow — draft, confirm, and background material generation.

Import from this package or from app.services.unified_service (backward compat).
"""

from app.services.unified.confirm import confirm_unified_draft
from app.services.unified.draft import (
    format_plan_as_text,
    generate_unified_draft,
    generate_unified_draft_stream,
)
from app.services.unified.materials import generate_materials_and_quizzes_for_plans_bg
from app.services.unified.validators import (
    get_active_goal_for_subject,
    prune_roadmap_history,
    validate_goal_deadline,
)

__all__ = [
    "confirm_unified_draft",
    "format_plan_as_text",
    "generate_materials_and_quizzes_for_plans_bg",
    "generate_unified_draft",
    "generate_unified_draft_stream",
    "get_active_goal_for_subject",
    "prune_roadmap_history",
    "validate_goal_deadline",
]
