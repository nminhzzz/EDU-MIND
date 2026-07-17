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


def _collect_constraint_text(
    user_message: Optional[str], history: Optional[list]
) -> str:
    """Gom tin nhắn học sinh dùng để phân tích ngày/thứ bận."""
    text_to_search = ""
    if user_message:
        text_to_search += " " + user_message.lower()
    if history:
        for msg in history:
            if isinstance(msg, dict) and msg.get("role") in ["user", "student"]:
                text_to_search += " " + msg.get("content", "").lower()
            elif (
                hasattr(msg, "role")
                and hasattr(msg, "content")
                and getattr(msg, "role") in ["user", "student"]
            ):
                text_to_search += " " + getattr(msg, "content", "").lower()
    return text_to_search


_VI_WEEKDAY_PATTERNS: list[tuple[str, list[str]]] = [
    ("mon", [r"thứ\s*2", r"thứ\s*hai"]),
    ("tue", [r"thứ\s*3", r"thứ\s*ba"]),
    ("wed", [r"thứ\s*4", r"thứ\s*tư", r"thứ\s*tu"]),
    ("thu", [r"thứ\s*5", r"thứ\s*năm", r"thứ\s*nam"]),
    ("fri", [r"thứ\s*6", r"thứ\s*sáu", r"thứ\s*sau"]),
    ("sat", [r"thứ\s*7", r"thứ\s*bảy", r"thứ\s*bay"]),
    ("sun", [r"chủ\s*nhật", r"\bcn\b"]),
]

_BUSY_CONTEXT = r"bận|nghỉ|không\s+học|đi\s+chơi|không\s+rảnh|có\s+việc"


def get_busy_weekdays(
    user_message: Optional[str], history: Optional[list]
) -> set[str]:
    """Nhận diện thứ trong tuần học sinh báo bận (vd: 'thứ 5 tôi bận đi chơi')."""
    text = _collect_constraint_text(user_message, history)
    busy: set[str] = set()
    for weekday_key, patterns in _VI_WEEKDAY_PATTERNS:
        for pat in patterns:
            if re.search(
                rf"(?:{pat})(?:[\w\s]{{0,30}})(?:{_BUSY_CONTEXT})",
                text,
            ) or re.search(
                rf"(?:{_BUSY_CONTEXT})(?:[\w\s]{{0,30}})(?:{pat})",
                text,
            ):
                busy.add(weekday_key)
                break
            if re.search(rf"(?:mỗi|hàng|tất\s+cả|các)\s+(?:{pat})", text) and re.search(
                _BUSY_CONTEXT, text
            ):
                busy.add(weekday_key)
                break
    return busy


def get_explicitly_available_weekdays(
    user_message: Optional[str], history: Optional[list]
) -> set[str]:
    """Nhận diện thứ trong tuần học sinh muốn học/rảnh học (vd: 'tôi muốn học cả thứ 7')."""
    text = _collect_constraint_text(user_message, history)
    available: set[str] = set()
    for weekday_key, patterns in _VI_WEEKDAY_PATTERNS:
        for pat in patterns:
            # Ví dụ: "học thứ 7", "học cả thứ 7", "học thêm thứ 7", "rảnh thứ 7"
            if re.search(
                rf"(?:học|hoc|rảnh|ranh|thêm|them|học\s+cả|hoc\s+ca)\s+(?:{pat})",
                text,
            ) or re.search(
                rf"(?:{pat})\s+(?:học|hoc|rảnh|ranh|cũng\s+học|cung\s+hoc|được|duoc)",
                text,
            ):
                # Đảm bảo không nằm cạnh từ phủ định
                if not re.search(rf"(?:không|khong|bận|ban)\s+(?:học\s+)?(?:cả\s+)?(?:{pat})", text):
                    available.add(weekday_key)
                    break
    return available


