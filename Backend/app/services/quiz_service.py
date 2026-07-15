"""
Backward-compatible re-exports — prefer app.services.quiz.
"""

from app.services.quiz import (  # noqa: F401
    generate_and_save_quiz,
    generate_classroom_quiz,
    get_classroom_quiz_attempts,
    get_quiz,
    get_quiz_for_study_plan,
    get_quiz_review,
    get_student_quiz_attempts,
    submit_quiz_attempt,
    submit_student_quiz,
    teacher_create_quiz,
)
