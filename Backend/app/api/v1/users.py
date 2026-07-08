from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_student, get_db
from app.models.user import User
from app.schemas.admin import AdminUserCreate, AdminUserResponse, AdminUserUpdate
from app.schemas.student_preference import StudentPreferenceBase, StudentPreferenceResponse
from app.services import user_service
from app.services.preference_service import get_student_preferences, upsert_student_preferences

router = APIRouter()


@router.get(
    "/preferences",
    response_model=StudentPreferenceResponse,
    summary="Lấy thông tin cấu hình lịch học của học sinh hiện tại",
)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    try:
        return get_student_preferences(db, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/preferences",
    response_model=StudentPreferenceResponse,
    summary="Cập nhật hoặc khởi tạo lịch học cho học sinh",
)
def update_preferences(
    body: StudentPreferenceBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    return upsert_student_preferences(db, current_user.id, body)


@router.get(
    "/admin/users",
    response_model=List[AdminUserResponse],
    summary="Admin lấy danh sách người dùng",
)
def list_users_admin(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return user_service.list_users_admin(
        db=db, role=role, is_active=is_active, skip=skip, limit=limit
    )


@router.post(
    "/admin/users",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin tạo người dùng mới",
)
def create_user_admin(
    body: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return user_service.create_user_admin(db=db, obj_in=body)


@router.patch(
    "/admin/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Admin cập nhật người dùng",
)
def update_user_admin(
    user_id: int,
    body: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return user_service.update_user_admin(
        db=db, user_id=user_id, obj_in=body, current_admin_id=current_admin.id
    )


@router.delete(
    "/admin/users/{user_id}",
    summary="Admin xóa người dùng",
)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user_service.delete_user_admin(
        db=db, user_id=user_id, current_admin_id=current_admin.id
    )
    return {"message": "Đã xóa tài khoản người dùng thành công."}