def get_manually_busy_dates(
    user_message: Optional[str], history: Optional[list], current_date: str
) -> set:
    busy_dates = set()
    try:
        current_dt = date.fromisoformat(current_date)
    except Exception:
        current_dt = date.today()

    tomorrow_date = (current_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_tomorrow_date = (current_dt + timedelta(days=2)).strftime("%Y-%m-%d")

    text_to_search = _collect_constraint_text(user_message, history)

    # Từ khóa báo bận / nghỉ
    busy_keywords = r"bận|ban|nghỉ|nghi|nghit|off|không\s+học|khong\s+hoc|không\s+rảnh|khong\s+ranh"
    # Chỉ ngày mai
    tomorrow_keywords = r"mai|ngày\s+mai|ngay\s+mai"
    # Chỉ ngày kia / ngày mốt
    kia_keywords = r"kia|ngày\s+kia|ngay\s+kia|mốt|ngày\s+mốt|ngay\s+mot"

    # 1. Check ngày mai
    if (
        re.search(rf"\b({tomorrow_keywords})\b(?:[\w\s]{{0,15}})\b({busy_keywords})\b", text_to_search)
        or re.search(rf"\b({busy_keywords})\b(?:[\w\s]{{0,15}})\b({tomorrow_keywords})\b", text_to_search)
    ):
        busy_dates.add(tomorrow_date)

    # 2. Check ngày kia
    if (
        re.search(rf"\b({kia_keywords})\b(?:[\w\s]{{0,15}})\b({busy_keywords})\b", text_to_search)
        or re.search(rf"\b({busy_keywords})\b(?:[\w\s]{{0,15}})\b({kia_keywords})\b", text_to_search)
    ):
        busy_dates.add(day_after_tomorrow_date)

    # 3. Check regex tìm khoảng ngày bận dạng từ DD/MM đến DD/MM
    range_patterns = re.findall(
        r"(?:bận|ban|nghỉ|nghi|nghit)\s+từ\s+(?:ngày\s+)?(\d{1,2})[/-](\d{1,2})\s+đến\s+(?:ngày\s+)?(\d{1,2})[/-](\d{1,2})",
        text_to_search,
    )
    for d1_str, m1_str, d2_str, m2_str in range_patterns:
        try:
            year = current_dt.year
            d1 = date(year, int(m1_str), int(d1_str))
            d2 = date(year, int(m2_str), int(d2_str))
            if d1 < current_dt:
                d1 = date(year + 1, int(m1_str), int(d1_str))
                d2 = date(year + 1, int(m2_str), int(d2_str))
            if d2 < d1:
                d2 = date(d2.year + 1, d2.month, d2.day)
            delta = d2 - d1
            for i in range(delta.days + 1):
                busy_dates.add((d1 + timedelta(days=i)).strftime("%Y-%m-%d"))
        except Exception:
            pass

    # 4. Check regex tìm ngày bận dạng DD/MM hoặc DD-MM
    date_patterns = re.findall(
        r"(?:bận|ban|nghỉ|nghi|nghit)(?:\s+ngày)?\s+(\d{1,2})[/-](\d{1,2})", text_to_search
    )
    for day_str, month_str in date_patterns:
        try:
            day = int(day_str)
            month = int(month_str)
            year = current_dt.year
            d = date(year, month, day)
            if d < current_dt:
                d = date(year + 1, month, day)
            busy_dates.add(d.strftime("%Y-%m-%d"))
        except Exception:
            pass

    # 5. Check regex tìm ngày bận dạng YYYY-MM-DD
    iso_patterns = re.findall(
        r"(?:bận|ban|nghỉ|nghi|nghit)(?:\s+ngày)?\s+(\d{4}-\d{2}-\d{2})", text_to_search
    )
    for iso_str in iso_patterns:
        busy_dates.add(iso_str)

    return busy_dates


def _reassign_daily_schedule_dates(
    data: dict,
    *,
    current_dt: date,
    deadline: date,
    off_days: list,
    history: Optional[list],
    current_date: str,
) -> None:
    """Gán lại ngày học theo lịch rảnh, ngày bận và thứ bận học sinh nêu."""
    if "daily_schedule" not in data or not isinstance(data["daily_schedule"], list):
        return

    filtered_schedule = [
        item
        for item in data["daily_schedule"]
        if isinstance(item, dict)
        and item.get("task")
        and item.get("task").strip()
    ]

    manually_busy_dates = get_manually_busy_dates(None, history, current_date)
    busy_weekdays = get_busy_weekdays(None, history)
    explicitly_available = get_explicitly_available_weekdays(None, history)
    
    # Hiệu lực ngày nghỉ = (ngày nghỉ mặc định + thứ bận mới) - thứ muốn học
    effective_off_days = (set(off_days or []) | busy_weekdays) - explicitly_available

    available_dates = []
    temp_dt = current_dt
    needed_days = len(filtered_schedule)
    while len(available_dates) < needed_days:
        if temp_dt > deadline + timedelta(days=90):
            raise ValueError(
                "Không tìm thấy đủ ngày học trống trong lịch rảnh của bạn. "
                "Vui lòng giảm bớt ngày bận hoặc lùi ngày hạn chót xa hơn để lộ trình khả thi."
            )
        weekday_key = temp_dt.strftime("%a").lower()
        date_str = temp_dt.strftime("%Y-%m-%d")
        if weekday_key not in effective_off_days and date_str not in manually_busy_dates:
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
    history: Optional[list] = None,
    db_mongo: Any = None,
) -> UnifiedGoalPlanResponse:
    """
    Super Agent hợp nhất Giai đoạn 1, 2 và 3.
    Thực hiện RAG để tìm giáo trình -> Gọi DeepSeek V4 Flash lập lịch tuần, lịch ngày, và tạo đề thi thử trọn gói.
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
Nhiệm vụ của bạn là lập và tinh chỉnh lộ trình học tập trọn gói (Unified Plan) đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (còn {days_left} ngày, tương đương {num_weeks} tuần).
Học sinh hiện tại có ID: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Thiết lập Lộ trình tuần (weeks) và phân chia Lịch học chi tiết từng ngày (daily_schedule) bắt đầu từ {current_date}.
   - Lộ trình tuần của bạn BẮT BUỘC phải thiết lập đủ {num_weeks} tuần (từ tuần 1 đến tuần {num_weeks}), mỗi tuần phải có danh sách các nhiệm vụ cụ thể để đạt mục tiêu.
   - Bạn PHẢI tuân thủ số giờ học mỗi ngày: {study_hours_per_day} giờ, khung giờ học ưu tiên: {preferred_time}.
   - Tuyệt đối KHÔNG xếp lịch học vào những ngày nghỉ: {off_days_str}.
   - Bám sát lịch rảnh: {schedule_text}.
   - PHÂN BỔ lịch học hàng ngày (daily_schedule) rải đều và trải rộng từ ngày bắt đầu ({current_date}) cho tới sát ngày hạn chót ({deadline}). Không gom lịch học kết thúc sớm (ví dụ: nếu hạn chót là {deadline}, lịch học không được kết thúc ở ngày 14 mà phải trải đều suốt cả {num_weeks} tuần tới sát ngày {deadline}). Nếu tài liệu tham khảo được cung cấp (RAG Context) chỉ chứa một vài chủ đề cơ bản, bạn PHẢI tự suy luận và bổ sung thêm các chủ đề/bài học chuẩn và phổ biến khác tương ứng của môn học '{subject}' để đảm bảo lộ trình đầy đủ kiến thức và trải rộng toàn bộ thời gian học.
   - Tuyệt đối KHÔNG tự tạo ra các bài học/nhiệm vụ hành chính hoặc chuẩn bị vô nghĩa như 'Lập kế hoạch học tập cho tuần X' hay 'Chuẩn bị học tập'. Tất cả các nhiệm vụ trong daily_schedule phải là nhiệm vụ học tập thực sự liên quan trực tiếp đến các chủ đề môn học.
   - ĐẶC BIỆT CHÚ Ý YÊU CẦU TINH CHỈNH: Xem kỹ tin nhắn phản hồi của học sinh. Nếu học sinh báo bận vào một ngày cụ thể (ví dụ: ngày mai, ngày kia, hoặc một ngày cụ thể nào đó) HOẶC một thứ trong tuần (ví dụ: thứ 5, thứ 7), bạn TUYỆT ĐỐI không được xếp lịch học (`daily_schedule`) vào ngày/thứ đó.
     * Lưu ý ngày hiện tại là {current_date}. 
     * "Ngày mai" (tomorrow) tương ứng với ngày {tomorrow_date_str}.
     * "Ngày kia" (day after tomorrow) tương ứng với ngày {day_after_tomorrow_str}.
     Nếu học sinh nói 'ngày mai bận' hoặc 'mai bận' thì tuyệt đối KHÔNG xếp lịch học vào ngày {tomorrow_date_str}.
2. Tuyệt đối KHÔNG sinh tài liệu tham khảo (curriculum_materials) và đề thi trắc nghiệm (quizzes) ở giai đoạn này. Luôn trả về hai danh sách này dưới dạng mảng rỗng ([]) để đảm bảo tốc độ phản hồi nhanh nhất.
3. Khi học sinh phản hồi tinh chỉnh, hãy phân tích kỹ yêu cầu của học sinh để điều chỉnh lịch học một cách hợp lý (dời lịch học sang ngày khác, thay đổi giờ, v.v.), đồng thời giữ nguyên các phần nội dung môn học khác đã được thống nhất.
4. Câu trả lời luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
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

    # Xây dựng danh sách messages
    messages = []
    if history:
        if history[0]["role"] in ["assistant", "model"]:
            messages.append(
                {
                    "role": "user",
                    "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'.",
                }
            )
        for msg in history:
            role = "assistant" if msg["role"] in ["model", "assistant"] else "user"
            messages.append({"role": role, "content": msg["content"]})
    else:
        messages.append(
            {
                "role": "user",
                "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'.",
            }
        )

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
            history=history,
            current_date=current_date,
        )
        return UnifiedGoalPlanResponse(**data)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích cú pháp kết quả từ Unified Super Agent: {e}. "
            f"Kết quả gốc: {response_text[:500]}"
        )


async def generate_unified_plan_stream(
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
    history: Optional[list] = None,
    db_mongo: Any = None,
):
    """
    Streaming version: yields progress messages while building plan, then returns result.
    Tránh parse JSON từ stream (dễ lỗi) → dùng sync call để parse chính xác.
    """
    yield ("progress", "📚 Đang tìm tài liệu tham khảo...")

    context_str = ""
    if db_mongo is not None:
        try:
            materials = await vector_search_materials(
                db_mongo=db_mongo, query_text=subject, subject_id=subject_id, top_k=3
            )
            if materials:
                context_parts = []
                for i, m in enumerate(materials):
                    content = m["content"]
                    if len(content) > 500:
                        content = content[:500] + "..."
                    context_parts.append(
                        f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{content}"
                    )
                context_str = "\n\n".join(context_parts)
                yield ("progress", f"✅ Tìm thấy {len(materials)} tài liệu tham khảo.")
        except Exception as e:
            logger.warning("RAG vector search failed: %s", e)

    yield ("progress", "📊 Đang phân tích học lực...")

    try:
        current_dt = date.fromisoformat(current_date)
    except Exception:
        current_dt = date.today()

    # Tính số ngày còn lại kể từ ngày bắt đầu lộ trình
    days_left = (deadline - current_dt).days
    if days_left <= 0:
        days_left = 30
    num_weeks = (days_left + 6) // 7

    tomorrow_dt = current_dt + timedelta(days=1)
    tomorrow_date_str = tomorrow_dt.strftime("%Y-%m-%d")
    day_after_tomorrow_dt = current_dt + timedelta(days=2)
    day_after_tomorrow_str = day_after_tomorrow_dt.strftime("%Y-%m-%d")

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
    schedule_text = f"Ngày rảnh: {format_available_schedule(available_schedule)}"

    analytics_str = ""
    try:
        analytics = get_student_analytics_db(student_id, subject_id)
        recent_attempts = get_recent_attempts_db(student_id, limit=5)
        analytics_str = "\n--- HỌC LỰC THỰC TẾ ---\n"
        analytics_str += f"Điểm TB: {analytics['average_score']}/10 ({analytics['quizzes_completed']} bài quiz)\n"
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
        analytics_str += (
            f"Phần yếu: {', '.join(weak_topics) if weak_topics else 'Chưa phát hiện'}\n"
        )
        analytics_str += f"Phần mạnh: {', '.join(strong_topics) if strong_topics else 'Chưa phát hiện'}\n"
        if recent_attempts:
            analytics_str += "Lịch sử bài làm gần nhất:\n"
            for att in recent_attempts:
                analytics_str += f"  - {att['quiz_title']}: {att['score']}/10\n"
    except Exception as e:
        logger.warning("Failed to query student analytics: %s", e)

    yield ("progress", "🤖 Đang soạn lộ trình học tập...")

    system_instruction = f"""Bạn là một chuyên gia giáo dục Việt Nam và trợ lý AI tối tân.
