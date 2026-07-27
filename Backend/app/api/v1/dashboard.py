"""
Dashboard SSE endpoint — streams real-time learning progress to students.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import TokenUser, get_current_student_from_token
from app.core.cache import get_cached, set_cached
from app.database.mysql import SessionLocal
from app.services.dashboard_service import build_dashboard_payload

router = APIRouter()


from typing import AsyncGenerator, Optional

async def _generate_progress_events(
    student_id: int, token_sid: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Infinite SSE generator — yields a JSON snapshot every 3 seconds.
    Monitors active session ID (sid) to trigger instant realtime logout when another device logs in.
    """
    cache_key = f"dashboard_snapshot:{student_id}"
    while True:
        try:
            if token_sid:
                from app.core.security import get_user_active_session
                active_sid = get_user_active_session(student_id)
                if active_sid and active_sid != token_sid:
                    yield f'data: {json.dumps({"error": "SESSION_REVOKED", "message": "Phiên đăng nhập đã bị vô hiệu hóa do có thiết bị mới đăng nhập."})}\n\n'
                    break

            # Thử đọc thông tin dashboard từ Redis cache
            payload = await get_cached(cache_key)
            if payload is None:
                # Cache miss -> Query MySQL
                with SessionLocal() as db:
                    payload = build_dashboard_payload(db, student_id)
                # Lưu vào cache 10 giây
                await set_cached(cache_key, payload, ttl_seconds=10)

            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f'data: {{"error": "{exc}"}}\n\n'

        await asyncio.sleep(3)


@router.get(
    "/stream",
    summary="Realtime Dashboard Stream (SSE)",
    description="Stream tiến độ học tập realtime: tasks hôm nay, tổng quan lộ trình, quiz stats, weak areas.",
)
async def dashboard_stream(
    current_user: TokenUser = Depends(get_current_student_from_token),
) -> StreamingResponse:
    return StreamingResponse(
        _generate_progress_events(current_user.id, current_user.sid),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
