import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.subject import Subject
from app.schemas.chat import (
    TutorSessionCreate,
    TutorMessageSend,
    TutorSessionResponse,
    TutorChatResponse,
)
from app.agents.chat_tutor.memory import (
    create_tutor_session,
    get_tutor_sessions,
    get_tutor_history,
    delete_tutor_session,
)
from app.agents.chat_tutor.agent import chat_with_tutor, chat_with_tutor_stream

router = APIRouter()


# ── POST /tutor/session ────────────────────────────────────────────
@router.post(
    "/tutor/session",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo phiên chat mới với Gia sư ảo",
)
async def create_session(
    body: TutorSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    # Kiểm tra môn học có tồn tại trong MySQL
    subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={body.subject_id}.",
        )

    try:
        session_id = await create_tutor_session(
            student_id=current_user.id,
            subject_id=subject.id,
            title=body.title or f"Trò chuyện môn {subject.name}",
        )
        return session_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi khởi tạo phiên chat: {str(e)}",
        )


# ── GET /tutor/sessions ───────────────────────────────────────────
@router.get(
    "/tutor/sessions",
    response_model=List[TutorSessionResponse],
    summary="Lấy danh sách các phiên chat của học sinh",
)
async def list_sessions(current_user: User = Depends(get_current_student)):
    try:
        sessions = await get_tutor_sessions(student_id=current_user.id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi truy vấn danh sách phiên chat: {str(e)}",
        )


# ── GET /tutor/messages/{session_id} ─────────────────────────────
@router.get(
    "/tutor/messages/{session_id}", summary="Lấy lịch sử tin nhắn của một phiên chat"
)
async def get_messages(
    session_id: str, current_user: User = Depends(get_current_student)
):
    try:
        chat_summary, messages = await get_tutor_history(session_id)
        return {"chat_summary": chat_summary, "messages": messages}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tải lịch sử tin nhắn: {str(e)}",
        )


# ── POST /tutor/message ───────────────────────────────────────────
@router.post(
    "/tutor/message",
    response_model=TutorChatResponse,
    summary="Gửi câu hỏi tới Gia sư ảo và nhận phản hồi",
)
async def send_message(
    body: TutorMessageSend, current_user: User = Depends(get_current_student)
):
    try:
        reply, history = await chat_with_tutor(
            user_message=body.content,
            student_id=current_user.id,
            session_id=body.session_id,
        )
        return {"reply": reply, "history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi gọi Gia sư ảo phản hồi: {str(e)}",
        )


# ── GET /tutor/stream ─────────────────────────────────────────────
@router.get(
    "/tutor/stream", summary="Gửi câu hỏi tới Gia sư ảo dạng Realtime Streaming (SSE)"
)
async def stream_message(
    content: str, session_id: str, current_user: User = Depends(get_current_student)
):
    async def event_generator():
        try:
            async for token in chat_with_tutor_stream(
                user_message=content, student_id=current_user.id, session_id=session_id
            ):
                # Format SSE: data: <token>\n\n
                yield f"data: {token}\n\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"data: [ERROR: {str(e)}]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── DELETE /tutor/session/{session_id} ─────────────────────────────
@router.delete("/tutor/session/{session_id}", summary="Xóa một phiên chat của học sinh")
async def delete_session(
    session_id: str, current_user: User = Depends(get_current_student)
):
    try:
        success = await delete_tutor_session(session_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên chat này hoặc bạn không có quyền xóa.",
            )
        return {"message": "Xóa phiên chat thành công."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa phiên chat: {str(e)}",
        )
