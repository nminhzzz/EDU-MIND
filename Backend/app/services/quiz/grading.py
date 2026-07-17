"""
Quiz grading and AI question normalisation helpers.
"""

import base64
import json
import mimetypes
import os
from typing import Any, Dict, List, Optional, Tuple

import docx
import httpx
import pdfplumber
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai import generate_content_deepseek
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
                return _extract_multimodal_file(file_path, "application/pdf")
            return text
        except Exception as exc:
            return f"[Lỗi trích xuất file PDF: {str(exc)}]"

    # 4. Images
    if ext in [".png", ".jpg", ".jpeg"]:
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "image/jpeg"
        return _extract_multimodal_file(file_path, mime_type)

    return f"[Lỗi: Định dạng file '{ext}' không được hỗ trợ để trích xuất text]"


def _extract_multimodal_file(file_path: str, mime_type: str) -> str:
    """Gọi Gemini API trích xuất chữ viết tay/in trong ảnh hoặc file PDF quét."""
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY chưa được thiết lập. Không thể chạy OCR.")
        return "[Lỗi OCR: GEMINI_API_KEY chưa cấu hình]"

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        base64_data = base64.b64encode(file_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hãy trích xuất và chép lại chính xác, đầy đủ toàn bộ nội dung văn bản, lời giải, câu trả lời tự luận của học sinh trong tệp tài liệu/hình ảnh này. Chỉ trả về phần văn bản trích xuất được, không bình luận thêm."
                        },
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": base64_data
                            }
                        }
                    ]
                }
            ]
        }

        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        return "[Không trích xuất được văn bản từ tệp]"
    except Exception as exc:
        logger.error("Multimodal OCR failed: %s", exc)
        return f"[Lỗi trích xuất OCR: {str(exc)}]"


def grade_essay_with_ai(
    question_text: str,
    student_answer: str,
    model_answer: str,
    explanation: Optional[str] = None,
) -> Tuple[float, str]:
    """
    AI Grader chấm điểm câu tự luận của học sinh đối chiếu với đáp án mẫu.
    """
    system_instruction = (
        "Bạn là giám khảo chấm thi tự luận chuyên nghiệp và công tâm. "
        "Hãy so sánh câu trả lời của Học sinh với Đáp án mẫu để chấm điểm."
    )

    prompt = f"""Hãy đánh giá câu trả lời tự luận dưới đây của Học sinh đối chiếu với Đáp án mẫu.

CÂU HỎI:
{question_text}

ĐÁP ÁN MẪU (MODEL ANSWER):
{model_answer}

TIÊU CHÍ CHẤM ĐIỂM (RUBRIC):
{explanation or "Chấm điểm dựa trên độ chính xác, tính logic và mức độ hoàn thành ý trả lời."}

BÀI LÀM CỦA HỌC SINH (TRÍCH XUẤT TỪ FILE):
{student_answer}

YÊU CẦU:
Chỉ ra điểm số (từ 0.0 đến 10.0) và viết một nhận xét ngắn gọn (dưới 3 câu) về bài làm của học sinh.
Trả về dữ liệu dưới định dạng JSON sau:
{{
    "score": 8.5,
    "feedback": "Nhận xét của bạn..."
}}
"""
    try:
        class EssayGradeSchema(BaseModel):
            score: float = Field(description="Điểm số thang 10, từ 0.0 đến 10.0")
            feedback: str = Field(description="Lời phê ngắn gọn, nhận xét ưu khuyết điểm")

        response_text = generate_content_deepseek(
            messages=[{"role": "user", "content": prompt}],
            system_instruction=system_instruction,
            response_schema=EssayGradeSchema,
            temperature=0.2,
        )

        cleaned_response = response_text.strip()
        start_idx = cleaned_response.find("{")
        end_idx = cleaned_response.rfind("}")
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            cleaned_response = cleaned_response[start_idx : end_idx + 1]

        data = json.loads(cleaned_response)
        score = float(data.get("score", 0.0))
        feedback = data.get("feedback", "").strip()
        return min(10.0, max(0.0, score)), feedback
    except Exception as exc:
        logger.warning("AI Essay Grader failed: %s. Using default pass.", exc)
        return 5.0, f"[AI Grader Error: {str(exc)}]"


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
            # Gọi AI chấm điểm bài tự luận
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
