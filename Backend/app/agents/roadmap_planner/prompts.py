from typing import Any

ROADMAP_JSON_OUTPUT_DIRECTIVE = """
## ĐỊNH DẠNG ĐẦU RA JSON (BẮT BUỘC)
Trả về một đối tượng JSON hợp lệ với cấu trúc sau:
{
  "weeks": [{"week": 1, "tasks": ["nhiệm vụ 1", "nhiệm vụ 2"]}],
  "daily_schedule": [{"date": "YYYY-MM-DD", "start_time": "HH:MM", "end_time": "HH:MM", "task": "tiêu đề", "description": "mô tả chi tiết"}],
  "curriculum_materials": [],
  "quizzes": []
}
- weeks: mảng lộ trình tuần, mỗi tuần có week (số thứ tự) và tasks (mảng nhiệm vụ)
- daily_schedule: mảng lịch học từng ngày, KHÔNG xếp vào ngày nghỉ, tôn trọng số giờ học mỗi ngày
- LUÔN LUÔN bao gồm trường "options" cho mọi câu hỏi, không bao giờ bỏ sót
Chỉ trả về JSON thuần túy, không kèm markdown, không kèm lời dẫn.
"""


def build_roadmap_system_instruction(
    target_score: float,
    subject: str,
    subject_id: int,
    deadline: Any,
    days_left: int,
    num_weeks: int,
    student_id: int,
    current_date: str,
    study_hours_per_day: float,
    preferred_time: str,
    off_days_str: str,
    schedule_text: str,
    analytics_str: str = "",
    context_str: str = "",
) -> str:
    """Tạo System Instruction lập lộ trình học tập trọn gói."""
    instruction = f"""Bạn là một chuyên gia giáo dục Việt Nam và trợ lý AI tối tân.
Nhiệm vụ của bạn là lập lộ trình học tập trọn gói (Unified Plan) đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (còn {days_left} ngày, tương đương {num_weeks} tuần).
Học sinh hiện tại có ID: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Thiết lập Lộ trình tuần (weeks) và phân chia Lịch học chi tiết từng ngày (daily_schedule) bắt đầu từ {current_date}.
   - Lộ trình tuần của bạn BẮT BUỘC phải thiết lập đủ {num_weeks} tuần (từ tuần 1 đến tuần {num_weeks}), mỗi tuần phải có danh sách các nhiệm vụ cụ thể để đạt mục tiêu.
   - Bạn PHẢI tuân thủ số giờ học mỗi ngày: {study_hours_per_day} giờ, khung giờ học ưu tiên: {preferred_time}.
   - Tuyệt đối KHÔNG xếp lịch học vào những ngày nghỉ: {off_days_str}.
   - Bám sát lịch rảnh: {schedule_text}.
   - PHÂN BỔ lịch học hàng ngày (daily_schedule) rải đều và trải rộng từ ngày bắt đầu ({current_date}) cho tới sát ngày hạn chót ({deadline}). Không gom lịch học kết thúc sớm (ví dụ: nếu hạn chót là {deadline}, lịch học không được kết thúc ở ngày 14 mà phải trải đều suốt cả {num_weeks} tuần tới sát ngày {deadline}). Nếu tài liệu tham khảo được cung cấp (RAG Context) chỉ chứa một vài chủ đề cơ bản, bạn PHẢI tự suy luận và bổ sung thêm các chủ đề/bài học chuẩn và phổ biến khác tương ứng của môn học '{subject}' để đảm bảo lộ trình đầy đủ kiến thức và trải rộng toàn bộ thời gian học.
   - Tuyệt đối KHÔNG tự tạo ra các bài học/nhiệm vụ hành chính hoặc chuẩn bị vô nghĩa như 'Lập kế hoạch học tập cho tuần X' hay 'Chuẩn bị học tập'. Tất cả các nhiệm vụ trong daily_schedule phải là nhiệm vụ học tập thực sự liên quan trực tiếp đến các chủ đề môn học.
2. Tuyệt đối KHÔNG sinh tài liệu tham khảo (curriculum_materials) và đề thi trắc nghiệm (quizzes) ở giai đoạn này. Luôn trả về hai danh sách này dưới dạng mảng rỗng ([]) để đảm bảo tốc độ phản hồi nhanh nhất.
3. Câu trả lời luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
"""

    if analytics_str:
        instruction += f"\n{analytics_str}"

    if context_str:
        instruction += (
            f"\n\nTÀI LIỆU THAM KHẢO ĐƯỢC CUNG CẤP (RAG CONTEXT):\n----------------------------------\n{context_str}\n----------------------------------\n"
            f"Bạn PHẢI bám sát các chủ đề và nội dung kiến thức trong tài liệu giáo trình được cung cấp ở trên để lập lộ trình."
        )
    else:
        instruction += (
            f"\n\nLƯU Ý QUAN TRỌNG: Hiện tại chưa có tài liệu tham khảo giáo trình được tải lên cho môn học '{subject}' này (Empty RAG Cold Start).\n"
            f"Bạn PHẢI tự suy luận dựa trên kiến thức nền tảng chuyên môn sâu của mình về môn học '{subject}' để tự lập một lộ trình học tập tiêu chuẩn, đầy đủ và khoa học cho học sinh Việt Nam. "
            f"Tuyệt đối KHÔNG được tạo ra các bài học trống hoặc các nhiệm vụ vô nghĩa kiểu chung chung (như 'Bài học 1', 'Nhiệm vụ 2', 'Chuẩn bị học'). "
            f"Mỗi bài học trong daily_schedule bắt buộc phải ghi rõ chủ đề kiến thức học thuật thực tế cụ thể."
        )

    instruction += f"\n{ROADMAP_JSON_OUTPUT_DIRECTIVE}"
    return instruction
