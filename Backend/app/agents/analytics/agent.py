import json
from app.infrastructure.ai import generate_content_deepseek
from app.agents.analytics.schemas import LearningAnalyticsResponse


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

    prompt = f"""Bạn là chuyên gia giáo dục phân tích học thuật cao cấp.
Nhiệm vụ của bạn là đọc lịch sử kết quả làm bài trắc nghiệm của học sinh (kèm theo các chủ đề điểm mạnh/điểm yếu chi tiết đã được phân tích tự động từ từng bài kiểm tra) để tổng hợp đánh giá điểm mạnh, điểm yếu và xu hướng học lực toàn diện cho môn học này.

Môn học:
{subject_name}

Lịch sử làm bài trắc nghiệm của học sinh:
{history_str if attempts_history else "Chưa có bài kiểm tra nào được hoàn thành."}

Yêu cầu đánh giá:
1. Tổng hợp các chủ đề, khái niệm, kỹ năng yếu cụ thể mà học sinh liên tục làm sai hoặc được đánh giá yếu trong lịch sử làm bài để đưa vào danh sách 'weak_topics' (ví dụ: các chủ đề/khái niệm chi tiết như 'Khai báo mảng 2 chiều', 'Tính nguyên hàm từng phần', 'Chia thì quá khứ đơn'...). Tránh đưa ra các tên chung chung chung như 'Bài kiểm tra 1'.
2. Tổng hợp các chủ đề, khái niệm cụ thể mà học sinh đã làm tốt hoặc được đánh giá mạnh để đưa vào 'strong_topics'.
3. Đánh giá xu hướng học tập gần đây (chọn một trong: 'improving', 'declining', 'stable') và đưa vào 'learning_trend'.
4. Viết nhận xét chi tiết và mang tính cá nhân hóa cao, chỉ rõ lỗ hổng kiến thức cốt lõi và đề xuất phương pháp học tập cải thiện và đưa vào 'ai_feedback'.
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
