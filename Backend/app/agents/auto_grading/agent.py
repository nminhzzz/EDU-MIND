"""
Auto Grading Agent: Logic chấm điểm bài tự luận bằng DeepSeek AI & OCR hình ảnh/PDF bằng Gemini Vision.
"""

import base64
import json
import mimetypes
from typing import Optional, Tuple

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai import generate_content_deepseek

logger = get_logger(__name__)


def extract_multimodal_file(file_path: str, mime_type: str) -> str:
    """Gọi Gemini Vision API trích xuất chữ viết tay/in trong ảnh hoặc file PDF quét."""
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
    AI Grader Agent chấm điểm câu tự luận của học sinh đối chiếu với đáp án mẫu và tiêu chí Rubric.
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


def generate_quiz_assessment_with_ai(
    quiz_title: str,
    questions_list: list,
    answers_json: list,
    score: float,
    correct_count: int,
    wrong_count: int,
) -> dict:
    """
    AI Diagnostic Agent: Phân tích kết quả bài thi của học sinh, đưa ra Lời phê tổng thể cá nhân hóa,
    điểm mạnh và lỗ hổng kiến thức cần củng cố.
    """
    system_instruction = (
        "Bạn là một Giám khảo & Giáo viên Chuyên môn xuất sắc. "
        "Hãy phân tích chi tiết từng câu hỏi trong đề thi để chỉ ra ĐÍCH XÁC các chủ đề/khái niệm kiến thức học sinh đã nắm vững (strengths) "
        "và các lỗ hổng kiến thức học sinh làm sai (weaknesses)."
    )

    q_summaries = []
    for ans in answers_json:
        idx = ans.get("question_index", 0)
        q_obj = questions_list[idx] if idx < len(questions_list) else {}
        q_text = q_obj.get("question_text", f"Câu {idx + 1}")
        student_ans = ans.get("answer", "")
        is_correct = ans.get("is_correct", False)
        correct_ans = q_obj.get("correct_answer", "")
        explanation = q_obj.get("explanation", "")
        
        q_summaries.append(
            f"Câu {idx + 1}: \"{q_text}\"\n"
            f"  - Học sinh chọn: '{student_ans}' | Kết quả: {'ĐÚNG' if is_correct else 'SAI (Đáp án đúng: ' + str(correct_ans) + ')'}\n"
            f"  - Giải thích kiến thức: {explanation}"
        )

    summary_text = "\n\n".join(q_summaries)
    prompt = f"""Hãy phân tích kết quả bài kiểm tra môn học dưới đây của Học sinh:

THÔNG TIN BÀI THI:
- Tiêu đề đề thi: {quiz_title}
- Điểm số đạt được: {score:.1f}/10
- Số câu đúng: {correct_count}/{len(questions_list)}

CHI TIẾT CÁC CÂU HỎI VÀ KẾT QUẢ BÀI LÀM:
{summary_text}

YÊU CẦU ĐÁNH GIÁ CHUYÊN SÂU:
1. `overall_feedback`: Viết Lời phê chuyên môn cá nhân hóa (2-3 câu), nhận xét sát thực tế về tư duy và mức độ làm bài của học sinh đối với đề thi '{quiz_title}'.
2. `strengths`: Danh sách 1-3 khái niệm/kiến thức CỤ THỂ MÔN HỌC mà học sinh đã làm đúng và thể hiện nắm vững.
3. `weaknesses`: Danh sách 1-3 khái niệm/lỗ hổng kiến thức CỤ THỂ DỰA TRÊN CÁC CÂU SAI mà học sinh còn nhầm lẫn.
4. `recommendation`: Lời khuyên bước ôn tập cụ thể tiếp theo.

Trả về dữ liệu dưới định dạng JSON:
{{
  "overall_feedback": "Lời phê ngắn gọn...",
  "strengths": ["Kiến thức đúng 1"],
  "weaknesses": ["Lỗ hổng kiến thức 1"],
  "recommendation": "Gợi ý ôn tập..."
}}"""

    try:
        class QuizAssessmentSchema(BaseModel):
            overall_feedback: str = Field(description="Lời phê cá nhân hóa từ AI Tutor")
            strengths: list[str] = Field(default_factory=list, description="Danh sách điểm mạnh")
            weaknesses: list[str] = Field(default_factory=list, description="Danh sách lỗ hổng kiến thức")
            recommendation: str = Field(description="Lời khuyên bước tiếp theo")

        response_text = generate_content_deepseek(
            messages=[{"role": "user", "content": prompt}],
            system_instruction=system_instruction,
            response_schema=QuizAssessmentSchema,
            temperature=0.3,
        )

        cleaned_response = response_text.strip()
        start_idx = cleaned_response.find("{")
        end_idx = cleaned_response.rfind("}")
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            cleaned_response = cleaned_response[start_idx : end_idx + 1]

        data = json.loads(cleaned_response)
        return {
            "overall_feedback": data.get("overall_feedback", "Chúc mừng bạn đã hoàn thành bài thi!"),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "recommendation": data.get("recommendation", "Hãy xem lại giải thích chi tiết phía dưới nhé."),
        }
    except Exception as exc:
        logger.warning("AI Diagnostic Feedback Agent failed: %s", exc)

    if score >= 8.0:
        overall = f"Xuất sắc! Bạn đạt {score:.1f}/10 và nắm rất vững kiến thức bài thi '{quiz_title}'."
        strengths = [f"Nắm vững các khái niệm trong bài '{quiz_title}'"]
        weaknesses = []
        rec = "Tiếp tục duy trì phong độ cho các bài thi tiếp theo!"
    elif score >= 5.0:
        overall = f"Khá tốt! Bạn đạt {score:.1f}/10. Hãy rà soát lại các câu làm sai để củng cố kiến thức."
        strengths = ["Nắm được phần lớn lý thuyết căn bản"]
        weaknesses = ["Còn sót một số câu vận dụng thực hành"]
        rec = "Nên luyện lại các câu hỏi vừa làm sai để đạt điểm tối đa."
    else:
        overall = f"Bạn đạt {score:.1f}/10. Đừng nản lòng, hãy xem lại lời giải chi tiết để bổ sung lỗ hổng kiến thức."
        strengths = []
        weaknesses = ["Cần ôn tập lại lý thuyết nền tảng"]
        rec = "Hãy đọc lại bài giảng và thử làm lại bài thi này nhé."

    return {
        "overall_feedback": overall,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": rec,
    }

