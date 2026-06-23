import json
from app.agents.base import generate_content_nvidia
from app.agents.daily_planner.schemas import DailyPlannerResponse

def generate_daily_plan(
    subject: str,
    target_score: float,
    days_left: int,
    weekly_plans_list: list,
    study_hours_per_day: float,
    preferred_time: str,
    off_days: list,
    current_date: str
) -> DailyPlannerResponse:
    """
    Agent lập lịch học chi tiết theo ngày dựa trên lộ trình tuần và ràng buộc thời gian rảnh.
    """
    # Định dạng chuỗi ngày nghỉ và danh sách nhiệm vụ để đưa vào prompt
    off_days_str = ", ".join(off_days) if off_days else "Không có"
    tasks_str = "\n".join(f"- {task}" for task in weekly_plans_list)

    # Xây dựng prompt tối giản
    prompt = f"""Mục tiêu:
{target_score} điểm {subject}

Thời gian:
{days_left} ngày

Học:
{study_hours_per_day} giờ/ngày

Khung giờ:
{preferred_time}

Ngày nghỉ:
{off_days_str}

Nhiệm vụ cần phân bổ:
{tasks_str}

Ngày hiện tại bắt đầu lập lịch:
{current_date}

Tạo lịch học cụ thể. Hãy phân chia các nhiệm vụ trên vào các ngày tương ứng bắt đầu từ {current_date}, tuân thủ khung giờ, số giờ học mỗi ngày, và không xếp lịch vào ngày nghỉ.
"""

    messages = [{"role": "user", "content": prompt}]
    
    # Gọi NVIDIA NIM API sinh thời khóa biểu chi tiết dưới dạng JSON
    response_text = generate_content_nvidia(
        messages=messages,
        system_instruction="Bạn là trợ lý ảo hỗ trợ lập lịch học tập chi tiết từng ngày cho học sinh.",
        response_schema=DailyPlannerResponse,
        temperature=0.2
    )

    # Đọc kết quả và chuyển thành Pydantic object
    try:
        data = json.loads(response_text)
        return DailyPlannerResponse(**data)
    except Exception as e:
        raise RuntimeError(f"Lỗi phân tích cú pháp kết quả từ Daily Planner Agent: {e}. Kết quả gốc: {response_text}")
