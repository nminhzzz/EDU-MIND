import json
import asyncio
from datetime import date
from typing import Optional, Dict, Any

from app.agents.base import generate_content_nvidia, generate_content_nvidia_stream
from app.schemas.unified_goal import UnifiedGoalPlanResponse
from app.agents.tools.db_tools import get_student_analytics_db, get_recent_attempts_db
from app.services.embedding_service import vector_search_materials

def format_available_schedule(schedule: Optional[Dict[str, Any]]) -> str:
    if not schedule:
        return "Linh hoạt tất cả các ngày"
    weekday_names = {
        "mon": "Thứ 2", "tue": "Thứ 3", "wed": "Thứ 4",
        "thu": "Thứ 5", "fri": "Thứ 6", "sat": "Thứ 7", "sun": "Chủ nhật"
    }
    slot_names = {
        "morning": "Sáng",
        "afternoon": "Chiều",
        "evening": "Tối"
    }
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
    db_mongo: Any = None
) -> UnifiedGoalPlanResponse:
    """
    Super Agent hợp nhất Giai đoạn 1, 2 và 3.
    Thực hiện RAG để tìm giáo trình -> Gọi Llama 3.1 70B lập lịch tuần, lịch ngày, và tạo đề thi thử trọn gói.
    """
    # 1. RAG: Tìm tài liệu học tập trong MongoDB
    context_str = ""
    print("-> unified_agent: Starting RAG vector search in MongoDB...")
    if db_mongo is not None:
        try:
            materials = await vector_search_materials(
                db_mongo=db_mongo,
                query_text=subject,
                subject_id=subject_id,
                top_k=3
            )
            if materials:
                context_str = "\n\n".join(
                    f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{m['content']}"
                    for i, m in enumerate(materials)
                )
        except Exception as e:
            print(f"[Warning] RAG vector search failed: {e}")

    # 2. Xử lý ngày nghỉ và lịch rảnh
    off_days_str = ", ".join(off_days) if off_days else "Không có"
    schedule_text = f"Ngày rảnh học trong tuần: {format_available_schedule(available_schedule)}"

    # Tính số ngày còn lại
    today = date.today()
    days_left = (deadline - today).days
    if days_left <= 0:
        days_left = 30

    # 3. Tra cứu học lực và điểm số của học sinh từ MySQL trực tiếp trong Python
    analytics_str = ""
    print("-> unified_agent: Querying MySQL for student analytics...")
    try:
        analytics = get_student_analytics_db(student_id, subject_id)
        recent_attempts = get_recent_attempts_db(student_id, limit=5)
        
        analytics_str = "\n--- THÔNG TIN HỌC LỰC THỰC TẾ CỦA HỌC SINH TỪ DATABASE ---\n"
        analytics_str += f"Điểm trung bình hiện tại: {analytics['average_score']}/10 (Số bài quiz đã hoàn thành: {analytics['quizzes_completed']})\n"
        analytics_str += f"Các phần yếu cần khắc phục: {', '.join(analytics['weak_topics']) if analytics['weak_topics'] else 'Chưa phát hiện'}\n"
        analytics_str += f"Các phần mạnh đã vững: {', '.join(analytics['strong_topics']) if analytics['strong_topics'] else 'Chưa phát hiện'}\n"
        ai_feedback = (analytics.get('ai_feedback') or "")[:200]
        analytics_str += f"Nhận xét của AI trước đó: {ai_feedback}\n"
        
        if recent_attempts:
            analytics_str += "Lịch sử làm bài trắc nghiệm gần nhất:\n"
            for att in recent_attempts:
                analytics_str += f"  - Đề: {att['quiz_title']} | Điểm: {att['score']}/10 | Số câu đúng: {att['correct_count']}/{att['correct_count']+att['wrong_count']}\n"
    except Exception as e:
        print(f"[Warning] Failed to query student analytics from MySQL: {e}")

    # 4. Định nghĩa System Instruction
    system_instruction = f"""Bạn là một chuyên gia giáo dục Việt Nam và trợ lý AI tối tân.
Nhiệm vụ của bạn là lập và tinh chỉnh lộ trình học tập trọn gói (Unified Plan) đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (còn {days_left} ngày).
Học sinh hiện tại có ID: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Thiết lập Lộ trình tuần (weeks) và phân chia Lịch học chi tiết từng ngày (daily_schedule) bắt đầu từ {current_date}.
   - Bạn PHẢI tuân thủ số giờ học mỗi ngày: {study_hours_per_day} giờ, khung giờ học ưu tiên: {preferred_time}.
   - Tuyệt đối KHÔNG xếp lịch học vào những ngày nghỉ: {off_days_str}.
   - Bám sát lịch rảnh: {schedule_text}.
2. Tuyệt đối KHÔNG sinh tài liệu tham khảo (curriculum_materials) và đề thi trắc nghiệm (quizzes) ở giai đoạn này. Luôn trả về hai danh sách này dưới dạng mảng rỗng ([]) để đảm bảo tốc độ phản hồi nhanh nhất.
3. Nếu học sinh phản hồi tinh chỉnh, hãy đọc kỹ lịch sử chat (history) để giữ nguyên các phần đã đồng ý và chỉ điều chỉnh các phần học sinh yêu cầu trong JSON kết quả.
4. Câu trả lời luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
"""

    if analytics_str:
        system_instruction += f"\n{analytics_str}"

    if context_str:
        system_instruction += f"\n\nTÀI LIỆU THAM KHẢO ĐƯỢC CUNG CẤP (RAG CONTEXT):\n----------------------------------\n{context_str}\n----------------------------------"

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

    prompt = f"Hãy lập lộ trình học tập trọn gói (Tuần, Ngày học, Giáo trình, và Quiz kiểm tra) cho môn học '{subject}'."

    # Xây dựng danh sách messages
    messages = []
    if history:
        for msg in history:
            role = "assistant" if msg["role"] in ["model", "assistant"] else "user"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})
    else:
        messages.append({"role": "user", "content": prompt})

    # Gọi NVIDIA NIM API qua OpenAI SDK để sinh JSON có cấu trúc
    print("-> unified_agent: Calling generate_content_nvidia...")
    response_text = generate_content_nvidia(
        messages=messages,
        system_instruction=system_instruction,
        response_schema=None,
        temperature=0.2,
        tools=None
    )
    print(f"-> unified_agent: generate_content_nvidia returned response of size {len(response_text)}")

    try:
        data = json.loads(response_text)
        return UnifiedGoalPlanResponse(**data)
    except Exception as e:
        raise RuntimeError(
            f"Lỗi phân tích cú pháp kết quả từ Unified Super Agent: {e}. "
            f"Kết quả gốc: {response_text}"
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
    db_mongo: Any = None
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
                db_mongo=db_mongo, query_text=subject,
                subject_id=subject_id, top_k=3
            )
            if materials:
                context_parts = []
                for i, m in enumerate(materials):
                    content = m['content']
                    if len(content) > 500:
                        content = content[:500] + "..."
                    context_parts.append(f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{content}")
                context_str = "\n\n".join(context_parts)
                yield ("progress", f"✅ Tìm thấy {len(materials)} tài liệu tham khảo.")
        except Exception as e:
            print(f"[Warning] RAG vector search failed: {e}")

    yield ("progress", "📊 Đang phân tích học lực...")

    schedule_text = f"Ngày rảnh: {format_available_schedule(available_schedule)}"

    today = date.today()
    days_left = (deadline - today).days
    if days_left <= 0:
        days_left = 30

    analytics_str = ""
    try:
        analytics = get_student_analytics_db(student_id, subject_id)
        recent_attempts = get_recent_attempts_db(student_id, limit=5)
        analytics_str = "\n--- HỌC LỰC THỰC TẾ ---\n"
        analytics_str += f"Điểm TB: {analytics['average_score']}/10 ({analytics['quizzes_completed']} bài quiz)\n"
        analytics_str += f"Phần yếu: {', '.join(analytics['weak_topics']) if analytics['weak_topics'] else 'Chưa phát hiện'}\n"
        analytics_str += f"Phần mạnh: {', '.join(analytics['strong_topics']) if analytics['strong_topics'] else 'Chưa phát hiện'}\n"
        if recent_attempts:
            analytics_str += "Lịch sử bài làm gần nhất:\n"
            for att in recent_attempts:
                analytics_str += f"  - {att['quiz_title']}: {att['score']}/10\n"
    except Exception as e:
        print(f"[Warning] Failed to query student analytics: {e}")

    yield ("progress", "🤖 Đang soạn lộ trình học tập...")

    off_days_str = ", ".join(off_days) if off_days else "Không có"
    history_text = ""
    if history:
        for msg in history[-3:]:
            role = "Học sinh" if msg["role"] == "user" else "Trợ lý"
            c = msg.get("content", "")[:150]
            history_text += f"{role}: {c}\n"

    system_instruction = f"""Bạn là một chuyên gia giáo dục Việt Nam và trợ lý AI tối tân.
Nhiệm vụ của bạn là lập và tinh chỉnh lộ trình học tập trọn gói (Unified Plan) đạt mục tiêu {target_score}/10 cho môn học '{subject}' (ID môn học: {subject_id}) với hạn chót là {deadline} (còn {days_left} ngày).
Học sinh hiện tại có ID: {student_id}.

YÊU CẦU BẮT BUỘC:
1. Thiết lập Lộ trình tuần (weeks) và phân chia Lịch học chi tiết từng ngày (daily_schedule) bắt đầu từ {current_date}.
   - Bạn PHẢI tuân thủ số giờ học mỗi ngày: {study_hours_per_day} giờ, khung giờ học ưu tiên: {preferred_time}.
   - Tuyệt đối KHÔNG xếp lịch học vào những ngày nghỉ: {off_days_str}.
   - Bám sát lịch rảnh: {schedule_text}.
2. Tuyệt đối KHÔNG sinh tài liệu tham khảo (curriculum_materials) và đề thi trắc nghiệm (quizzes) ở giai đoạn này. Luôn trả về hai danh sách này dưới dạng mảng rỗng ([]) để đảm bảo tốc độ phản hồi nhanh nhất.
3. Nếu học sinh phản hồi tinh chỉnh, hãy đọc kỹ lịch sử chat (history) để giữ nguyên các phần đã đồng ý và chỉ điều chỉnh các phần học sinh yêu cầu trong JSON kết quả.
4. Câu trả lời luôn luôn phải là một đối tượng JSON khớp chính xác 100% với cấu trúc JSON Schema được định nghĩa.
"""
    if analytics_str:
        system_instruction += f"\n{analytics_str}"
    if context_str:
        system_instruction += f"\n\nTÀI LIỆU THAM KHẢO ĐƯỢC CUNG CẤP (RAG CONTEXT):\n----------------------------------\n{context_str}\n----------------------------------"
    if history_text:
        system_instruction += f"\n\nLỊCH SỬ THẢO LUẬN TRƯỚC ĐÓ:\n{history_text}"

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

    messages = [{"role": "user", "content": f"Hãy lập lộ trình học tập trọn gói cho môn học '{subject}'."}]

    yield ("progress", "⏳ Đang sinh lộ trình...")

    try:
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                generate_content_nvidia, messages=messages,
                system_instruction=system_instruction,
                response_schema=None, temperature=0.2, tools=None
            ),
            timeout=180.0
        )
        print(f"-> sync call done, got {len(response_text)} chars")
    except asyncio.TimeoutError:
        yield ("error", "Quá thời gian tạo lộ trình, hãy thử lại.")
        return

    try:
        data = json.loads(response_text)
        plan = UnifiedGoalPlanResponse(**data)
        yield ("complete", plan)
    except Exception as e:
        yield ("error", f"Lỗi xử lý lộ trình: {str(e)[:150]}")
