from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.ai_job_service import cancel_ai_job, get_owned_ai_job, serialize_ai_job


router = APIRouter()


@router.get("/{job_id}")
def get_ai_job(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    try:
        return serialize_ai_job(get_owned_ai_job(db, job_id=job_id, user_id=current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{job_id}/cancel")
def cancel_ai_job_api(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    try:
        return serialize_ai_job(cancel_ai_job(db, job_id=job_id, user_id=current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
