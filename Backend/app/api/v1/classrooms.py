"""
Classrooms API — CRUD for classrooms, student enrollment, and progress reporting.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
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
