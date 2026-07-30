"""
Auto Grading Agent Prompts — Các câu lệnh prompt OCR Multimodal, Chấm điểm bài thi Tự luận & Chẩn đoán học lực.
"""

from typing import Optional

MULTIMODAL_OCR_PROMPT = (
    "Hãy trích xuất và chép lại chính xác, đầy đủ toàn bộ nội dung văn bản, lời giải, câu trả lời tự luận "
    "của học sinh trong tệp tài liệu/hình ảnh này. Chỉ trả về phần văn bản trích xuất được, không bình luận thêm."
)

ESSAY_GRADER_SYSTEM_INSTRUCTION = (
    "Bạn là giám khảo chấm thi tự luận chuyên nghiệp và công tâm. "
    "Hãy so sánh câu trả lời của Học sinh với Đáp án mẫu để chấm điểm."
)

QUIZ_ASSESSMENT_SYSTEM_INSTRUCTION = (
    "Bạn là một Giám khảo & Giáo viên Chuyên môn xuất sắc. "
    "Hãy phân tích chi tiết từng câu hỏi trong đề thi để chỉ ra ĐÍCH XÁC các chủ đề/khái niệm kiến thức học sinh đã nắm vững (strengths) "
    "và các lỗ hổng kiến thức học sinh làm sai (weaknesses)."
)


def build_essay_grader_prompt(
    question_text: str,
    student_answer: str,
    model_answer: str,
    explanation: Optional[str] = None,
) -> str:
    """Xây dựng prompt cho AI Grader chấm điểm bài tự luận."""
    rubric_text = explanation or "Chấm điểm dựa trên độ chính xác, tính logic và mức độ hoàn thành ý trả lời."
    return f"""Hãy đánh giá câu trả lời tự luận dưới đây của Học sinh đối chiếu với Đáp án mẫu.

CÂU HỎI:
{question_text}

ĐÁP ÁN MẪU (MODEL ANSWER):
{model_answer}

TIÊU CHÍ CHẤM ĐIỂM (RUBRIC):
{rubric_text}

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


def build_quiz_assessment_prompt(
    quiz_title: str,
    score: float,
    questions_count: int,
    correct_count: int,
    summary_text: str,
) -> str:
    """Xây dựng prompt cho AI Diagnostic Agent phân tích kết quả toàn bộ bài thi."""
    return f"""Hãy phân tích kết quả bài kiểm tra môn học dưới đây của Học sinh:

THÔNG TIN BÀI THI:
- Tiêu đề đề thi: {quiz_title}
- Điểm số đạt được: {score:.1f}/10
- Số câu đúng: {correct_count}/{questions_count}

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
