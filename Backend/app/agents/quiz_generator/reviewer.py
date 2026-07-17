"""
QC Reviewer Agent.

Reads the original source material (RAG context) and a generated quiz,
then cross-checks question accuracy, uniqueness, explanation clarity, and
distractor quality.  Returns a structured verdict that the orchestrating
service uses to decide whether to accept or regenerate the quiz.
"""

import json
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.infrastructure.ai import generate_content_deepseek

logger = get_logger(__name__)

_SYSTEM_INSTRUCTION = (
    "Bạn là chuyên gia thẩm định đề thi học thuật khắt khe. "
    "Chỉ trả về JSON khớp 100% với schema yêu cầu."
)

_REVIEW_CRITERIA = (
    "⚠️ QUY TẮC THẨM ĐỊNH (TIÊU CHÍ ĐÁNH GIÁ):\n"
    "1. **Tính chính xác**: Đáp án đúng (`correct_answer`) phải hoàn toàn chuẩn xác và có thể "
    "kiểm chứng trực tiếp từ Tài liệu gốc.\n"
    "2. **Không trùng lặp**: Các câu hỏi trong đề không được trùng lặp nội dung hoặc kiểm tra "
    "cùng một ý nghĩa giống nhau.\n"
    "3. **Giải thích chi tiết**: Phần giải thích (`explanation`) phải rõ ràng, chỉ rõ tại sao "
    "chọn phương án đó dựa trên tài liệu.\n"
    "4. **Đáp án nhiễu chất lượng**: Các đáp án sai (distractors) phải hợp lý về mặt logic học "
    "tập, không được viết ngớ ngẩn làm học sinh dễ dàng loại trừ.\n\n"
    "Nếu phát hiện bất kỳ câu hỏi nào vi phạm 4 quy tắc trên, hãy đánh dấu `is_valid` là False, "
    "ghi rõ lý do và hướng dẫn sửa đổi trong `feedback`, và liệt kê index của các câu bị lỗi "
    "(0-indexed) vào `error_question_indices`."
)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class QuizReviewResponse(BaseModel):
    """Structured verdict returned by the QC Reviewer Agent."""

    is_valid: bool = Field(
        ...,
        description=(
            "True nếu toàn bộ câu hỏi đạt chuẩn chất lượng cao. "
            "False nếu phát hiện lỗi cần viết lại."
        ),
    )
    feedback: Optional[str] = Field(
        None,
        description="Nhận xét chi tiết chỉ rõ các điểm lỗi và hướng dẫn cụ thể cách sửa đổi.",
    )
    error_question_indices: List[int] = Field(
        default_factory=list,
        description=(
            "Danh sách các chỉ số index (0-indexed, từ 0 đến 9) "
            "của các câu hỏi bị lỗi cần sinh lại."
        ),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def review_generated_quiz(quiz_data: dict, context: str) -> QuizReviewResponse:
    """
    Cross-check a generated quiz against the source material.

    Evaluates four quality criteria: answer accuracy, question uniqueness,
    explanation clarity, and distractor quality.

    Args:
        quiz_data: The quiz as a plain dict (serialised from ``QuizResponse``).
        context:   The RAG source material used during quiz generation.

    Returns:
        A ``QuizReviewResponse`` with a pass/fail verdict and, on failure,
        structured feedback and the indices of problematic questions.
    """
    quiz_str = json.dumps(quiz_data, ensure_ascii=False, indent=2)

    prompt = (
        "Bạn là một chuyên gia khảo thí chất lượng cao (QC Reviewer Agent).\n"
        "Nhiệm vụ của bạn là thẩm định và đánh giá chất lượng của bộ đề thi trắc nghiệm (Quiz) "
        "dưới đây dựa trên tài liệu gốc (Context) được cung cấp.\n\n"
        f"TÀI LIỆU GỐC (CONTEXT):\n"
        f"----------------------------------\n"
        f"{context}\n"
        f"----------------------------------\n\n"
        f"BỘ ĐỀ THI CẦN THẨM ĐỊNH (QUIZ):\n"
        f"----------------------------------\n"
        f"{quiz_str}\n"
        f"----------------------------------\n\n"
        f"{_REVIEW_CRITERIA}"
    )

    raw_response = generate_content_deepseek(
        messages=[{"role": "user", "content": prompt}],
        system_instruction=_SYSTEM_INSTRUCTION,
        response_schema=QuizReviewResponse,
        temperature=0.1,
    )

    try:
        data = json.loads(raw_response)
        return QuizReviewResponse(**data)
    except Exception as exc:
        # If the LLM response cannot be parsed, fail safe by returning
        # is_valid=False so the orchestrator triggers a regeneration rather
        # than silently accepting a potentially incorrect quiz.
        logger.warning(
            "QC Reviewer: failed to parse review response: %s. Raw (first 200 chars): %s",
            exc,
            raw_response[:200],
        )
        return QuizReviewResponse(
            is_valid=False,
            feedback="Lỗi parse kết quả thẩm định — quiz cần được sinh lại.",
            error_question_indices=[],
        )
