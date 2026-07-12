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
        options = q.options or []
        correct_ans = (q.correct_answer or "").strip()

        # 1. Lọc các tùy chọn trùng lặp nội dung (không phân biệt hoa thường và khoảng trắng)
        seen_values = set()
        unique_opts = []
        correct_val = None

        # Tìm giá trị thực tế của đáp án đúng trước khi lọc trùng
        for opt in options:
            if opt.key.strip().upper() == correct_ans.upper():
                correct_val = opt.value.strip().lower()
                break
        else:
            # Fallback: nếu đáp án đúng được sinh dạng text chứ không phải key A/B/C/D
            correct_val = correct_ans.lower()

        for opt in options:
            if not opt or not opt.value:
                continue
            val_clean = opt.value.strip().lower()
            if val_clean not in seen_values:
                seen_values.add(val_clean)
                unique_opts.append(opt)

        # 2. Xây dựng lại danh sách lựa chọn và re-map ký tự key nếu không phải câu True/False
        options_data = []
        new_correct_ans = ""

        is_true_false = (
            getattr(q, "question_type", None) == "true_false" or
            any(opt.key.strip().lower() in ["true", "false", "t", "f"] for opt in unique_opts)
        )
        keys_pool = ["A", "B", "C", "D", "E", "F"]

        for idx, opt in enumerate(unique_opts):
            new_key = opt.key.strip()
            if not is_true_false and idx < len(keys_pool):
                new_key = keys_pool[idx]

            options_data.append({"key": new_key, "value": opt.value})

            # Ánh xạ đáp án đúng sang key mới tương ứng
            if (correct_val and opt.value.strip().lower() == correct_val) or \
               (not correct_val and opt.key.strip().upper() == correct_ans.upper()):
                new_correct_ans = new_key

        if not new_correct_ans and options_data:
            # Fallback nếu không khớp được đáp án nào
            new_correct_ans = options_data[0]["key"]

        questions_json.append(
            {
                "question_text": q.question_text,
                "options": options_data,
                "correct_answer": new_correct_ans,
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
