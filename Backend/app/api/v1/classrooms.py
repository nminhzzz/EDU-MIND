"""
FastAPI Router cho các API Lớp học (Classrooms) — Giai đoạn 4.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    get_current_user,
    get_current_teacher,
    get_current_student,
)
from app.models.user import User
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomResponse,
    ClassroomDetailResponse,
    ClassroomStudentAdd,
    ClassroomJoin,
)
from app.services.classroom_service import (
    create_classroom,
    get_classrooms_for_user,
    get_classroom_detail,
    add_student_to_classroom,
    student_join_classroom,
)

router = APIRouter()


# ── POST / — Tạo lớp học (Chỉ Giáo viên) ─────────────────────────────
@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên tạo lớp học mới",
    description="Chỉ tài khoản giáo viên mới có thể tạo lớp học. Mã lớp (class_code) phải là duy nhất.",
)
def api_create_classroom(
    body: ClassroomCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    try:
        return create_classroom(db=db, teacher_id=current_teacher.id, obj_in=body)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# ── GET / — Danh sách lớp học (Giáo viên xem lớp dạy, Học sinh xem lớp học) ───
@router.get(
    "/",
    response_model=List[ClassroomResponse],
    summary="Xem danh sách các lớp học liên quan của người dùng",
)
def api_get_classrooms(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_classrooms_for_user(db=db, user=current_user)


# ── GET /{classroom_id} — Chi tiết lớp học (Môn học, Học sinh) ─────────
@router.get(
    "/{classroom_id}",
    response_model=ClassroomDetailResponse,
    summary="Xem chi tiết thông tin lớp học (Thầy cô, môn học, học sinh)",
)
def api_get_classroom_detail(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        detail = get_classroom_detail(
            db=db, classroom_id=classroom_id, user=current_user
        )
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
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))


# ── POST /{classroom_id}/students — Thêm học sinh (Chỉ Giáo viên) ─────
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
):
    try:
        add_student_to_classroom(
            db=db,
            classroom_id=classroom_id,
            teacher_id=current_teacher.id,
            student_email=body.student_email,
        )
        return {
            "message": f"Đã thêm thành công học sinh có email {body.student_email} vào lớp học."
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))


# ── POST /join — Học sinh tự tham gia lớp học bằng class_code ────────
@router.post(
    "/join",
    status_code=status.HTTP_200_OK,
    summary="Học sinh chủ động tham gia lớp bằng mã lớp",
)
def api_join_classroom(
    body: ClassroomJoin,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student),
):
    try:
        student_join_classroom(
            db=db, student_id=current_student.id, class_code=body.class_code
        )
        return {"message": "Tham gia lớp học thành công!"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# ── ADMIN ENDPOINTS ──
from app.api.deps import get_current_admin
from app.services.classroom_service import (
    list_all_classrooms_admin,
    get_classroom_students_progress,
    remove_student_from_classroom,
)


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
):
    return list_all_classrooms_admin(db=db, skip=skip, limit=limit)


@router.delete(
    "/{classroom_id}", summary="Admin hoặc Giáo viên chủ quản xóa/giải tán lớp học"
)
def api_delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.classroom_service import classroom_repository
    from app.models.classroom import Classroom

    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp học."
        )

    # Chỉ Admin hoặc Giáo viên tạo lớp mới được quyền xóa
    if current_user.role != "admin" and classroom.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền giải tán lớp học này.",
        )

    from app.repositories.classroom_repository import classroom_repository as cr

    cr.remove(db=db, id=classroom_id)
    return {"message": "Đã giải tán lớp học thành công."}


# ── TEACHER MANAGE STUDENTS IN CLASSROOM ──
from app.schemas.teacher import TeacherClassroomStudentResponse


@router.get(
    "/{classroom_id}/students/progress",
    response_model=List[TeacherClassroomStudentResponse],
    summary="Giáo viên lấy danh sách học sinh kèm báo cáo tiến độ học tập",
)
def api_get_classroom_students_progress(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
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
):
    remove_student_from_classroom(
        db=db,
        classroom_id=classroom_id,
        student_id=student_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role,
    )
    return {"message": "Đã xóa học sinh khỏi lớp học thành công."}
