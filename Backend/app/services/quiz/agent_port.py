"""
Agent port — isolates quiz_service from concrete quiz_generator agent imports.

Tests can patch `quiz_generator` instead of deep agent module paths.
"""

from typing import Any

from app.agents.quiz_generator.agent import generate_quiz


class QuizGeneratorPort:
    """Thin adapter over the quiz generator agent."""

    def generate(
        self,
        *,
        subject: str,
        topic: str,
        difficulty: str,
        total_questions: int,
        question_type: str,
        context: str,
        essay_count: int = 0,
    ) -> Any:
        return generate_quiz(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
            question_type=question_type,
            context=context,
            essay_count=essay_count,
        )


quiz_generator = QuizGeneratorPort()
