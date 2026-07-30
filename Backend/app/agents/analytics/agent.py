from app.infrastructure.ai import generate_content_deepseek
from app.agents.analytics.schemas import LearningAnalyticsResponse
from app.agents.analytics.prompts import (
    ANALYTICS_SYSTEM_INSTRUCTION,
    build_analytics_prompt,
)


def evaluate_learning_performance(
    subject_name: str, attempts_history: list
) -> LearningAnalyticsResponse:
    """
    Agent phân tích kết quả lịch sử làm bài thi để tự động đánh giá học lực của học sinh.
    """
    # Định dạng lịch sử làm bài kèm theo chi tiết đánh giá tự động của từng bài thi
    history_lines = []
    for a in attempts_history:
        line = f"- Bài kiểm tra: {a['topic']} | Điểm: {a['score']}/10 | Đạt: {'Có' if a['is_passed'] else 'Không'}"
        ai_ass = a.get("ai_assessment")
        if ai_ass and isinstance(ai_ass, dict):
            strengths = ai_ass.get("strengths", [])
            weaknesses = ai_ass.get("weaknesses", [])
            if strengths:
                line += f" | Điểm mạnh cụ thể: {', '.join(strengths)}"
            if weaknesses:
                line += f" | Điểm yếu cụ thể: {', '.join(weaknesses)}"
        history_lines.append(line)
    
    history_str = "\n".join(history_lines)
    prompt = build_analytics_prompt(subject_name=subject_name, history_str=history_str)

    messages = [{"role": "user", "content": prompt}]

    # Gọi DeepSeek API
    response_text = generate_content_deepseek(
        messages=messages,
        system_instruction=ANALYTICS_SYSTEM_INSTRUCTION,
        response_schema=LearningAnalyticsResponse,
        temperature=0.2,
    )

    try:
        cleaned = response_text.strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and start < end:
            cleaned = cleaned[start : end + 1]
        data = json.loads(cleaned)
        return LearningAnalyticsResponse(**data)
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích cú pháp đánh giá học lực từ AI: {e}. Kết quả gốc: {response_text}"
        )
