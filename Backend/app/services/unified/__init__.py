"""
Unified goal workflow — draft, confirm, and background material generation.

Import from this package or from app.services.unified_service (backward compat).
"""

from app.services.unified.confirm import confirm_unified_draft
from app.services.unified.draft import generate_unified_draft
from app.services.unified.materials import generate_materials_and_quizzes_for_plans_bg
from app.services.unified.validators import (
    get_active_goal_for_subject,
    validate_goal_deadline,
)

__all__ = [
    "confirm_unified_draft",
    "generate_materials_and_quizzes_for_plans_bg",
    "generate_unified_draft",
    "get_active_goal_for_subject",
    "validate_goal_deadline",
]
