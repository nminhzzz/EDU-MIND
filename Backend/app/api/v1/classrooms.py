"""
Classrooms API — CRUD for classrooms, student enrollment, and progress reporting.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_admin,
    get_current_student,
    get_current_teacher,
    get_current_user,
    get_db,
)
from app.models.user import User
from app.repositories.classroom_repository import classroom_repository
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomDetailResponse,
    ClassroomJoin,
    ClassroomResponse,
    ClassroomStudentAdd,
)
from app.schemas.teacher import TeacherClassroomStudentResponse
from app.services.classroom_service import (
    add_student_to_classroom,
    create_classroom,
    get_classroom_detail,
    get_classroom_students_progress,
    get_classrooms_for_user,
    list_all_classrooms_admin,
    remove_student_from_classroom,
    student_join_classroom,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên tạo lớp học mới",
)
def api_create_classroom(
    body: ClassroomCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> ClassroomResponse:
    return create_classroom(db=db, teacher_id=current_teacher.id, obj_in=body)


@router.get(
    "/",
    response_model=List[ClassroomResponse],
    summary="Xem danh sách các lớp học của người dùng",
)
def api_get_classrooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ClassroomResponse]:
    return get_classrooms_for_user(db=db, user=current_user)


@router.get(
    "/admin/all",
    response_model=List[ClassroomResponse],
    summary="Admin xem tất cả lớp học trên hệ thống",
)
def api_admin_list_all_classrooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> List[ClassroomResponse]:
    return list_all_classrooms_admin(db=db, skip=skip, limit=limit)


@router.get(
    "/unread-counts",
    response_model=Dict[int, int],
    summary="Lấy số tin nhắn chưa đọc của người dùng theo từng lớp học",
)
def api_get_unread_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[int, int]:
    from app.models.classroom import Classroom
    from app.models.classroom_student import ClassroomStudent
    from app.models.classroom_chat_message import ClassroomChatMessage
    from app.models.classroom_chat_read_cursor import ClassroomChatReadCursor

    if current_user.role == "teacher":
        class_ids = [c.id for c in db.query(Classroom.id).filter(Classroom.teacher_id == current_user.id).all()]
    else:
        class_ids = [cs.classroom_id for cs in db.query(ClassroomStudent.classroom_id).filter(ClassroomStudent.student_id == current_user.id).all()]

    if not class_ids:
        return {}

    cursors = {
        c.classroom_id: c.last_read_message_id
        for c in db.query(ClassroomChatReadCursor).filter(
            ClassroomChatReadCursor.user_id == current_user.id,
            ClassroomChatReadCursor.classroom_id.in_(class_ids)
        ).all()
    }

    unread_counts: Dict[int, int] = {}
    for cid in class_ids:
        last_read_id = cursors.get(cid, 0)
        count = (
            db.query(func.count(ClassroomChatMessage.id))
            .filter(
                ClassroomChatMessage.classroom_id == cid,
                ClassroomChatMessage.id > last_read_id,
                ClassroomChatMessage.sender_id != current_user.id,
            )
            .scalar() or 0
        )
        unread_counts[cid] = count

    return unread_counts


@router.get(
    "/{classroom_id}",
    response_model=ClassroomDetailResponse,
    summary="Xem chi tiết thông tin lớp học",
)
def api_get_classroom_detail(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassroomDetailResponse:
    detail = get_classroom_detail(db=db, classroom_id=classroom_id, user=current_user)
    classroom = detail["classroom"]
    return ClassroomDetailResponse(
        id=classroom.id,
        teacher_id=classroom.teacher_id,
        subject_id=classroom.subject_id,
        class_name=classroom.class_name,
        class_code=classroom.class_code,
        description=classroom.description,
        created_at=classroom.created_at,
        teacher=detail["teacher"],
        students=detail["students"],
        subject=detail["subject"],
    )


@router.post(
    "/{classroom_id}/students",
    status_code=status.HTTP_200_OK,
    summary="Giáo viên thêm học sinh vào lớp học bằng Email",
)
def api_add_student(
    classroom_id: int,
    body: ClassroomStudentAdd,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> dict:
    add_student_to_classroom(
        db=db,
        classroom_id=classroom_id,
        teacher_id=current_teacher.id,
        student_email=body.student_email,
    )
    return {"message": f"Đã thêm thành công học sinh có email {body.student_email} vào lớp học."}


@router.post(
    "/join",
    status_code=status.HTTP_200_OK,
    summary="Học sinh chủ động tham gia lớp bằng mã lớp",
)
def api_join_classroom(
    body: ClassroomJoin,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student),
) -> dict:
    student_join_classroom(db=db, student_id=current_student.id, class_code=body.class_code)
    return {"message": "Tham gia lớp học thành công!"}


@router.delete(
    "/{classroom_id}",
    summary="Admin hoặc Giáo viên chủ quản xóa/giải tán lớp học",
)
def api_delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lớp học.",
        )

    if current_user.role != "admin" and classroom.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền giải tán lớp học này.",
        )

    classroom_repository.remove(db=db, id=classroom_id)
    return {"message": "Đã giải tán lớp học thành công."}


@router.get(
    "/{classroom_id}/students/progress",
    response_model=List[TeacherClassroomStudentResponse],
    summary="Giáo viên lấy danh sách học sinh kèm báo cáo tiến độ học tập",
)
def api_get_classroom_students_progress(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> List[TeacherClassroomStudentResponse]:
    return get_classroom_students_progress(
        db=db,
        classroom_id=classroom_id,
        current_teacher_id=current_teacher.id,
        current_user_role=current_teacher.role,
    )


@router.delete(
    "/{classroom_id}/students/{student_id}",
    summary="Giáo viên hoặc Admin xóa học sinh khỏi lớp học",
)
def api_remove_student_from_classroom(
    classroom_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    remove_student_from_classroom(
        db=db,
        classroom_id=classroom_id,
        student_id=student_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role,
    )
    return {"message": "Đã xóa học sinh khỏi lớp học thành công."}


from app.models.classroom_chat_message import ClassroomChatMessage
from app.schemas.classroom import ClassroomChatMessageResponse
from sqlalchemy.orm import joinedload
from app.core.security import decode_access_token

@router.get(
    "/{classroom_id}/chat/messages",
    response_model=List[ClassroomChatMessageResponse],
    summary="Lấy lịch sử tin nhắn của lớp học",
)
def api_get_classroom_chat_messages(
    classroom_id: int,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ClassroomChatMessageResponse]:
    # 1. Check classroom membership
    from app.models.classroom import Classroom
    from app.models.classroom_student import ClassroomStudent
    
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại."
        )
        
    is_teacher = classroom.teacher_id == current_user.id
    is_student = db.query(ClassroomStudent).filter(
        ClassroomStudent.classroom_id == classroom_id,
        ClassroomStudent.student_id == current_user.id
    ).first() is not None
    
    if not is_teacher and not is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của lớp học này."
        )
        
    # 2. Fetch history with optimized loading (joinedload sender to prevent N+1)
    messages = (
        db.query(ClassroomChatMessage)
        .options(joinedload(ClassroomChatMessage.sender))
        .filter(ClassroomChatMessage.classroom_id == classroom_id)
        .order_by(ClassroomChatMessage.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages


@router.post(
    "/{classroom_id}/chat/mark-read",
    summary="Đánh dấu đã đọc tất cả tin nhắn trong lớp học",
)
def api_mark_classroom_chat_read(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.classroom_chat_message import ClassroomChatMessage
    from app.models.classroom_chat_read_cursor import ClassroomChatReadCursor

    max_msg_id = (
        db.query(func.max(ClassroomChatMessage.id))
        .filter(ClassroomChatMessage.classroom_id == classroom_id)
        .scalar() or 0
    )

    cursor = db.query(ClassroomChatReadCursor).filter(
        ClassroomChatReadCursor.classroom_id == classroom_id,
        ClassroomChatReadCursor.user_id == current_user.id
    ).first()

    if not cursor:
        cursor = ClassroomChatReadCursor(
            classroom_id=classroom_id,
            user_id=current_user.id,
            last_read_message_id=max_msg_id,
        )
        db.add(cursor)
    else:
        if max_msg_id > cursor.last_read_message_id:
            cursor.last_read_message_id = max_msg_id

    db.commit()
    return {"status": "ok", "last_read_message_id": max_msg_id}


@router.websocket("/{classroom_id}/chat/ws")
async def websocket_classroom_chat(
    websocket: WebSocket,
    classroom_id: int,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 1. Verify token (fallback to cookies if not in query param)
    if not token:
        token = websocket.cookies.get("access_token")
        if not token:
            cookie_header = websocket.headers.get("cookie")
            if cookie_header:
                for cookie in cookie_header.split(";"):
                    cookie = cookie.strip()
                    if cookie.startswith("access_token="):
                        token = cookie.split("=")[1]
                        break

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user_id = int(user_id)
    
    # 2. Check if user is teacher of the classroom or student enrolled in the classroom
    from app.models.classroom import Classroom
    from app.models.classroom_student import ClassroomStudent
    
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    is_teacher = classroom.teacher_id == user_id
    is_student = db.query(ClassroomStudent).filter(
        ClassroomStudent.classroom_id == classroom_id,
        ClassroomStudent.student_id == user_id
    ).first() is not None
    
    if not is_teacher and not is_student:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    # 3. Accept connection
    await websocket.accept()
    
    # Register connection in ConnectionManager
    from app.services.classroom_chat_service import classroom_chat_manager
    await classroom_chat_manager.connect(classroom_id, websocket)
    
    # Get user model for broadcast sender info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await classroom_chat_manager.disconnect(classroom_id, websocket)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            content = data.get("content", "").strip()
            if not content:
                continue
                
            # Save message to database
            from app.models.classroom_chat_message import ClassroomChatMessage
            msg = ClassroomChatMessage(
                classroom_id=classroom_id,
                sender_id=user_id,
                content=content
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            
            # Broadcast to all active clients in room
            broadcast_payload = {
                "id": msg.id,
                "classroom_id": msg.classroom_id,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "sender": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                }
            }
            await classroom_chat_manager.broadcast(classroom_id, broadcast_payload)
            
    except WebSocketDisconnect:
        await classroom_chat_manager.disconnect(classroom_id, websocket)
    except Exception as e:
        print(f"WS error: {e}")
        await classroom_chat_manager.disconnect(classroom_id, websocket)
