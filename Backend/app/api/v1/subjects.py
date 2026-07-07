"""
FastAPI Router cho các API Môn học (Subjects) — Giai đoạn 4.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_teacher
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.services.subject_service import (
    create_subject,
    get_subject,
    get_all_subjects,
    update_subject,
    delete_subject,
)

router = APIRouter()


# ── POST / — Tạo môn học mới (Chỉ Giáo viên / Admin) ─────────────────
@router.post(
    "/",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên / Admin tạo môn học mới",
    description="Chỉ giáo viên hoặc admin mới có quyền tạo môn học. Mã môn học (code) phải là duy nhất.",
)
def api_create_subject(
    body: SubjectCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    try:
        return create_subject(db=db, obj_in=body)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# ── GET / — Lấy danh sách môn học (Tất cả tài khoản đăng nhập) ─────────
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
):
    return get_all_subjects(db=db, skip=skip, limit=limit)


# ── GET /{subject_id} — Chi tiết môn học ─────────────────────────────
@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Xem chi tiết thông tin một môn học",
)
def api_get_subject_detail(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_subject(db=db, subject_id=subject_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


# ── PATCH /{subject_id} — Cập nhật môn học (Chỉ Giáo viên / Admin) ─────
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
):
    try:
        return update_subject(db=db, subject_id=subject_id, obj_in=body)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# ── DELETE /{subject_id} — Xóa môn học (Chỉ Giáo viên / Admin) ─────────
@router.delete(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Xóa một môn học khỏi hệ thống",
)
def api_delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    try:
        return delete_subject(db=db, subject_id=subject_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
