from typing import Optional, List, Dict, Any, AsyncGenerator
from app.agents.base import generate_content_nvidia, generate_content_nvidia_stream
from app.agents.prompts import CHAT_TUTOR_SYSTEM_PROMPT
from app.agents.tools.datetime_tool import get_current_date
from app.agents.tools.db_tools import get_student_study_plans_db, get_student_analytics_db, get_last_attempt_details_db
from app.agents.chat_tutor.memory import (
    get_tutor_history,
    add_tutor_message,
    summarize_session_if_needed
)
from app.agents.chat_tutor.intent import detect_intent, extract_subject
from app.database.mysql import SessionLocal
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.services.unified_service import (
    generate_unified_draft,
    generate_unified_draft_stream,
    confirm_unified_draft,
    format_plan_as_text,
    get_active_goal_for_subject
)
from app.database.redis import get_redis_client

async def _build_chat_context(
    user_message: str,
    history: Optional[List[Dict[str, str]]],
    student_id: int,
    session_id: Optional[str]
) -> tuple:
    today = get_current_date()
    try:
        plans = get_student_study_plans_db(student_id)
        analytics = get_student_analytics_db(student_id)
        rag_context = "\n--- THÔNG TIN THỰC TẾ TỪ DATABASE ---\n"
        rag_context += f"Học lực: {analytics['average_score']}/10 ({analytics['quizzes_completed']} bài quiz)\n"
        rag_context += f"Phần yếu: {analytics['weak_topics']}\n"
        rag_context += f"Phần mạnh: {analytics['strong_topics']}\n"
        if plans:
            rag_context += "Lịch trình sắp tới:\n"
            for p in plans[:5]:
                rag_context += f"  + Ngày {p['date']} ({p['time']}): {p['title']} [{p['status']}]\n"
    except Exception as e:
        rag_context = f"\n(Không thể truy vấn DB: {e})\n"

    chat_summary = ""
    recent_messages = []
    if session_id:
        chat_summary, recent_messages = await get_tutor_history(session_id)
    else:
        recent_messages = history if history is not None else []

    system_instruction = f"Hôm nay: {today}.\n{rag_context}\n"
    if chat_summary:
        system_instruction += f"\n--- TÓM TẮT HỘI THOẠI TRƯỚC ---\n{chat_summary}\n"
    system_instruction += f"\n{CHAT_TUTOR_SYSTEM_PROMPT}"

    formatted_messages = []
    for msg in recent_messages:
        role = "assistant" if msg["role"] in ["model", "assistant"] else "user"
        formatted_messages.append({"role": role, "content": msg["content"]})
    formatted_messages.append({"role": "user", "content": user_message})

    return system_instruction, formatted_messages, recent_messages, chat_summary


async def normal_chat_with_tutor(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None
) -> tuple:
    sys_inst, msgs, recent, _ = await _build_chat_context(user_message, history, student_id, session_id)

    reply_text = generate_content_nvidia(
        messages=msgs,
        system_instruction=sys_inst,
        temperature=0.7
    )

    if session_id:
        await add_tutor_message(session_id, "user", user_message)
        await add_tutor_message(session_id, "assistant", reply_text)
        await summarize_session_if_needed(session_id)
        _, updated_messages = await get_tutor_history(session_id)
        return reply_text, updated_messages
    else:
        updated_history = list(recent)
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "assistant", "content": reply_text})
        return reply_text, updated_history


async def stream_chat_with_tutor(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None
):
    sys_inst, msgs, recent, _ = await _build_chat_context(user_message, history, student_id, session_id)

    reply_tokens = []
    for token in generate_content_nvidia_stream(
        messages=msgs,
        system_instruction=sys_inst,
        temperature=0.7
    ):
        reply_tokens.append(token)
        yield token

    reply_text = "".join(reply_tokens)

    if session_id:
        await add_tutor_message(session_id, "user", user_message)
        await add_tutor_message(session_id, "assistant", reply_text)
        await summarize_session_if_needed(session_id)


