import json
from datetime import date
from typing import Optional, Dict, Any

from app.agents.base import generate_content_nvidia
from app.agents.goal_planner.schemas import GoalPlannerResponse
from app.agents.tools.db_tools import get_student_analytics_db, get_recent_attempts_db


def generate_goal_plan(
    subject: str,
    target_score: float,
    deadline: date,
    student_id: int,
    subject_id: int,
    available_schedule: Optional[Dict[str, Any]] = None,
    history: Optional[list[dict[str, str]]] = None
) -> GoalPlannerResponse:
    """
    Agent sinh lộ trình học theo tuần dựa trên mục tiêu, deadline,
    lịch rảnh của học sinh bằng cách tự động gọi các tool truy vấn DB để tự đánh giá học lực.
    Hỗ trợ nhận history tin nhắn để thảo luận tinh chỉnh lộ trình.

    Args:
        subject: Tên môn học (vd: "Triết học")
        target_score: Điểm mong muốn (vd: 8.0)
        deadline: Hạn chót đạt mục tiêu
        student_id: ID học sinh
        subject_id: ID môn học
        available_schedule: Lịch rảnh học sinh {"mon": true, "tue": false, ...}
        history: Lịch sử tin nhắn hội thoại nháp [{"role": "user", "content": "..."}, ...]

    Returns:
        GoalPlannerResponse — lộ trình học chia theo tuần
    """
    # Tính số ngày còn lại
    today = date.today()
    days_left = (deadline - today).days
    if days_left <= 0:
        days_left = 30  # Giá trị dự phòng nếu deadline ở quá khứ

    # Chuyển available_schedule thành text dễ đọc cho AI
    WEEKDAY_NAMES = {
        "mon": "Thứ 2", "tue": "Thứ 3", "wed": "Thứ 4",
        "thu": "Thứ 5", "fri": "Thứ 6", "sat": "Thứ 7", "sun": "Chủ nhật"
    }
    if available_schedule:
        free_days = [WEEKDAY_NAMES.get(k, k) for k, v in available_schedule.items() if v]
        schedule_text = f"Ngày rảnh học: {', '.join(free_days) if free_days else 'Linh hoạt'}"
    else:
        schedule_text = "Lịch học: Linh hoạt tất cả các ngày"

    # Định nghĩa System Instruction
    system_instruction = f"""Bạn là chuyên gia giáo dục Việt Nam.
Nhiệm vụ của bạn là lập và tinh chỉnh lộ trình tự học đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (tức là còn {days_left} ngày).
Học sinh hiện tại có ID là: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Bạn PHẢI sử dụng các công cụ (Tools) được cung cấp để tự động tra cứu lịch sử điểm số và phân tích học lực thực tế của học sinh này từ cơ sở dữ liệu ở lượt đầu tiên (nếu lịch sử chat chưa có thông tin).
   * Lưu ý: Bạn chỉ được phép sử dụng các công cụ có sẵn trong danh sách cung cấp (`get_student_analytics_db` và `get_recent_attempts_db`). Tuyệt đối KHÔNG tự bịa ra, KHÔNG giả lập bất kỳ công cụ nào khác.
2. Nếu học sinh đưa ra ý kiến phản hồi về lộ trình trước đó (ở các tin nhắn sau trong lịch sử chat), bạn hãy đọc kỹ lịch sử hội thoại để giữ nguyên các phần học sinh đồng ý, và chỉ chỉnh sửa các phần học sinh yêu cầu thay đổi trong lộ trình JSON.
3. Câu trả lời của bạn luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
4. Lộ trình của bạn phải bám sát lịch rảnh học tập của học sinh: {schedule_text}
"""

    prompt = f"""Hãy lập lộ trình học tập đạt mục tiêu {target_score}/10 cho môn học '{subject}'."""

    # Xây dựng danh sách messages gửi cho NVIDIA
    messages = []
    if history:
        for msg in history:
            role = "assistant" if msg["role"] in ["model", "assistant"] else "user"
            messages.append({"role": role, "content": msg["content"]})
        # Thêm prompt yêu cầu lập/tinh chỉnh lộ trình
        messages.append({"role": "user", "content": prompt})
    else:
        messages.append({"role": "user", "content": prompt})

    # Gọi trực tiếp NVIDIA NIM API qua OpenAI SDK
    response_text = generate_content_nvidia(
        messages=messages,
        system_instruction=system_instruction,
        response_schema=GoalPlannerResponse,
        temperature=0.2,
        tools=[get_student_analytics_db, get_recent_attempts_db]
    )

    # Parse kết quả thành Pydantic object
    try:
        data = json.loads(response_text)
        return GoalPlannerResponse(**data)
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích kết quả từ Goal Planner Agent: {e}. "
            f"Kết quả gốc: {response_text}"
        )
