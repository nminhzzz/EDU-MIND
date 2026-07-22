"""
Quiz grading and AI question normalisation helpers.
"""

import mimetypes
import os
from typing import Any, Dict, List, Optional, Tuple

import docx
import pdfplumber

from app.core.logging import get_logger
from app.agents.auto_grading import (
    grade_essay_with_ai,
    extract_multimodal_file,
    generate_quiz_assessment_with_ai,
)
from app.schemas.quiz_attempt import QuizAttemptAnswer

logger = get_logger(__name__)

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
        q_type = getattr(q, "question_type", "mcq")
        if q_type == "essay":
            questions_json.append(
                {
                    "question_text": q.question_text,
                    "question_type": "essay",
                    "options": [],
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
            )
            continue

        options = q.options or []
        correct_ans = (q.correct_answer or "").strip()

        # 1. Lọc các tùy chọn trùng lặp nội dung
        seen_values = set()
        unique_opts = []
        correct_val = None

        for opt in options:
            if opt.key.strip().upper() == correct_ans.upper():
                correct_val = opt.value.strip().lower()
                break
        else:
            correct_val = correct_ans.lower()

        for opt in options:
            if not opt or not opt.value:
                continue
            val_clean = opt.value.strip().lower()
            if val_clean not in seen_values:
                seen_values.add(val_clean)
                unique_opts.append(opt)

        # 2. Xây dựng lại danh sách lựa chọn và re-map ký tự key
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

            if (correct_val and opt.value.strip().lower() == correct_val) or \
               (not correct_val and opt.key.strip().upper() == correct_ans.upper()):
                new_correct_ans = new_key

        if not new_correct_ans and options_data:
            new_correct_ans = options_data[0]["key"]

        questions_json.append(
            {
                "question_text": q.question_text,
                "question_type": q_type,
                "options": options_data,
                "correct_answer": new_correct_ans,
                "explanation": q.explanation,
            }
        )

    return questions_json


def extract_text_from_file(file_path: str) -> str:
    """Trích xuất nội dung văn bản từ các tệp tin bài làm tự luận (PDF, Word, TXT, Hình ảnh)."""
    if not os.path.exists(file_path):
        logger.error("Không tìm thấy file: %s", file_path)
        return f"[Lỗi: Không tìm thấy tệp {file_path}]"

    ext = os.path.splitext(file_path)[1].lower()

    # 1. Plain Text
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as exc:
            return f"[Lỗi đọc file TXT: {str(exc)}]"

    # 2. Word document
    if ext == ".docx":
        try:
            doc = docx.Document(file_path)
            paragraphs_text = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs_text).strip()
        except Exception as exc:
            return f"[Lỗi trích xuất file Word: {str(exc)}]"

    # 3. PDF
    if ext == ".pdf":
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages]).strip()

            # Nếu là PDF quét (scanned PDF - không có text)
            if not text:
                return extract_multimodal_file(file_path, "application/pdf")
            return text
        except Exception as exc:
            return f"[Lỗi trích xuất file PDF: {str(exc)}]"

    # 4. Images
    if ext in [".png", ".jpg", ".jpeg"]:
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "image/jpeg"
        return extract_multimodal_file(file_path, mime_type)

    return f"[Lỗi: Định dạng file '{ext}' không được hỗ trợ để trích xuất text]"


def grade_submission(
    questions_list: List[Dict[str, Any]],
    submitted_answers: List[QuizAttemptAnswer],
    essay_file_path: Optional[str] = None,
) -> Tuple[float, int, int, List[Dict[str, Any]]]:
    """
    Chấm điểm bài thi tự động. Hỗ trợ câu hỏi Trắc nghiệm và Tự luận (qua file bài làm).
    Trả về (score, correct_count, wrong_count, answers_json).
    """
    total_q = len(questions_list)
    submitted_map = {ans.question_index: ans.answer for ans in submitted_answers}

    # Trích xuất văn bản từ bài làm tự luận nếu có
    student_essay_text = ""
    if essay_file_path:
        logger.info("Chạy trích xuất text tự luận từ file: %s", essay_file_path)
        student_essay_text = extract_text_from_file(essay_file_path)

    correct_count = 0
    wrong_count = 0
    answers_json: List[Dict[str, Any]] = []
    total_points = 0.0

    for idx, q_item in enumerate(questions_list):
        q_type = q_item.get("question_type", "mcq")

        if q_type == "essay":
            correct_ans = q_item.get("correct_answer", "")
            # Gọi AI Agent chấm điểm bài tự luận
            if student_essay_text.strip():
                score_val, feedback_val = grade_essay_with_ai(
                    question_text=q_item.get("question_text", ""),
                    student_answer=student_essay_text,
                    model_answer=correct_ans,
                    explanation=q_item.get("explanation"),
                )
            else:
                score_val, feedback_val = 0.0, "Không tìm thấy nội dung bài làm tự luận (chưa upload file)."

            is_correct = score_val >= 5.0
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1

            total_points += score_val
            answers_json.append(
                {
                    "question_index": idx,
                    "answer": student_essay_text if student_essay_text else "[Chưa upload bài làm]",
                    "is_correct": is_correct,
                    "score": score_val,
                    "feedback": feedback_val,
                    "essay_file_path": essay_file_path,
                }
            )
        else:
            # Trắc nghiệm (MCQ) hoặc Đúng/Sai (True/False)
            student_ans = submitted_map.get(idx, "")
            correct_ans = q_item.get("correct_answer", "")
            is_correct = (
                str(student_ans).strip().upper() == str(correct_ans).strip().upper()
            )

            score_val = 10.0 if is_correct else 0.0
            if is_correct:
                correct_count += 1
                total_points += 10.0
            else:
                wrong_count += 1

            answers_json.append(
                {"question_index": idx, "answer": student_ans, "is_correct": is_correct}
            )

    score = (total_points / total_q) if total_q > 0 else 0.0
    return score, correct_count, wrong_count, answers_json


def generate_ai_attempt_feedback(
    quiz_title: str,
    questions_list: List[Dict[str, Any]],
    answers_json: List[Dict[str, Any]],
    score: float,
    correct_count: int,
    wrong_count: int,
) -> Dict[str, Any]:
    """
    Delegate AI Diagnostic Feedback generation to the Agent Layer.
    """
    return generate_quiz_assessment_with_ai(
        quiz_title=quiz_title,
        questions_list=questions_list,
        answers_json=answers_json,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
    )

