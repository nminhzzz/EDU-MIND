"""
FastAPI Router cho các API Analytics — Giai đoạn 4.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.schemas.admin import AdminAnalyticsResponse
from app.services.analytic_service import get_system_analytics

router = APIRouter()

@router.get(
    "/admin/system",
    response_model=AdminAnalyticsResponse,
    summary="Admin lấy báo cáo chỉ số hệ thống",
    description="Chỉ Admin mới có quyền truy cập. Trả về tổng quan số lượng tài khoản, lớp học và lộ trình trên hệ thống."
)
def api_get_system_analytics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return get_system_analytics(db=db)
