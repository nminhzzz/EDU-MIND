from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.student_preference import StudentPreference
from app.schemas.student_preference import (
    StudentPreferenceResponse,
    StudentPreferenceBase,
)

router = APIRouter()


@router.get(
    "/preferences",
    response_model=StudentPreferenceResponse,
    summary="Lấy thông tin cấu hình lịch học của học sinh hiện tại",
    description="Trả về lịch học, số giờ học mỗi ngày và khung giờ học mong muốn. Trả về 404 nếu chưa thiết lập.",
)
def get_preferences(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_student)
):
    pref = (
        db.query(StudentPreference)
        .filter(StudentPreference.student_id == current_user.id)
        .first()
    )
    if not pref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Học sinh chưa cấu hình lịch học và thời gian học ưa thích.",
        )
    return pref


@router.put(
    "/preferences",
    response_model=StudentPreferenceResponse,
    summary="Cập nhật hoặc khởi tạo lịch học cho học sinh",
    description="Khởi tạo hoặc ghi đè cấu hình lịch rảnh và thời gian học ưa thích.",
)
def update_preferences(
    body: StudentPreferenceBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    pref = (
        db.query(StudentPreference)
        .filter(StudentPreference.student_id == current_user.id)
        .first()
    )
    if not pref:
        # Nếu chưa có, tạo mới
        pref = StudentPreference(
            student_id=current_user.id,
            study_hours_per_day=body.study_hours_per_day,
            preferred_study_time=body.preferred_study_time.value,
            available_schedule=body.available_schedule,
        )
        db.add(pref)
    else:
        # Nếu đã có, ghi đè cập nhật
        pref.study_hours_per_day = body.study_hours_per_day
        pref.preferred_study_time = body.preferred_study_time.value
        pref.available_schedule = body.available_schedule

    db.commit()
    db.refresh(pref)
    return pref


# ── ADMIN USER MANAGEMENT ENDPOINTS ──

from typing import List, Optional
from app.api.deps import get_current_admin
from app.schemas.admin import AdminUserCreate, AdminUserUpdate, AdminUserResponse
from app.services import user_service


@router.get(
    "/admin/users",
    response_model=List[AdminUserResponse],
    summary="Admin lấy danh sách người dùng",
    description="Chỉ Admin mới có quyền truy cập. Hỗ trợ lọc theo vai trò (role) và trạng thái hoạt động (is_active).",
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
    description="Chỉ Admin mới có quyền truy cập. Cho phép tạo thủ công tài khoản giáo viên/admin.",
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
    description="Chỉ Admin mới có quyền truy cập. Sửa đổi thông tin chi tiết hoặc vô hiệu hóa tài khoản.",
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
    description="Chỉ Admin mới có quyền truy cập. Xóa vĩnh viễn tài khoản khỏi database.",
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
