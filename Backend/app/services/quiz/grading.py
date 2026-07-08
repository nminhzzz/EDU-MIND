"""
Quiz grading and AI question normalisation helpers.
"""

from typing import Any, Dict, List, Tuple

from app.schemas.quiz_attempt import QuizAttemptAnswer

PLAN_PASS_SCORE_THRESHOLD = 8.0


def build_rag_context(materials: List[Dict[str, Any]]) -> str:
    """Format vector-search results into a single context string for the AI agent."""
    if not materials:
        return ""
    return "\n\n".join(
        f"--- Tài liệu {i + 1} (Chủ đề: {m['topic']}) ---\n{m['content']}"
        for i, m in enumerate(materials)
    )


def normalize_ai_questions(ai_quiz: Any) -> List[Dict[str, Any]]:
    """Convert agent output into the JSON shape stored on the Quiz model."""
    questions_json: List[Dict[str, Any]] = []

    for q in ai_quiz.questions:
        options_data = (
            [{"key": opt.key, "value": opt.value} for opt in q.options]
            if q.options
            else []
        )
        correct_ans = q.correct_answer.strip() if q.correct_answer else ""

        if options_data:
            valid_keys = {opt["key"].strip().upper() for opt in options_data}
            if correct_ans.upper() not in valid_keys:
                matched_key = next(
                    (
                        opt["key"]
                        for opt in options_data
                        if opt["value"].strip().lower() == correct_ans.lower()
                    ),
                    None,
                )
                correct_ans = matched_key if matched_key else options_data[0]["key"]

        questions_json.append(
            {
                "question_text": q.question_text,
                "options": options_data,
                "correct_answer": correct_ans,
                "explanation": q.explanation,
            }
        )

    return questions_json


def grade_submission(
    questions_list: List[Dict[str, Any]],
    submitted_answers: List[QuizAttemptAnswer],
) -> Tuple[float, int, int, List[Dict[str, Any]]]:
    """
    Auto-grade a quiz submission.

    Returns (score out of 10, correct_count, wrong_count, answers_json).
    """
    total_q = len(questions_list)
    submitted_map = {ans.question_index: ans.answer for ans in submitted_answers}

    correct_count = 0
    wrong_count = 0
    answers_json: List[Dict[str, Any]] = []

    for idx, q_item in enumerate(questions_list):
        student_ans = submitted_map.get(idx, "")
        correct_ans = q_item.get("correct_answer", "")
        is_correct = (
            str(student_ans).strip().upper() == str(correct_ans).strip().upper()
        )

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        answers_json.append(
            {"question_index": idx, "answer": student_ans, "is_correct": is_correct}
        )

    score = (correct_count / total_q * 10.0) if total_q > 0 else 0.0
    return score, correct_count, wrong_count, answers_json
