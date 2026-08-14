import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from pydantic import BaseModel, Field

from app.infrastructure.ai.content import (
    _build_schema_instruction,
    _record_response_usage,
    capture_ai_usage,
)
from app.infrastructure.ai.retry import is_retryable_ai_error
from app.models.study_plan import StudyPlan
from app.services.plan_generation_service import request_plan_generation
from app.services.unified.confirm import _create_study_plans
from app.schemas.learning_bundle import LearningBundle
from pydantic import ValidationError


class _ProviderError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class _Schema(BaseModel):
    value: str = Field(description="Verbose text that should not enter the prompt")


class AIOptimizationTests(unittest.TestCase):
    def test_retry_policy_only_accepts_transient_failures(self):
        self.assertTrue(is_retryable_ai_error(_ProviderError(429)))
        self.assertTrue(is_retryable_ai_error(_ProviderError(503)))
        self.assertTrue(is_retryable_ai_error(TimeoutError()))
        self.assertFalse(is_retryable_ai_error(_ProviderError(401)))
        self.assertFalse(is_retryable_ai_error(_ProviderError(402)))
        self.assertFalse(is_retryable_ai_error(ValueError("invalid JSON")))

    def test_schema_prompt_removes_non_structural_metadata(self):
        instruction = _build_schema_instruction(_Schema)
        self.assertIn('"value"', instruction)
        self.assertNotIn("Verbose text", instruction)
        self.assertNotIn('"title"', instruction)

    def test_usage_falls_back_to_sum_when_provider_omits_total(self):
        captured = []
        response = Mock(
            usage_metadata={"input_tokens": 11, "output_tokens": 7},
            response_metadata={},
        )
        with capture_ai_usage(captured.append):
            _record_response_usage(response)
        self.assertEqual(captured[0]["total_tokens"], 18)

    def test_generation_request_is_idempotent(self):
        db = Mock()
        plan = StudyPlan(id=42, generation_status="not_started", generation_attempts=0)
        db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.one.return_value = plan

        self.assertTrue(request_plan_generation(db, plan))
        self.assertEqual(plan.generation_status, "queued")
        self.assertEqual(plan.generation_attempts, 1)
        self.assertFalse(request_plan_generation(db, plan))
        db.commit.assert_called_once()

    def test_learning_bundle_requires_exactly_ten_questions(self):
        question = {
            "question_text": "Question?",
            "question_type": "mcq",
            "options": [
                {"key": key, "value": key} for key in ("A", "B", "C", "D")
            ],
            "correct_answer": "A",
            "explanation": "Because A is correct.",
            "difficulty": "medium",
        }
        payload = {
            "lesson_markdown": "x" * 500,
            "lesson_summary": "s" * 100,
            "quiz_title": "Quiz",
            "questions": [question] * 10,
        }
        bundle = LearningBundle.model_validate(payload)
        self.assertEqual(len(bundle.questions), 10)
        self.assertEqual(sum(q.question_type == "mcq" for q in bundle.questions), 7)
        self.assertEqual(sum(q.question_type == "essay" for q in bundle.questions), 3)
        payload["questions"] = [question] * 9
        with self.assertRaises(ValidationError):
            LearningBundle.model_validate(payload)

        essay = dict(question)
        essay.update({"question_type": "essay", "options": None})
        payload["questions"] = [question] * 9 + [essay]
        self.assertEqual(len(LearningBundle.model_validate(payload).questions), 10)

    def test_confirm_creates_plans_without_assigning_read_only_subject(self):
        db = Mock()
        draft = SimpleNamespace(
            daily_schedule=[
                SimpleNamespace(
                    date="2026-08-15",
                    start_time="08:00",
                    end_time="09:00",
                    task="Lesson",
                    description="Description",
                )
            ]
        )
        plans = _create_study_plans(db, draft, goal_id=7, student_id=3)
        self.assertEqual(len(plans), 1)
        self.assertNotIn("subject_id", plans[0].__dict__)
        db.flush.assert_called_once()


if __name__ == "__main__":
    unittest.main()
