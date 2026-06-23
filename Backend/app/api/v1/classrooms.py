"""
FastAPI Router cho các API Lớp học (Classrooms) — Giai đoạn 4.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_teacher, get_current_student
from app.models.user import User
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomResponse,
    ClassroomDetailResponse,
    ClassroomStudentAdd,
    ClassroomSubjectAdd,
    ClassroomJoin
)
from app.services.classroom_service import (
    create_classroom,
    get_classrooms_for_user,
    get_classroom_detail,
    add_student_to_classroom,
    add_subject_to_classroom,
    student_join_classroom
)

router = APIRouter()


# ── POST / — Tạo lớp học (Chỉ Giáo viên) ─────────────────────────────
@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên tạo lớp học mới",
    description="Chỉ tài khoản giáo viên mới có thể tạo lớp học. Mã lớp (class_code) phải là duy nhất."
)
def api_create_classroom(
    body: ClassroomCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher)
):
    try:
        return create_classroom(db=db, teacher_id=current_teacher.id, obj_in=body)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# ── GET / — Danh sách lớp học (Giáo viên xem lớp dạy, Học sinh xem lớp học) ───
@router.get(
    "/",
    response_model=List[ClassroomResponse],
    summary="Xem danh sách các lớp học liên quan của người dùng"
)
def api_get_classrooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_classrooms_for_user(db=db, user=current_user)


# ── GET /{classroom_id} — Chi tiết lớp học (Môn học, Học sinh) ─────────
@router.get(
    "/{classroom_id}",
    response_model=ClassroomDetailResponse,
    summary="Xem chi tiết thông tin lớp học (Thầy cô, môn học, học sinh)"
)
def api_get_classroom_detail(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        detail = get_classroom_detail(db=db, classroom_id=classroom_id, user=current_user)
        classroom = detail["classroom"]
        return ClassroomDetailResponse(
            id=classroom.id,
            teacher_id=classroom.teacher_id,
            class_name=classroom.class_name,
            class_code=classroom.class_code,
            description=classroom.description,
            created_at=classroom.created_at,
            teacher=detail["teacher"],
            students=detail["students"],
            subjects=detail["subjects"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))


# ── POST /{classroom_id}/students — Thêm học sinh (Chỉ Giáo viên) ─────
@router.post(
    "/{classroom_id}/students",
    status_code=status.HTTP_200_OK,
    summary="Giáo viên thêm học sinh vào lớp học bằng Email"
)
def api_add_student(
    classroom_id: int,
    body: ClassroomStudentAdd,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher)
):
    try:
        add_student_to_classroom(
            db=db,
            classroom_id=classroom_id,
            teacher_id=current_teacher.id,
            student_email=body.student_email
        )
        return {"message": f"Đã thêm thành công học sinh có email {body.student_email} vào lớp học."}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))


# ── POST /{classroom_id}/subjects — Thêm môn học (Chỉ Giáo viên) ──────
@router.post(
    "/{classroom_id}/subjects",
    status_code=status.HTTP_200_OK,
    summary="Giáo viên gán môn học vào lớp học"
)
def api_add_subject(
    classroom_id: int,
    body: ClassroomSubjectAdd,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher)
):
    try:
        add_subject_to_classroom(
            db=db,
            classroom_id=classroom_id,
            teacher_id=current_teacher.id,
            subject_id=body.subject_id
        )
        return {"message": "Đã gán môn học vào lớp học thành công."}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))


# ── POST /join — Học sinh tự tham gia lớp học bằng class_code ────────
@router.post(
    "/join",
    status_code=status.HTTP_200_OK,
    summary="Học sinh chủ động tham gia lớp bằng mã lớp"
)
def api_join_classroom(
    body: ClassroomJoin,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    try:
        student_join_classroom(db=db, student_id=current_student.id, class_code=body.class_code)
        return {"message": "Tham gia lớp học thành công!"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