async def chat_with_plan(
    intent: dict,
    student_id: int,
    session_id: Optional[str],
    db=None
) -> tuple:
    data = intent["data"]

    if intent["type"] == "ask_info":
        missing = data["missing"]
        subject_hint = f" môn {data['subject']}" if data.get("subject") else ""
        score_hint = f" điểm {data['target_score']}" if data.get("target_score") else ""
        deadline_hint = f" hạn {data['deadline']}" if data.get("deadline") else ""
        reply = (
            f"Để lập lộ trình học tập, anh/chị vui lòng cung cấp thêm: {', '.join(missing)}.\n"
            f"Ví dụ: \"Tôi muốn học{subject_hint} đạt{score_hint} trong{deadline_hint} 2 tuần\""
        )
        return reply, []

    if intent["type"] in ("create_plan", "refine_plan"):
        student = db.query(User).filter(User.id == student_id).first() if db else None
        if not student:
            return "Vui lòng đăng nhập để lập lộ trình.", []

        subject_name = data.get("subject", "")
        subject = db.query(Subject).filter(
            Subject.name.ilike(f"%{subject_name}%")
        ).first() if db else None
        if not subject:
            return f"Không tìm thấy môn học '{subject_name}' trong hệ thống.", []

        target_score = float(data.get("target_score", 7.0))
        from datetime import date
        deadline_str = data.get("deadline")
        deadline = date.fromisoformat(deadline_str) if deadline_str else date.today().replace(month=date.today().month + 1)

        user_msg = data.get("user_message", "Hãy lập lộ trình học tập cho tôi.")

        session_id_to_use = session_id if intent["type"] == "refine_plan" else None

        result = await generate_unified_draft(
            student=student,
            subject_obj=subject,
            target_score=target_score,
            deadline=deadline,
            user_message=user_msg,
            session_id=session_id_to_use
        )

        plan = result["plan"]
        plan_text = format_plan_as_text(plan)
        new_session_id = result["session_id"]

        reply = (
            f"📋 **Lộ trình học {subject.name} - Mục tiêu {target_score}/10**\n\n"
            f"{plan_text}\n\n"
            f"---\n"
            f"🆔 Mã phiên: {new_session_id}\n\n"
            f"Anh/chị có thể:\n"
            f"- Nói **\"sửa/tinh chỉnh\"** để điều chỉnh lộ trình\n"
            f"- Nói **\"lưu lại\"** hoặc **\"OK\"** để chốt lưu vào hệ thống"
        )
        return reply, []

    if intent["type"] == "confirm_plan":
        student = db.query(User).filter(User.id == student_id).first() if db else None
        if not student or not session_id:
            return "Không tìm thấy phiên lộ trình nào để lưu.", []

        cached_key = f"unified_draft:{session_id}"
        redis_client = get_redis_client()
        if not redis_client.exists(cached_key):
            return "Không tìm thấy lộ trình nháp. Vui lòng tạo lộ trình trước.", []

        import json
        from datetime import date
        cached = redis_client.get(cached_key)
        plan_data = json.loads(cached)

        subject_id = plan_data.get("_subject_id")
        if not subject_id:
            first_material = (plan_data.get("curriculum_materials") or [None])
            if first_material:
                subject = db.query(Subject).filter(
                    Subject.name.ilike(f"%{first_material[0].get('topic', '')}%")
                ).first() if db else None
                subject_id = subject.id if subject else None

        if not subject_id:
            subject = db.query(Subject).first()
            subject_id = subject.id if subject else None

        subject_obj = db.query(Subject).filter(Subject.id == subject_id).first() if subject_id else None
        if not subject_obj:
            return "Không tìm thấy môn học. Vui lòng tạo lại lộ trình.", []

        last_date = plan_data.get("daily_schedule", [{}])[-1].get("date", str(date.today()))
        from datetime import date as dt_date
        confirm = await confirm_unified_draft(
            db=db,
            student=student,
            subject_obj=subject_obj,
            session_id=session_id,
            target_score=plan_data.get("_target_score", 7.0),
            deadline=dt_date.fromisoformat(last_date) if isinstance(last_date, str) else dt_date.today()
        )

        reply = (
            f"✅ **Đã lưu lộ trình thành công!**\n"
            f"- Số ngày học: {confirm['total_plans']}\n"
            f"- Số đề thi: {confirm['total_quizzes']}\n\n"
            f"Chúc anh/chị học tập hiệu quả!"
        )
        return reply, []

    return "Tôi chưa hiểu ý anh/chị. Vui lòng nói rõ hơn!", []


