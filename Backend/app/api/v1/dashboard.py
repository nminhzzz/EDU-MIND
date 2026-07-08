"""
Dashboard SSE endpoint — streams real-time learning progress to students.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import TokenUser, get_current_student_from_token
from app.database.mysql import SessionLocal
from app.services.dashboard_service import build_dashboard_payload

router = APIRouter()


async def _generate_progress_events(student_id: int) -> AsyncGenerator[str, None]:
    """
    Infinite SSE generator — yields a JSON snapshot every 5 seconds.
    Uses a short-lived DB session per tick to avoid holding connections open.
    """
    while True:
        with SessionLocal() as db:
            try:
                payload = build_dashboard_payload(db, student_id)
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            except Exception as exc:
                yield f'data: {{"error": "{exc}"}}\n\n'

        await asyncio.sleep(5)


@router.get(
    "/stream",
    summary="Realtime Dashboard Stream (SSE)",
    description="Stream tiến độ học tập realtime: tasks hôm nay, tổng quan lộ trình, quiz stats, weak areas.",
)
async def dashboard_stream(
    current_user: TokenUser = Depends(get_current_student_from_token),
) -> StreamingResponse:
    return StreamingResponse(
        _generate_progress_events(current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
