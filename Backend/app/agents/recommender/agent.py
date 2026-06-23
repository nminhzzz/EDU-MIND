from app.agents.base import generate_content_nvidia
from typing import Optional

def generate_recommendation(
    subject_name: str,
    topic_name: str,
    score: float,
    weak_topics: Optional[list] = None
) -> str:
    """
    AI Agent đóng vai trò Gia sư phân tích lỗi sai và đề xuất nội dung ôn tập cụ thể
    dựa trên kết quả bài kiểm tra của học sinh.
    """
    # Định dạng các chủ đề yếu (nếu có)
    weak_topics_str = ""
    if weak_topics:
        weak_topics_str = "Các chủ đề yếu trước đây của học sinh:\n" + "\n".join(
            f"- {t.get('topic', t)} (Mức độ nắm vững: {t.get('score', 0)}/10)"
            for t in weak_topics
        )

    prompt = f"""Bạn là một Gia sư AI chuyên nghiệp và tận tâm tại Việt Nam.
Một học sinh vừa hoàn thành bài thi trắc nghiệm môn {subject_name} về chủ đề "{topic_name}".
Kết quả đạt được: {score}/10 điểm (Chưa đạt yêu cầu tối ưu).

{weak_topics_str}

Hãy phân tích kết quả trên và biên soạn một **Đề xuất ôn tập chi tiết** (khoảng 100 - 200 từ) gửi cho học sinh để bồi dưỡng kiến thức.
Đề xuất phải bao gồm:
1. Nhận xét ngắn gọn về kết quả thi của chủ đề này (động viên nhưng thẳng thắn chỉ ra lỗ hổng).
2. Liệt kê các nội dung cốt lõi của chủ đề "{topic_name}" học sinh cần xem lại ngay.
3. Đưa ra 2-3 hành động học tập cụ thể, thực tế (ví dụ: đọc lại trang slide, làm lại các câu trắc nghiệm sai, vẽ sơ đồ tư duy).

Yêu cầu: Viết bằng tiếng Việt, giọng điệu chuyên nghiệp, tích cực và mang tính hành động cao. Trả về nội dung đề xuất dạng văn bản thuần (có định dạng markdown đẹp, không có bao ngoài json).
"""

    messages = [{"role": "user", "content": prompt}]
    
    # Gọi NVIDIA NIM API
    response_text = generate_content_nvidia(
        messages=messages,
        system_instruction="Bạn là trợ lý AI chuyên nghiệp phân tích kết quả học tập và đề xuất ôn tập.",
        temperature=0.3
    )

    return response_text.strip()
