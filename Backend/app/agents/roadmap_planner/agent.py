import asyncio
import json
import re
from datetime import date, timedelta
from typing import Any, Dict, Optional

from app.infrastructure.ai import generate_content_deepseek, generate_content_deepseek_stream
from app.agents.tools.db_tools import get_recent_attempts_db, get_student_analytics_db
from app.core.logging import get_logger
from app.schemas.unified_goal import UnifiedGoalPlanResponse
from app.services.embedding_service import vector_search_materials

logger = get_logger(__name__)


def _parse_llm_roadmap_json(response_text: str) -> dict:
    """Parse JSON roadmap from LLM output with clear errors for empty/invalid payloads."""
    if not response_text or not response_text.strip():
        raise ValueError(
            "AI không trả về nội dung lộ trình (phản hồi rỗng). "
            "Vui lòng thử lại sau vài giây."
        )

    cleaned_response = response_text
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        cleaned_response = response_text[start_idx : end_idx + 1]

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError as exc:
        preview = response_text[:200].replace("\n", " ")
        raise ValueError(
            "AI trả về dữ liệu không phải JSON hợp lệ. "
            "Vui lòng gửi lại yêu cầu tinh chỉnh hoặc tạo lộ trình mới."
        ) from exc


def normalize_roadmap_keys(data: Any) -> Any:
    """
    Chuẩn hóa các key trong dữ liệu JSON từ LLM (TC-07) để tránh lỗi Pydantic Validation.
    Tự động sửa các lỗi chính tả, kiểu lạc chữ hoa chữ thường (camelCase, kebab-case) sang snake_case.
    """
    if isinstance(data, list):
        return [normalize_roadmap_keys(item) for item in data]
    elif isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            normalized_key = k
            # Sửa các key viết lệch phổ biến trong daily_schedule và weeks
            k_lower = k.lower().replace("-", "_")
            if k_lower in ["start_time", "starttime"]:
                normalized_key = "start_time"
            elif k_lower in ["end_time", "endtime"]:
                normalized_key = "end_time"
            elif k_lower in ["task_name", "taskname", "title"]:
                normalized_key = "task"
            elif k_lower in ["desc", "detail", "task_description", "taskdescription"]:
                normalized_key = "description"

            new_data[normalized_key] = normalize_roadmap_keys(v)
        return new_data
    return data


def _reassign_daily_schedule_dates(
    data: dict,
    *,
    current_dt: date,
    deadline: date,
    off_days: list,
) -> None:
    """Gán lại ngày học theo lịch rảnh và ngày nghỉ mặc định."""
    if "daily_schedule" not in data or not isinstance(data["daily_schedule"], list):
        return

    filtered_schedule = [
        item
        for item in data["daily_schedule"]
        if isinstance(item, dict)
        and item.get("task")
        and item.get("task").strip()
    ]

    effective_off_days = set(off_days or [])

    available_dates = []
    temp_dt = current_dt
    needed_days = len(filtered_schedule)
    while len(available_dates) < needed_days:
        if temp_dt > deadline + timedelta(days=90):
            raise ValueError(
                "Không tìm thấy đủ ngày học trống trong lịch rảnh của bạn. "
                "Vui lòng lùi ngày hạn chót xa hơn để lộ trình khả thi."
            )
        weekday_key = temp_dt.strftime("%a").lower()
        date_str = temp_dt.strftime("%Y-%m-%d")
        if weekday_key not in effective_off_days:
            available_dates.append(date_str)
        temp_dt += timedelta(days=1)

    for i, item in enumerate(filtered_schedule):
        item["date"] = available_dates[i]
    data["daily_schedule"] = filtered_schedule


def format_available_schedule(schedule: Optional[Dict[str, Any]]) -> str:
    if not schedule:
        return "Linh hoạt tất cả các ngày"
    weekday_names = {
        "mon": "Thứ 2",
        "tue": "Thứ 3",
        "wed": "Thứ 4",
        "thu": "Thứ 5",
        "fri": "Thứ 6",
        "sat": "Thứ 7",
        "sun": "Chủ nhật",
    }
    slot_names = {"morning": "Sáng", "afternoon": "Chiều", "evening": "Tối"}
    parts = []
    for day_key in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        if day_key in schedule:
            val = schedule[day_key]
            if isinstance(val, dict):
                free_slots = []
                for s in ["morning", "afternoon", "evening"]:
                    if val.get(s):
                        start = val.get(f"{s}_start")
                        end = val.get(f"{s}_end")
                        if start and end:
                            free_slots.append(f"{slot_names[s]} ({start}-{end})")
                        else:
                            free_slots.append(slot_names[s])
                if len(free_slots) == 3:
                    parts.append(f"{weekday_names[day_key]} (Cả ngày)")
                elif free_slots:
                    parts.append(f"{weekday_names[day_key]} ({', '.join(free_slots)})")
            elif val is True:
                parts.append(f"{weekday_names[day_key]} (Cả ngày)")
    if not parts:
        return "Linh hoạt tất cả các ngày"
    return "; ".join(parts)


