import pytest
from unittest.mock import patch, MagicMock
from app.services.quiz.grading import normalize_ai_questions, grade_submission
from app.schemas.quiz_attempt import QuizAttemptAnswer


def test_normalize_ai_questions_mcq():
    # Mock an AI quiz response containing MCQ
    class MockOption:
        def __init__(self, key, value):
            self.key = key
            self.value = value

    class MockQuestion:
        def __init__(self, question_text, question_type, options, correct_answer, explanation):
            self.question_text = question_text
            self.question_type = question_type
            self.options = options
            self.correct_answer = correct_answer
            self.explanation = explanation

    class MockQuiz:
        def __init__(self, title, questions):
            self.title = title
            self.questions = questions

    q1 = MockQuestion(
        question_text="2 + 2 = ?",
        question_type="mcq",
        options=[MockOption("A", "3"), MockOption("B", "4")],
        correct_answer="B",
        explanation="2 + 2 is 4"
    )

    q2 = MockQuestion(
        question_text="Viết bài phân tích tác phẩm Lão Hạc.",
        question_type="essay",
        options=None,
        correct_answer="Bài mẫu phân tích: Lão Hạc là...",
        explanation="Thang điểm: 4đ cho nội dung, 3đ cho lập luận, 3đ cho cách diễn đạt"
    )

    mock_quiz = MockQuiz("Đề thi thử", [q1, q2])

    normalized = normalize_ai_questions(mock_quiz)

    assert len(normalized) == 2
    assert normalized[0]["question_text"] == "2 + 2 = ?"
    assert normalized[0]["question_type"] == "mcq"
    assert len(normalized[0]["options"]) == 2
    assert normalized[0]["correct_answer"] == "B"

    assert normalized[1]["question_text"] == "Viết bài phân tích tác phẩm Lão Hạc."
    assert normalized[1]["question_type"] == "essay"
    assert normalized[1]["options"] == []
    assert normalized[1]["correct_answer"].startswith("Bài mẫu phân tích")


@patch("app.services.quiz.grading.extract_text_from_file")
@patch("app.services.quiz.grading.grade_essay_with_ai")
def test_grade_submission_mixed(mock_grade_essay, mock_extract):
    # Mock text extraction and AI grading
    mock_extract.return_value = "Học sinh trả lời: Lão Hạc là nhân vật trung tâm..."
    mock_grade_essay.return_value = (8.5, "Lời phê tốt, lập luận chặt chẽ.")

    questions = [
        {
            "question_text": "2 + 2 = ?",
            "question_type": "mcq",
            "options": [{"key": "A", "value": "3"}, {"key": "B", "value": "4"}],
            "correct_answer": "B",
            "explanation": "2+2=4"
        },
        {
            "question_text": "Phân tích nhân vật Lão Hạc",
            "question_type": "essay",
            "options": [],
            "correct_answer": "Bài mẫu phân tích...",
            "explanation": "Thang điểm 10"
        }
    ]

    submitted_answers = [
        QuizAttemptAnswer(question_index=0, answer="B")
    ]

    score, correct_count, wrong_count, answers_json = grade_submission(
        questions_list=questions,
        submitted_answers=submitted_answers,
        essay_file_path="uploads/classroom_quizzes/dummy.pdf"
    )

    mock_extract.assert_called_once_with("uploads/classroom_quizzes/dummy.pdf")
    mock_grade_essay.assert_called_once()

    # Total questions = 2
    # MCQ correct gets 10 points
    # Essay gets 8.5 points
    # Average score = (10 + 8.5) / 2 = 9.25
    assert score == 9.25
    assert correct_count == 2
    assert wrong_count == 0
    assert len(answers_json) == 2
    assert answers_json[0]["is_correct"] is True
    assert answers_json[1]["is_correct"] is True
    assert answers_json[1]["score"] == 8.5
    assert answers_json[1]["feedback"] == "Lời phê tốt, lập luận chặt chẽ."
