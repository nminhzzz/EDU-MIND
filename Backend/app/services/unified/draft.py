"""
Unified goal draft generation — AI roadmap planning and Redis cache.
"""

import json
from datetime import date
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.agents.roadmap_planner import generate_unified_plan, generate_unified_plan_stream
from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db
from app.database.redis import get_redis
from app.models.subject import Subject
from app.models.user import User
from app.repositories import chat_repository
from app.services.unified.validators import load_student_preferences, prune_roadmap_history

logger = get_logger(__name__)


def _save_draft_to_cache(
    session_id: str,
    plan: Any,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    student_id: int,
) -> None:
    """Persist a draft plan to Redis with metadata (TTL 30 minutes)."""
    redis_client = get_redis()
    redis_key = f"unified_draft:{session_id}"
    cache_data = plan.model_dump()
    cache_data["_subject_id"] = subject_obj.id
    cache_data["_subject_name"] = subject_obj.name
    cache_data["_target_score"] = target_score
    cache_data["_deadline"] = deadline.isoformat()
    cache_data["_student_id"] = student_id
    redis_client.setex(redis_key, 1800, json.dumps(cache_data, ensure_ascii=False))
    logger.debug("Cached unified draft in Redis for session %s (TTL: 1800s)", session_id)


async def generate_unified_draft(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    user_message: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sinh/tinh chỉnh lộ trình hợp nhất và lưu vào Redis Cache.
    """
    db_mongo = get_mongodb_db()

    if not session_id:
        session_id = await chat_repository.create_chat_session(
            student_id=student.id, title=f"Lập lộ trình {subject_obj.name}"
        )

    if user_message:
        await chat_repository.add_chat_message(session_id, "user", user_message)

    history_msgs = await chat_repository.get_chat_messages(session_id)

    study_hours_per_day, preferred_time_vn, off_days, available_schedule = (
        load_student_preferences(student.id)
    )

    current_date = date.today().strftime("%Y-%m-%d")
    try:
        plan = await generate_unified_plan(
            subject=subject_obj.name,
            target_score=target_score,
            deadline=deadline,
            student_id=student.id,
            subject_id=subject_obj.id,
            study_hours_per_day=study_hours_per_day,
            preferred_time=preferred_time_vn,
            off_days=off_days,
            current_date=current_date,
            available_schedule=available_schedule,
            history=prune_roadmap_history(history_msgs),
            db_mongo=db_mongo,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    _save_draft_to_cache(
        session_id, plan, subject_obj, target_score, deadline, student.id
    )

    await chat_repository.add_chat_message(
        session_id, "assistant", plan.model_dump_json()
    )

    return {"session_id": session_id, "plan": plan}


async def generate_unified_draft_stream(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    user_message: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """
    Streaming version: yields (type, data) tuples.
    Types: 'progress', 'token', 'complete', 'error'
    """
    db_mongo = get_mongodb_db()

    if not session_id:
        session_id = await chat_repository.create_chat_session(
            student_id=student.id, title=f"Lập lộ trình {subject_obj.name}"
        )
        yield ("progress", f"🆔 Phiên làm việc: {session_id}")

    if user_message:
        await chat_repository.add_chat_message(session_id, "user", user_message)

    history_msgs = await chat_repository.get_chat_messages(session_id)

    study_hours_per_day, preferred_time_vn, off_days, available_schedule = (
        load_student_preferences(student.id)
    )

    current_date = date.today().strftime("%Y-%m-%d")

    plan = None
    async for msg_type, msg_data in generate_unified_plan_stream(
        subject=subject_obj.name,
        target_score=target_score,
        deadline=deadline,
        student_id=student.id,
        subject_id=subject_obj.id,
        study_hours_per_day=study_hours_per_day,
        preferred_time=preferred_time_vn,
        off_days=off_days,
        current_date=current_date,
        available_schedule=available_schedule,
        history=prune_roadmap_history(history_msgs),
        db_mongo=db_mongo,
    ):
        if msg_type == "complete":
            plan = msg_data
        elif msg_type == "error":
            yield ("error", msg_data)
            return
        else:
            yield (msg_type, msg_data)

    if plan is None:
        yield ("error", "Không thể tạo lộ trình.")
        return

    _save_draft_to_cache(
        session_id, plan, subject_obj, target_score, deadline, student.id
    )

    await chat_repository.add_chat_message(
        session_id, "assistant", plan.model_dump_json()
    )

    yield ("progress", "💾 Đã lưu bản nháp. Bạn có thể nói 'lưu lại' để xác nhận.")
    yield (
        "complete_plan",
        {
            "session_id": session_id,
            "plan": plan,
            "plan_text": format_plan_as_text(plan),
        },
    )


def format_plan_as_text(plan) -> str:
    lines = []
    lines.append("📅 **Lộ trình tuần:**")
    for w in plan.weeks:
        lines.append(f"  • Tuần {w.week}: {' | '.join(w.tasks[:3])}")
        if len(w.tasks) > 3:
            lines.append(f"    ... và {len(w.tasks) - 3} nhiệm vụ khác")

    lines.append(f"\n📆 **Thời khóa biểu chi tiết ({len(plan.daily_schedule)} buổi):**")
    for day in plan.daily_schedule[:5]:
        lines.append(f"  • {day.date} ({day.start_time}-{day.end_time}): {day.task}")
    if len(plan.daily_schedule) > 5:
        lines.append(f"    ... và {len(plan.daily_schedule) - 5} buổi khác")

    lines.append(
        f"\n📚 **Tài liệu tham khảo ({len(plan.curriculum_materials)} tài liệu):**"
    )
    for m in plan.curriculum_materials[:3]:
        lines.append(f"  • {m.topic}")

    lines.append(f"\n📝 **Bài kiểm tra ({len(plan.quizzes)} đề):**")
    for q in plan.quizzes:
        lines.append(f"  • {q.title} ({len(q.questions)} câu)")

    return "\n".join(lines)