Nhiệm vụ của bạn là lập và tinh chỉnh lộ trình học tập trọn gói (Unified Plan) đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (còn {days_left} ngày, tương đương {num_weeks} tuần).
Học sinh hiện tại có ID: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Thiết lập Lộ trình tuần (weeks) và phân chia Lịch học chi tiết từng ngày (daily_schedule) bắt đầu từ {current_date}.
   - Lộ trình tuần của bạn BẮT BUỘC phải thiết lập đủ {num_weeks} tuần (từ tuần 1 đến tuần {num_weeks}), mỗi tuần phải có danh sách các nhiệm vụ cụ thể để đạt mục tiêu.
   - Bạn PHẢI tuân thủ số giờ học mỗi ngày: {study_hours_per_day} giờ, khung giờ học ưu tiên: {preferred_time}.
   - Tuyệt đối KHÔNG xếp lịch học vào những ngày nghỉ: {off_days_str}.
   - Bám sát lịch rảnh: {schedule_text}.
   - PHÂN BỔ lịch học hàng ngày (daily_schedule) rải đều và trải rộng từ ngày bắt đầu ({current_date}) cho tới sát ngày hạn chót ({deadline}). Không gom lịch học kết thúc sớm (ví dụ: nếu hạn chót là {deadline}, lịch học không được kết thúc ở ngày 14 mà phải trải đều suốt cả {num_weeks} tuần tới sát ngày {deadline}). Nếu tài liệu tham khảo được cung cấp (RAG Context) chỉ chứa một vài chủ đề cơ bản, bạn PHẢI tự suy luận và bổ sung thêm các chủ đề/bài học chuẩn và phổ biến khác tương ứng của môn học '{subject}' để đảm bảo lộ trình đầy đủ kiến thức và trải rộng toàn bộ thời gian học.
   - Tuyệt đối KHÔNG tự tạo ra các bài học/nhiệm vụ hành chính hoặc chuẩn bị vô nghĩa như 'Lập kế hoạch học tập cho tuần X' hay 'Chuẩn bị học tập'. Tất cả các nhiệm vụ trong daily_schedule phải là nhiệm vụ học tập thực sự liên quan trực tiếp đến các chủ đề môn học.
   - ĐẶC BIỆT CHÚ Ý YÊU CẦU TINH CHỈNH: Xem kỹ tin nhắn phản hồi của học sinh. Nếu học sinh báo bận vào một ngày cụ thể (ví dụ: ngày mai, ngày kia, hoặc một ngày cụ thể nào đó) HOẶC một thứ trong tuần (ví dụ: thứ 5, thứ 7), bạn TUYỆT ĐỐI không được xếp lịch học (`daily_schedule`) vào ngày/thứ đó.
     * Lưu ý ngày hiện tại là {current_date}. 
     * "Ngày mai" (tomorrow) tương ứng với ngày {tomorrow_date_str}.
     * "Ngày kia" (day after tomorrow) tương ứng với ngày {day_after_tomorrow_str}.
     Nếu học sinh nói 'ngày mai bận' hoặc 'mai bận' thì tuyệt đối KHÔNG xếp lịch học vào ngày {tomorrow_date_str}.