async def chat_with_tutor(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None
) -> tuple:
    intent = await detect_intent(user_message, session_id, student_id)

    if intent["type"] in ("create_plan", "refine_plan", "confirm_plan", "ask_info"):
        db = SessionLocal()
        try:
            return await chat_with_plan(intent, student_id, session_id, db)
        except Exception as e:
            return f"Lỗi xử lý lộ trình: {str(e)}", []
        finally:
            db.close()

    if intent["type"] == "explain_quiz":
        # Lấy thông tin bài quiz gần nhất của học sinh từ MySQL
        quiz_data = get_last_attempt_details_db(student_id)
        if not quiz_data:
            return "Bạn chưa hoàn thành bài quiz nào gần đây để mình có thể phân tích lỗi sai giúp bạn.", []
        
        # Tạo prompt cho AI dựa trên chi tiết câu trả lời sai
        analysis_context = f"Đề thi: {quiz_data['quiz_title']}\n"
        analysis_context += f"Kết quả: {quiz_data['correct_count']} câu đúng, {quiz_data['wrong_count']} câu sai (Điểm: {quiz_data['score']}/10)\n\n"
        analysis_context += "Chi tiết các câu hỏi trong đề thi:\n"
        
        for idx, q in enumerate(quiz_data["questions"]):
            status_text = "Đúng" if q["is_correct"] else "SAI"
            analysis_context += f"Câu {idx+1}: {q['question_text']}\n"
            analysis_context += f"  - Lựa chọn: {q['options']}\n"
            analysis_context += f"  - Học sinh trả lời: {q['chosen_answer']}\n"
            analysis_context += f"  - Đáp án đúng: {q['correct_answer']} (Trạng thái: {status_text})\n"
            analysis_context += f"  - Giải thích lý thuyết: {q['explanation']}\n\n"

        system_instruction = (
            "Bạn là một gia sư AI thân thiện. Nhiệm vụ của bạn là phân tích bài thi thử gần nhất của học sinh dựa trên dữ liệu đầu vào. "
            "Hãy tóm tắt học lực của họ qua bài thi này, chỉ ra những câu họ đã làm sai, phân tích cặn kẽ TẠI SAO họ lại sai (giải thích từ lỗi hiểu lầm thường gặp của học sinh) "
            "và hướng dẫn họ ôn tập lại phần lý thuyết liên quan dựa vào phần 'Giải thích lý thuyết' được cung cấp. Giọng điệu thân thiện, động viên."
        )

        messages = [
            {"role": "user", "content": f"Hãy phân tích chi tiết kết quả làm bài của tôi và giải thích các câu sai.\n\nDữ liệu bài làm:\n{analysis_context}"}
        ]

        reply_text = generate_content_nvidia(
            messages=messages,
            system_instruction=system_instruction,
            temperature=0.4
        )

        if session_id:
            await add_tutor_message(session_id, "user", user_message)
            await add_tutor_message(session_id, "assistant", reply_text)
            _, updated_messages = await get_tutor_history(session_id)
            return reply_text, updated_messages
        else:
            return reply_text, []

    return await normal_chat_with_tutor(
        user_message, history, student_id, session_id
    )



async def chat_with_tutor_stream(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None
) -> AsyncGenerator[str, None]:
    intent = await detect_intent(user_message, session_id, student_id)

    if intent["type"] == "ask_info":
        db = SessionLocal()
        try:
            reply, _ = await chat_with_plan(intent, student_id, session_id, db)
            for token in reply.split(" "):
                yield token + " "
                import asyncio
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"[Lỗi: {str(e)}]"
        finally:
            db.close()
        return

    if intent["type"] in ("create_plan", "refine_plan"):
        db = SessionLocal()
        try:
            student = db.query(User).filter(User.id == student_id).first()
            if not student:
                yield "Vui lòng đăng nhập."
                return

            subject_name = intent["data"].get("subject", "")
            subject = db.query(Subject).filter(
                Subject.name.ilike(f"%{subject_name}%")
            ).first() if db else None
            if not subject:
                yield f"Không tìm thấy môn học '{subject_name}'."
                return

            target_score = float(intent["data"].get("target_score", 7.0))
            from datetime import date
            deadline_str = intent["data"].get("deadline")
            deadline = date.fromisoformat(deadline_str) if deadline_str else date.today().replace(month=date.today().month + 1)
            user_msg = intent["data"].get("user_message", "")
            sid_to_use = session_id if intent["type"] == "refine_plan" else None

            is_first_token = True
            async for msg_type, msg_data in generate_unified_draft_stream(
                student=student, subject_obj=subject,
                target_score=target_score, deadline=deadline,
                user_message=user_msg, session_id=sid_to_use
            ):
                if msg_type == "progress":
                    yield f"\n{msg_data}\n"
                elif msg_type == "token":
                    if is_first_token:
                        yield "\n📝 Nội dung lộ trình:\n\n"
                        is_first_token = False
                    yield msg_data
                elif msg_type == "complete_plan":
                    yield f"\n\n{msg_data['plan_text']}\n\n"
                    yield f"🆔 Mã phiên: {msg_data['session_id']}\n"
                    yield "💡 Nói 'lưu lại' để xác nhận hoặc 'sửa' để điều chỉnh.\n"
                elif msg_type == "error":
                    yield f"\n❌ {msg_data}\n"
        except Exception as e:
            yield f"\n❌ Lỗi: {str(e)}\n"
        finally:
            db.close()
        return

    if intent["type"] == "confirm_plan":
        db = SessionLocal()
        try:
            reply, _ = await chat_with_plan(intent, student_id, session_id, db)
            for token in reply.split(" "):
                yield token + " "
                import asyncio
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"[Lỗi: {str(e)}]"
        finally:
            db.close()
        return

    if intent["type"] == "explain_quiz":
        try:
            reply, _ = await chat_with_tutor(user_message, history, student_id, session_id)
            for token in reply.split(" "):
                yield token + " "
                import asyncio
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"[Lỗi: {str(e)}]"
        return


    async for token in stream_chat_with_tutor(
        user_message, history, student_id, session_id
    ):
        yield token
