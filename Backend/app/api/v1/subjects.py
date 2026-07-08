"""
Subjects API — CRUD for academic subjects.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher, get_current_user, get_db
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.subject_service import (
    create_subject,
    delete_subject,
    get_all_subjects,
    get_subject,
    update_subject,
)

router = APIRouter()


@router.post(
    "/",
    response_model=SubjectResponse,
    status_code=201,
    summary="Giáo viên / Admin tạo môn học mới",
)
def api_create_subject(
    body: SubjectCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> SubjectResponse:
    return create_subject(db=db, obj_in=body)


@router.get(
    "/",
    response_model=List[SubjectResponse],
    summary="Lấy danh sách tất cả các môn học",
)
def api_get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SubjectResponse]:
    return get_all_subjects(db=db, skip=skip, limit=limit)


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Xem chi tiết thông tin một môn học",
)
def api_get_subject_detail(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectResponse:
    return get_subject(db=db, subject_id=subject_id)


@router.patch(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Cập nhật thông tin một môn học",
)
def api_update_subject(
    subject_id: int,
    body: SubjectUpdate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> SubjectResponse:
    return update_subject(db=db, subject_id=subject_id, obj_in=body)


@router.delete(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Xóa một môn học khỏi hệ thống",
)
def api_delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
) -> SubjectResponse:
    return delete_subject(db=db, subject_id=subject_id)
