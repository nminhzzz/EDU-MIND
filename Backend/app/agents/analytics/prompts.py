"""
Learning Analytics Agent Prompts — Các câu lệnh prompt phân tích học lực và xu hướng học tập.
"""

ANALYTICS_SYSTEM_INSTRUCTION = "Bạn là trợ lý AI chuyên gia giáo dục phân tích học thuật cao cấp."


def build_analytics_prompt(subject_name: str, history_str: str) -> str:
    """Xây dựng prompt phân tích đánh giá lịch sử làm bài của học sinh."""
    return f"""Bạn là chuyên gia giáo dục phân tích học thuật cao cấp.
Nhiệm vụ của bạn là đọc lịch sử kết quả làm bài trắc nghiệm của học sinh (kèm theo các chủ đề điểm mạnh/điểm yếu chi tiết đã được phân tích tự động từ từng bài kiểm tra) để tổng hợp đánh giá điểm mạnh, điểm yếu và xu hướng học lực toàn diện cho môn học này.

Môn học:
{subject_name}

Lịch sử làm bài trắc nghiệm của học sinh:
{history_str if history_str else "Chưa có bài kiểm tra nào được hoàn thành."}

Yêu cầu đánh giá:
1. Tổng hợp các chủ đề, khái niệm, kỹ năng yếu cụ thể mà học sinh liên tục làm sai hoặc được đánh giá yếu trong lịch sử làm bài để đưa vào danh sách 'weak_topics' (ví dụ: các chủ đề/khái niệm chi tiết như 'Khai báo mảng 2 chiều', 'Tính nguyên hàm từng phần', 'Chia thì quá khứ đơn'...). Tránh đưa ra các tên chung chung như 'Bài kiểm tra 1'.
2. Tổng hợp các chủ đề, khái niệm cụ thể mà học sinh đã làm tốt hoặc được đánh giá mạnh để đưa vào 'strong_topics'.
3. Đánh giá xu hướng học tập gần đây (chọn một trong: 'improving', 'declining', 'stable') và đưa vào 'learning_trend'.
4. Viết nhận xét chi tiết và mang tính cá nhân hóa cao, chỉ rõ lỗ hổng kiến thức cốt lõi và đề xuất phương pháp học tập cải thiện và đưa vào 'ai_feedback'.
"""
