import json
from app.agents.base import generate_content_nvidia
from app.agents.prompts import QUIZ_GENERATOR_SYSTEM_PROMPT
from app.agents.quiz_generator.schemas import QuizResponse

def generate_quiz(
    subject: str,
    topic: str,
    difficulty: str = "medium",
    total_questions: int = 5,
    question_type: str = "mcq",
    context: str = ""
) -> QuizResponse:
    """
    Agent sinh đề kiểm tra tự động dựa trên môn học, chủ đề, độ khó, số câu hỏi yêu cầu và tài liệu RAG.
    Sử dụng NVIDIA NIM sinh JSON có cấu trúc bám sát ngữ cảnh.
    """
    # Định dạng prompt hệ thống
    base_prompt = QUIZ_GENERATOR_SYSTEM_PROMPT.format(
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type=question_type
    )
    
    # Thêm RAG context nếu có
    if context:
        prompt = f"""{base_prompt}

TÀI LIỆU THAM KHẢO ĐƯỢC CUNG CẤP (RAG CONTEXT):
----------------------------------
{context}
----------------------------------
Yêu cầu bắt buộc: Hãy thiết kế các câu hỏi bám sát và dựa hoàn toàn vào các nội dung, kiến thức được đề cập trong Tài liệu tham khảo trên.
"""
    else:
        prompt = base_prompt

    messages = [{"role": "user", "content": prompt}]
    
    # Gọi NVIDIA NIM sinh JSON có cấu trúc
    response_text = generate_content_nvidia(
        messages=messages,
        system_instruction="Bạn là trợ lý AI thiết kế câu hỏi kiểm tra học tập chuẩn chất lượng cao.",
        response_schema=QuizResponse,
        temperature=0.3
    )
    
    try:
        data = json.loads(response_text)
        return QuizResponse(**data)
    except Exception as e:
        raise RuntimeError(f"Lỗi phân tích cú pháp kết quả từ Quiz Generator Agent: {e}. Kết quả gốc: {response_text}")
