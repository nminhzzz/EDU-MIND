"""Boundary validation tests for untrusted quiz payloads."""

import unittest

from pydantic import ValidationError

from app.schemas.quiz import ClassroomQuizCreateRequest
from app.schemas.quiz_attempt import QuizAttemptCreate


class QuizPayloadValidationTests(unittest.TestCase):
    def test_negative_duration_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            QuizAttemptCreate(
                answers=[],
                duration_seconds=-1,
                tab_violations_count=0,
            )

    def test_negative_question_index_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            QuizAttemptCreate(
                answers=[{"question_index": -1, "answer": "A"}],
                duration_seconds=10,
                tab_violations_count=0,
            )

    def test_excessive_generation_request_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ClassroomQuizCreateRequest(
                subject_id=1,
                total_questions=101,
            )

    def test_invalid_difficulty_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ClassroomQuizCreateRequest(
                subject_id=1,
                difficulty="impossible",
            )


if __name__ == "__main__":
    unittest.main()
