import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.chat_tutor.agent import chat_with_tutor, chat_with_tutor_stream
from app.agents.chat_tutor.memory import (
    delete_tutor_session,
    get_tutor_history,
    get_tutor_sessions,
    verify_session_owner,
)
from app.api.deps import TokenUser, get_current_student, get_current_student_from_token, get_db
from app.models.user import User
from app.schemas.chat import (
    TutorChatResponse,
    TutorMessageSend,
    TutorSessionCreate,
    TutorSessionResponse,
)
from app.services.chat_service import create_student_tutor_session

router = APIRouter()


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
    try:
        return await create_student_tutor_session(
            db,
            student_id=current_user.id,
            subject_id=body.subject_id,
            title=body.title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi khởi tạo phiên chat: {str(exc)}",
        ) from exc


@router.get(
    "/tutor/sessions",
    response_model=List[TutorSessionResponse],
    summary="Lấy danh sách các phiên chat của học sinh",
)
async def list_sessions(current_user: User = Depends(get_current_student)):
    try:
        return await get_tutor_sessions(student_id=current_user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi truy vấn danh sách phiên chat: {str(exc)}",
        ) from exc


@router.get(
    "/tutor/messages/{session_id}",
    summary="Lấy lịch sử tin nhắn của một phiên chat",
)
async def get_messages(
    session_id: str, current_user: User = Depends(get_current_student)
):
    if not await verify_session_owner(session_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phiên chat không tồn tại hoặc bạn không có quyền truy cập.",
        )
    try:
        chat_summary, messages = await get_tutor_history(session_id)
        return {"chat_summary": chat_summary, "messages": messages}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tải lịch sử tin nhắn: {str(exc)}",
        ) from exc


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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi gọi Gia sư ảo phản hồi: {str(exc)}",
        ) from exc


@router.get(
    "/tutor/stream",
    summary="Gửi câu hỏi tới Gia sư ảo dạng Realtime Streaming (SSE)",
)
async def stream_message(
    content: str,
    session_id: str,
    current_user: TokenUser = Depends(get_current_student_from_token),
):
    if not await verify_session_owner(session_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phiên chat không tồn tại hoặc bạn không có quyền truy cập.",
        )

    async def event_generator():
        try:
            async for token in chat_with_tutor_stream(
                user_message=content,
                student_id=current_user.id,
                session_id=session_id,
            ):
                yield f"data: {token}\n\n"
                await asyncio.sleep(0.01)
        except Exception as exc:
            yield f"data: [ERROR: {str(exc)}]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete(
    "/tutor/session/{session_id}",
    summary="Xóa một phiên chat của học sinh",
)
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
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa phiên chat: {str(exc)}",
        ) from exc
