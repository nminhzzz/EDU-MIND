import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from app.infrastructure.ai import generate_content_deepseek, generate_content_deepseek_stream
from app.agents.prompts import CHAT_TUTOR_SYSTEM_PROMPT
from app.agents.tools.datetime_tool import get_current_date
from app.agents.tools.db_tools import (
    get_student_study_plans_db,
    get_student_analytics_db,
    get_last_attempt_details_db,
)
from app.agents.chat_tutor.memory import (
    get_tutor_history,
    add_tutor_message,
    summarize_session_if_needed,
)
from app.agents.chat_tutor.intent import detect_intent


async def _build_chat_context(
    user_message: str,
    history: Optional[List[Dict[str, str]]],
    student_id: int,
    session_id: Optional[str],
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
    session_id: Optional[str] = None,
) -> tuple:
    sys_inst, msgs, recent, _ = await _build_chat_context(
        user_message, history, student_id, session_id
    )

    reply_text = await asyncio.to_thread(
        generate_content_deepseek, messages=msgs, system_instruction=sys_inst, temperature=0.7
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
    session_id: Optional[str] = None,
):
    sys_inst, msgs, recent, _ = await _build_chat_context(
        user_message, history, student_id, session_id
    )

    # Run the sync streaming generator in a thread to avoid blocking the event loop.
    # Tokens are collected into a list and yielded progressively.
    import queue as _queue

    token_queue: _queue.Queue = _queue.Queue()

    def _stream_to_queue() -> None:
        for tok in generate_content_deepseek_stream(
            messages=msgs, system_instruction=sys_inst, temperature=0.7
        ):
            token_queue.put(tok)
        token_queue.put(None)  # sentinel

    loop = asyncio.get_event_loop()
    stream_future = loop.run_in_executor(None, _stream_to_queue)

    reply_tokens = []
    while True:
        try:
            tok = token_queue.get_nowait()
        except _queue.Empty:
            await asyncio.sleep(0.01)
            continue
        if tok is None:
            break
        reply_tokens.append(tok)
        yield tok

    await stream_future  # ensure thread completed cleanly
    reply_text = "".join(reply_tokens)

    if session_id:
        await add_tutor_message(session_id, "user", user_message)
        await add_tutor_message(session_id, "assistant", reply_text)
        await summarize_session_if_needed(session_id)


async def chat_with_tutor(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None,
) -> tuple:
    intent = await detect_intent(user_message, session_id, student_id)

    if intent["type"] == "explain_quiz":
        # Lấy thông tin bài quiz gần nhất của học sinh từ MySQL
        quiz_data = get_last_attempt_details_db(student_id)
        if not quiz_data:
            return (
                "Bạn chưa hoàn thành bài quiz nào gần đây để mình có thể phân tích lỗi sai giúp bạn.",
                [],
            )

        # Tạo prompt cho AI dựa trên chi tiết câu trả lời sai
        analysis_context = f"Đề thi: {quiz_data['quiz_title']}\n"
        analysis_context += f"Kết quả: {quiz_data['correct_count']} câu đúng, {quiz_data['wrong_count']} câu sai (Điểm: {quiz_data['score']}/10)\n\n"
        analysis_context += "Chi tiết các câu hỏi trong đề thi:\n"

        for idx, q in enumerate(quiz_data["questions"]):
            status_text = "Đúng" if q["is_correct"] else "SAI"
            analysis_context += f"Câu {idx+1}: {q['question_text']}\n"
            analysis_context += f"  - Lựa chọn: {q['options']}\n"
            analysis_context += f"  - Học sinh trả lời: {q['chosen_answer']}\n"
            analysis_context += (
                f"  - Đáp án đúng: {q['correct_answer']} (Trạng thái: {status_text})\n"
            )
            analysis_context += f"  - Giải thích lý thuyết: {q['explanation']}\n\n"

        system_instruction = (
            "Bạn là một gia sư AI thân thiện. Nhiệm vụ của bạn là phân tích bài thi thử gần nhất của học sinh dựa trên dữ liệu đầu vào. "
            "Hãy tóm tắt học lực của họ qua bài thi này, chỉ ra những câu họ đã làm sai, phân tích cặn kẽ TẠI SAO họ lại sai (giải thích từ lỗi hiểu lầm thường gặp của học sinh) "
            "và hướng dẫn họ ôn tập lại phần lý thuyết liên quan dựa vào phần 'Giải thích lý thuyết' được cung cấp. Giọng điệu thân thiện, động viên."
        )

        messages = [
            {
                "role": "user",
                "content": f"Hãy phân tích chi tiết kết quả làm bài của tôi và giải thích các câu sai.\n\nDữ liệu bài làm:\n{analysis_context}",
            }
        ]

        reply_text = await asyncio.to_thread(
            generate_content_deepseek,
            messages=messages,
            system_instruction=system_instruction,
            temperature=0.4,
        )

        if session_id:
            await add_tutor_message(session_id, "user", user_message)
            await add_tutor_message(session_id, "assistant", reply_text)
            _, updated_messages = await get_tutor_history(session_id)
            return reply_text, updated_messages
        else:
            return reply_text, []

    return await normal_chat_with_tutor(user_message, history, student_id, session_id)


async def chat_with_tutor_stream(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    student_id: int = 1,
    session_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    intent = await detect_intent(user_message, session_id, student_id)

    if intent["type"] == "explain_quiz":
        try:
            reply, _ = await chat_with_tutor(
                user_message, history, student_id, session_id
            )
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
