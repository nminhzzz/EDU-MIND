from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.services.quiz.grading import grade_submission, normalize_choice_answer


def test_normalize_choice_answer_accepts_ai_answer_with_option_text():
    assert normalize_choice_answer("A") == "A"
    assert normalize_choice_answer("A. saw") == "A"
    assert normalize_choice_answer(" b) option ") == "B"
    assert normalize_choice_answer("C - option") == "C"


def test_grade_submission_matches_choice_key_to_ai_answer_with_text():
    questions = [
        {
            "question_type": "mcq",
            "correct_answer": "C. has finished",
            "question_text": "Example",
        }
    ]
    answers = [QuizAttemptAnswer(question_index=0, answer="C")]

    score, correct_count, wrong_count, stored_answers = grade_submission(
        questions, answers
    )

    assert score == 10.0
    assert correct_count == 1
    assert wrong_count == 0
    assert stored_answers[0]["is_correct"] is True
