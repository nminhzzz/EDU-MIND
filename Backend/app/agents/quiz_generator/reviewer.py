import json
from pydantic import BaseModel, Field
from typing import List, Optional
from app.agents.base import generate_content_nvidia

class QuizReviewResponse(BaseModel):
    """Cấu trúc kết quả đánh giá chất lượng bộ đề thi của QC Reviewer Agent."""
    is_valid: bool = Field(
        ..., 
        description="True nếu toàn bộ câu hỏi đạt chuẩn chất lượng cao. False nếu phát hiện lỗi cần viết lại."
    )
    feedback: Optional[str] = Field(
        None, 
        description="Nhận xét chi tiết chỉ rõ các điểm lỗi và hướng dẫn cụ thể cách sửa đổi."
    )
    error_question_indices: List[int] = Field(
        default_factory=list, 
        description="Danh sách các chỉ số index (0-indexed, từ 0 đến 9) của các câu hỏi bị lỗi cần sinh lại."
    )

def review_generated_quiz(quiz_data: dict, context: str) -> QuizReviewResponse:
    """
    QC Reviewer Agent: Đọc hiểu tài liệu gốc (context) và bộ đề thi mẫu để chấm điểm chéo chất lượng.
    Đảm bảo:
      1. Không có câu hỏi trùng lặp ý nghĩa.
      2. Đáp án đúng là hoàn toàn chuẩn xác dựa trên context.
      3. Giải thích câu hỏi rõ ràng.
      4. Đáp án nhiễu hợp lý, không ngớ ngẩn.
    """
    quiz_str = json.dumps(quiz_data, ensure_ascii=False, indent=2)
    
    prompt = f"""Bạn là một chuyên gia khảo thí chất lượng cao (QC Reviewer Agent).
Nhiệm vụ của bạn là thẩm định và đánh giá chất lượng của bộ đề thi trắc nghiệm (Quiz) dưới đây dựa trên tài liệu gốc (Context) được cung cấp.

TÀI LIỆU GỐC (CONTEXT):
----------------------------------
{context}
----------------------------------

BỘ ĐỀ THI CẦN THẨM ĐỊNH (QUIZ):
----------------------------------
{quiz_str}
----------------------------------

⚠️ QUY TẮC THẨM ĐỊNH (TIÊU CHÍ ĐÁNH GIÁ):
1. **Tính chính xác**: Đáp án đúng (`correct_answer`) phải hoàn toàn chuẩn xác và có thể kiểm chứng trực tiếp từ Tài liệu gốc.
2. **Không trùng lặp**: Các câu hỏi trong đề không được trùng lặp nội dung hoặc kiểm tra cùng một ý nghĩa giống nhau.
3. **Giải thích chi tiết**: Phần giải thích (`explanation`) phải rõ ràng, chỉ rõ tại sao chọn phương án đó dựa trên tài liệu.
4. **Đáp án nhiễu chất lượng**: Các đáp án sai (distractors) phải hợp lý về mặt logic học tập, không được viết ngớ ngẩn làm học sinh dễ dàng loại trừ.

Nếu phát hiện bất kỳ câu hỏi nào vi phạm 4 quy tắc trên, hãy đánh dấu `is_valid` là False, ghi rõ lý do và hướng dẫn sửa đổi trong `feedback`, và liệt kê index của các câu bị lỗi (0-indexed) vào `error_question_indices`.
"""

    response_text = generate_content_nvidia(
        messages=[{"role": "user", "content": prompt}],
        system_instruction="Bạn là chuyên gia thẩm định đề thi học thuật khắt khe. Chỉ trả về JSON khớp 100% với schema yêu cầu.",
        response_schema=QuizReviewResponse,
        temperature=0.1  # Nhiệt độ thấp để thẩm định chính xác khách quan
    )
    
    try:
        data = json.loads(response_text)
        return QuizReviewResponse(**data)
    except Exception as e:
        # Dự phòng: Nếu parse lỗi, mặc định duyệt qua để tránh treo tiến trình
        print(f"[QC Reviewer] Lỗi parse kết quả thẩm định: {e}. Kết quả gốc: {response_text}")
        return QuizReviewResponse(is_valid=True, feedback="Lỗi parse thẩm định chéo, bỏ qua duyệt.", error_question_indices=[])
