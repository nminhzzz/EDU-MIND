"""Object-level authorization regression tests for student quizzes."""

import unittest
from types import SimpleNamespace

from app.services.quiz.queries import authorize_student_quiz_access


class StudentQuizAuthorizationTests(unittest.TestCase):
    def test_owner_can_access_personal_quiz(self) -> None:
        quiz = SimpleNamespace(student_id=10, study_plan_id=None, classroom_id=None)
        authorize_student_quiz_access(None, quiz, 10)

    def test_other_student_cannot_access_personal_quiz(self) -> None:
        quiz = SimpleNamespace(student_id=10, study_plan_id=None, classroom_id=None)
        with self.assertRaises(PermissionError):
            authorize_student_quiz_access(None, quiz, 11)

    def test_unassigned_quiz_is_denied(self) -> None:
        quiz = SimpleNamespace(student_id=None, study_plan_id=None, classroom_id=None)
        with self.assertRaises(PermissionError):
            authorize_student_quiz_access(None, quiz, 11)


if __name__ == "__main__":
    unittest.main()
