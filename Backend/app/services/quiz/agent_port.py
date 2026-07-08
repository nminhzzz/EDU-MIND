"""
Agent port — isolates quiz_service from concrete quiz_generator agent imports.

Tests can patch `quiz_generator` instead of deep agent module paths.
"""

from typing import Any

from app.agents.quiz_generator.agent import correct_quiz_questions, generate_quiz
from app.agents.quiz_generator.reviewer import review_generated_quiz


class QuizGeneratorPort:
    """Thin adapter over the quiz generator + QC reviewer agents."""

    def generate(
        self,
        *,
        subject: str,
        topic: str,
        difficulty: str,
        total_questions: int,
        question_type: str,
        context: str,
    ) -> Any:
        return generate_quiz(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
            question_type=question_type,
            context=context,
        )

    def review(self, *, quiz_data: dict, context: str) -> Any:
        return review_generated_quiz(quiz_data=quiz_data, context=context)

    def correct(self, *, original_quiz: dict, feedback: str, context: str) -> Any:
        return correct_quiz_questions(
            original_quiz=original_quiz,
            feedback=feedback,
            context=context,
        )


quiz_generator = QuizGeneratorPort()