async def generate_unified_plan(
    subject: str,
    target_score: float,
    deadline: date,
    student_id: int,
    subject_id: int,
    study_hours_per_day: float,
    preferred_time: str,
    off_days: list,
    current_date: str,
    available_schedule: Optional[Dict[str, Any]] = None,
    db_mongo: Any = None,
) -> UnifiedGoalPlanResponse:
    """
    Super Agent hợp nhất Giai đoạn 1, 2 và 3.
    Thực hiện RAG để tìm giáo trình -> Gọi DeepSeek V4 Flash lập lịch tuần, lịch ngày.
    """
    # 1. RAG: Tìm tài liệu học tập trong MongoDB
    context_str = ""
    logger.debug("roadmap_planner: Starting RAG vector search in MongoDB...")
    if db_mongo is not None:
        try:
            materials = await vector_search_materials(
                db_mongo=db_mongo, query_text=subject, subject_id=subject_id, top_k=3
            )
            if materials:
                context_str = "\n\n".join(
                    f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{m['content']}"
                    for i, m in enumerate(materials)
                )
        except Exception as e:
            logger.warning("RAG vector search failed: %s", e)

    try:
        current_dt = date.fromisoformat(current_date)
    except Exception:
        current_dt = date.today()

    # 2. Xử lý ngày nghỉ và lịch rảnh
    WEEKDAY_VN = {
        "mon": "Thứ Hai",
        "tue": "Thứ Ba",
        "wed": "Thứ Tư",
        "thu": "Thứ Năm",
        "fri": "Thứ Sáu",
        "sat": "Thứ Bảy",
        "sun": "Chủ Nhật",
    }
    off_dates_list = []
    temp_dt = current_dt
    while temp_dt <= deadline:
        weekday_key = temp_dt.strftime("%a").lower()
        if weekday_key in off_days:
            vn_name = WEEKDAY_VN.get(weekday_key, weekday_key)
            off_dates_list.append(f"{temp_dt.strftime('%Y-%m-%d')} ({vn_name})")
        temp_dt += timedelta(days=1)

    off_days_str = ", ".join(off_dates_list) if off_dates_list else "Không có"
    schedule_text = (
        f"Ngày rảnh học trong tuần: {format_available_schedule(available_schedule)}"
    )

    # Tính số ngày còn lại kể từ ngày bắt đầu lộ trình
    days_left = (deadline - current_dt).days
    if days_left <= 0:
        days_left = 30
    num_weeks = (days_left + 6) // 7

    tomorrow_dt = current_dt + timedelta(days=1)
    tomorrow_date_str = tomorrow_dt.strftime("%Y-%m-%d")
    day_after_tomorrow_dt = current_dt + timedelta(days=2)
    day_after_tomorrow_str = day_after_tomorrow_dt.strftime("%Y-%m-%d")

    # 3. Tra cứu học lực và điểm số của học sinh từ MySQL trực tiếp trong Python
    analytics_str = ""
    logger.debug("roadmap_planner: Querying MySQL for student analytics...")
    try:
        analytics = get_student_analytics_db(student_id, subject_id)
        recent_attempts = get_recent_attempts_db(student_id, limit=5)

        analytics_str = "\n--- THÔNG TIN HỌC LỰC THỰC TẾ CỦA HỌC SINH TỪ DATABASE ---\n"
        analytics_str += f"Điểm trung bình hiện tại: {analytics['average_score']}/10 (Số bài quiz đã hoàn thành: {analytics['quizzes_completed']})\n"
        weak_topics = (
            [
                t.get("topic", str(t)) if isinstance(t, dict) else str(t)
                for t in analytics["weak_topics"]
            ]
            if analytics["weak_topics"]
            else []
        )
        strong_topics = (
            [
                t.get("topic", str(t)) if isinstance(t, dict) else str(t)
                for t in analytics["strong_topics"]
            ]
            if analytics["strong_topics"]
            else []
        )
        analytics_str += f"Các phần yếu cần khắc phục: {', '.join(weak_topics) if weak_topics else 'Chưa phát hiện'}\n"
        analytics_str += f"Các phần mạnh đã vững: {', '.join(strong_topics) if strong_topics else 'Chưa phát hiện'}\n"
        ai_feedback = (analytics.get("ai_feedback") or "")[:200]
        analytics_str += f"Nhận xét của AI trước đó: {ai_feedback}\n"

        if recent_attempts:
            analytics_str += "Lịch sử làm bài trắc nghiệm gần nhất:\n"
            for att in recent_attempts:
                analytics_str += f"  - Đề: {att['quiz_title']} | Điểm: {att['score']}/10 | Số câu đúng: {att['correct_count']}/{att['correct_count']+att['wrong_count']}\n"
    except Exception as e:
        logger.warning("Failed to query student analytics from MySQL: %s", e)

    # 4. Định nghĩa System Instruction
    system_instruction = f"""Bạn là một chuyên gia giáo dục Việt Nam và trợ lý AI tối tân.
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
        system_instruction += f"\n{analytics_str}"

    if context_str:
        system_instruction += (
            f"\n\nTÀI LIỆU THAM KHẢO ĐƯỢC CUNG CẤP (RAG CONTEXT):\n----------------------------------\n{context_str}\n----------------------------------\n"
            f"Bạn PHẢI bám sát các chủ đề và nội dung kiến thức trong tài liệu giáo trình được cung cấp ở trên để lập lộ trình."
        )
    else:
        system_instruction += (
            f"\n\nLƯU Ý QUAN TRỌNG: Hiện tại chưa có tài liệu tham khảo giáo trình được tải lên cho môn học '{subject}' này (Empty RAG Cold Start).\n"
            f"Bạn PHẢI tự suy luận dựa trên kiến thức nền tảng chuyên môn sâu của mình về môn học '{subject}' để tự lập một lộ trình học tập tiêu chuẩn, đầy đủ và khoa học cho học sinh Việt Nam. "
            f"Tuyệt đối KHÔNG được tạo ra các bài học trống hoặc các nhiệm vụ vô nghĩa kiểu chung chung (như 'Bài học 1', 'Nhiệm vụ 2', 'Chuẩn bị học'). "
            f"Mỗi bài học trong daily_schedule bắt buộc phải ghi rõ chủ đề kiến thức học thuật thực tế cụ thể."
        )

    # Thêm hướng dẫn output JSON chi tiết (tránh đổ cả schema Pydantic vào prompt)
    system_instruction += """

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
Chỉ trả về JSON thuần túy, không kèm markdown, không kèm lời dẫn."""

    messages = [
        {
            "role": "user",
            "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'.",
        }
    ]

    # Gọi NVIDIA NIM API qua OpenAI SDK để sinh JSON có cấu trúc
    logger.debug("roadmap_planner: Calling generate_content_deepseek...")
    response_text = generate_content_deepseek(
        messages=messages,
        system_instruction=system_instruction,
        response_schema=UnifiedGoalPlanResponse,
        temperature=0.2,
        tools=None,
    )

    try:
        data = _parse_llm_roadmap_json(response_text)
        data = normalize_roadmap_keys(data)
        _reassign_daily_schedule_dates(
            data,
            current_dt=current_dt,
            deadline=deadline,
            off_days=off_days,
        )
        return UnifiedGoalPlanResponse(**data)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích cú pháp kết quả từ Unified Super Agent: {e}. "
            f"Kết quả gốc: {response_text[:500]}"
        )
    off_dates_list = []
    temp_dt = current_dt
    while temp_dt <= deadline:
        weekday_key = temp_dt.strftime("%a").lower()
        if weekday_key in off_days:
            vn_name = WEEKDAY_VN.get(weekday_key, weekday_key)
            off_dates_list.append(f"{temp_dt.strftime('%Y-%m-%d')} ({vn_name})")
        temp_dt += timedelta(days=1)

    off_days_str = ", ".join(off_dates_list) if off_dates_list else "Không có"
    schedule_text = f"Ngày rảnh: {format_available_schedule(available_schedule)}"


def generate_lecture_material_agent(
    plan_title: str,
    system_instruction: str,
    context_str: Optional[str] = None,
) -> str:
    """
    AI Lecture Generation Agent: Generates detailed, structured lecture materials (markdown)
    for a study plan using RAG context or general domain knowledge.
    """
    if context_str:
        user_message = (
            f"Dưới đây là các đoạn văn bản trích xuất từ giáo trình/tài liệu tham khảo liên quan:\n\n"
            f"{context_str}\n\n"
            f"Dựa trên các tài liệu trên và kiến thức chuyên môn của bạn, hãy viết tài liệu bài học "
            f"hoàn chỉnh, sâu sắc và cực kỳ chi tiết cho chủ đề: \"{plan_title}\"."
        )
    else:
        user_message = (
            f"Hãy viết một bài giảng/tài liệu học tập hoàn chỉnh, chi tiết và sâu sắc cho chủ đề: \"{plan_title}\"."
        )

    return generate_content_deepseek(
        messages=[{"role": "user", "content": user_message}],
        system_instruction=system_instruction,
        temperature=0.3,
    )