2. Tuyệt đối KHÔNG sinh tài liệu tham khảo (curriculum_materials) và đề thi trắc nghiệm (quizzes) ở giai đoạn này. Luôn trả về hai danh sách này dưới dạng mảng rỗng ([]) để đảm bảo tốc độ phản hồi nhanh nhất.
3. Khi học sinh phản hồi tinh chỉnh, hãy phân tích kỹ yêu cầu của học sinh để điều chỉnh lịch học một cách hợp lý (dời lịch học sang ngày khác, thay đổi giờ, v.v.), đồng thời giữ nguyên các phần nội dung môn học khác đã được thống nhất.
4. Câu trả lời luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
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

    system_instruction += """

## ĐỊNH DẠNG ĐẦU RA JSON (BẮT BUỘC)
Trả về một đối tượng JSON hợp lệ với cấu trúc sau:
{
  "weeks": [{"week": 1, "tasks": ["nhiệm vụ 1", "nhiệm vụ 2"]}],
  "daily_schedule": [{"date": "YYYY-MM-DD", "start_time": "HH:MM", "end_time": "HH:MM", "task": "tiêu đề", "description": "mô tả chi tiết"}],
  "curriculum_materials": [],
  "quizzes": []
}
- weeks: mảng lộ trình tuần, mỗi tuần có week (số thứ tự) và tasks (mảng nhiệm vụ dạng chuỗi văn bản thuần)
- daily_schedule: mảng lịch học từng ngày, KHÔNG xếp vào ngày nghỉ, tôn trọng số giờ học mỗi ngày
- curriculum_materials: LUÔN để danh sách rỗng []
- quizzes: LUÔN để danh sách rỗng []
- LUÔN LUÔN bao gồm trường "options" cho mọi câu hỏi, không bao giờ bỏ sót
Chỉ trả về JSON thuần túy, không kèm markdown, không kèm lời dẫn."""

    messages = []
    if history:
        if history[0]["role"] in ["assistant", "model"]:
            messages.append(
                {
                    "role": "user",
                    "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'.",
                }
            )
        for msg in history:
            role = "assistant" if msg["role"] in ["model", "assistant"] else "user"
            messages.append({"role": role, "content": msg["content"]})
    else:
        messages.append(
            {
                "role": "user",
                "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'.",
            }
        )

    yield ("progress", "⏳ Đang sinh lộ trình...")

    try:
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                generate_content_deepseek,
                messages=messages,
                system_instruction=system_instruction,
                response_schema=UnifiedGoalPlanResponse,
                temperature=0.2,
                tools=None,
            ),
            timeout=180.0,
        )
        logger.debug("sync call done, got %d chars", len(response_text))
    except asyncio.TimeoutError:
        yield ("error", "Quá thời gian tạo lộ trình, hãy thử lại.")
        return

    try:
        data = _parse_llm_roadmap_json(response_text)
        data = normalize_roadmap_keys(data)
        _reassign_daily_schedule_dates(
            data,
            current_dt=current_dt,
            deadline=deadline,
            off_days=off_days,
            history=history,
            current_date=current_date,
        )
        plan = UnifiedGoalPlanResponse(**data)
        yield ("complete", plan)
    except ValueError as exc:
        yield ("error", str(exc))
    except Exception as e:
        yield ("error", f"Lỗi xử lý lộ trình: {str(e)[:150]}")
