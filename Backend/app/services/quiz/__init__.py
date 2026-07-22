"""
Quiz workflow — AI generation, grading, teacher management, and history.

Import from this package or from app.services.quiz_service (backward compat).
"""

from app.services.quiz.attempts import (
    get_classroom_quiz_attempts,
    get_student_quiz_attempts,
    submit_quiz_attempt,
)
from app.services.quiz.generation import (
    generate_and_save_quiz,
    generate_classroom_quiz,
    generate_classroom_quiz_from_file,
)
from app.services.quiz.grading import PLAN_PASS_SCORE_THRESHOLD
from app.services.quiz.queries import (
    get_quiz,
    get_quiz_for_study_plan,
    get_quiz_review,
    get_student_assigned_quizzes_service,
    submit_student_quiz,
)
from app.services.quiz.teacher import teacher_create_quiz, update_quiz_by_teacher

__all__ = [
    "PLAN_PASS_SCORE_THRESHOLD",
    "generate_and_save_quiz",
    "generate_classroom_quiz",
    "generate_classroom_quiz_from_file",
    "get_classroom_quiz_attempts",
    "get_quiz",
    "get_quiz_for_study_plan",
    "get_quiz_review",
    "get_student_quiz_attempts",
    "submit_quiz_attempt",
    "submit_student_quiz",
    "teacher_create_quiz",
    "update_quiz_by_teacher",
]
