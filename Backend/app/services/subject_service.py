"""
Service xử lý các nghiệp vụ liên quan đến Môn học (Subjects) — Giai đoạn 4.
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.repositories.subject_repository import subject_repository


def create_subject(db: Session, obj_in: SubjectCreate) -> Subject:
    """Tạo mới một môn học (kiểm tra tính duy nhất của code)."""
    existing = subject_repository.get_by_code(db, obj_in.code)
    if existing:
        raise ValueError(f"Mã môn học '{obj_in.code}' đã tồn tại trong hệ thống.")
    return subject_repository.create(db=db, obj_in=obj_in)


def get_subject(db: Session, subject_id: int) -> Subject:
    """Lấy thông tin chi tiết một môn học."""
    subject = subject_repository.get(db=db, id=subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}.")
    return subject


def get_all_subjects(db: Session, skip: int = 0, limit: int = 100) -> List[Subject]:
    """Lấy danh sách tất cả môn học."""
    return subject_repository.get_multi(db=db, skip=skip, limit=limit)


def update_subject(db: Session, subject_id: int, obj_in: SubjectUpdate) -> Subject:
    """Cập nhật thông tin môn học (kiểm tra trùng mã code nếu cập nhật code)."""
    subject = subject_repository.get(db=db, id=subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}.")

    if obj_in.code and obj_in.code != subject.code:
        existing = subject_repository.get_by_code(db, obj_in.code)
        if existing:
            raise ValueError(f"Mã môn học '{obj_in.code}' đã thuộc về môn học khác.")

    return subject_repository.update(db=db, db_obj=subject, obj_in=obj_in)


def delete_subject(db: Session, subject_id: int) -> Subject:
    """Xóa một môn học theo ID."""
    subject = subject_repository.get(db=db, id=subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}.")
    return subject_repository.remove(db=db, id=subject_id)
