import json
from app.infrastructure.ai import generate_content_deepseek
from app.agents.analytics.schemas import LearningAnalyticsResponse


def evaluate_learning_performance(
    subject_name: str, attempts_history: list
) -> LearningAnalyticsResponse:
    """
    Agent phân tích kết quả lịch sử làm bài thi để tự động đánh giá học lực của học sinh.
    """
    # Định dạng lịch sử làm bài để đưa vào prompt
    history_str = "\n".join(
        f"- Chủ đề/Chương: {a['topic']} | Điểm số đạt được: {a['score']}/10 | Đạt yêu cầu: {'Có' if a['is_passed'] else 'Không'}"
        for a in attempts_history
    )

    prompt = f"""Bạn là chuyên gia giáo dục phân tích học thuật cao cấp.
Nhiệm vụ của bạn là đọc lịch sử kết quả làm bài trắc nghiệm của học sinh và đánh giá điểm mạnh, điểm yếu và xu hướng học lực.

Môn học:
{subject_name}

Lịch sử làm bài trắc nghiệm của học sinh:
{history_str if attempts_history else "Chưa có bài kiểm tra nào được hoàn thành."}

Yêu cầu đánh giá:
1. Xác định các chủ đề yếu (điểm trung bình dưới 6.5) và đưa vào 'weak_topics'.
2. Xác định các chủ đề mạnh (điểm trung bình từ 8.0 trở lên) và đưa vào 'strong_topics'.
3. Đánh giá xu hướng học tập gần đây (chọn một trong: 'improving', 'declining', 'stable') và đưa vào 'learning_trend'.
4. Viết nhận xét chi tiết, chỉ ra lỗ hổng kiến thức và đề xuất phương pháp học tập cải thiện và đưa vào 'ai_feedback'.
"""

    messages = [{"role": "user", "content": prompt}]

    # Gọi DeepSeek API
    response_text = generate_content_deepseek(
        messages=messages,
        system_instruction="Bạn là trợ lý AI chuyên gia giáo dục phân tích học thuật cao cấp.",
        response_schema=LearningAnalyticsResponse,
        temperature=0.2,
    )

    try:
        data = json.loads(response_text)
        return LearningAnalyticsResponse(**data)
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích cú pháp đánh giá học lực từ AI: {e}. Kết quả gốc: {response_text}"
        )
