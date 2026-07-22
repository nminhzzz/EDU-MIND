from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_student, get_current_user, get_db
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


from app.schemas.user import StudentProfileDetailResponse
from app.models.learning_analytic import LearningAnalytic
from sqlalchemy.orm import selectinload

@router.get(
    "/profile",
    response_model=StudentProfileDetailResponse,
    summary="Lấy chi tiết hồ sơ cá nhân & báo cáo học lực học sinh",
)
def get_student_profile_detail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch learning analytics with subject relation
    analytics = (
        db.query(LearningAnalytic)
        .options(selectinload(LearningAnalytic.subject))
        .filter(LearningAnalytic.student_id == current_user.id)
        .all()
    )
    
    # Tự động tạo/nâng cấp báo cáo học lực on-the-fly dựa trên chi tiết của từng bài thi
    from app.models.quiz_attempt import QuizAttempt
    from app.models.quiz import Quiz
    from app.models.subject import Subject
    from app.services.analytic_service import _recalculate_learning_analytic
    from app.agents.analytics.agent import evaluate_learning_performance
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == current_user.id).all()
    if attempts:
        # Lấy danh sách các môn học từ lịch sử bài thi
        subject_ids = set()
        for a in attempts:
            quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
            if quiz:
                subject_ids.add(quiz.subject_id)
                
        existing_subject_ids = {an.subject_id for an in analytics}
        missing_subject_ids = subject_ids - existing_subject_ids
        
        # Thêm các môn đã có nhưng chưa có báo cáo chi tiết hoặc chưa phân tích cụ thể
        for an in analytics:
            if an.quizzes_completed == 0 or not an.weak_topics or not an.strong_topics:
                missing_subject_ids.add(an.subject_id)
                
        if missing_subject_ids:
            for sub_id in missing_subject_ids:
                subject = db.query(Subject).filter(Subject.id == sub_id).first()
                if subject:
                    analytic, attempts_history = _recalculate_learning_analytic(
                        db, current_user.id, sub_id, subject.name
                    )
                    if attempts_history:
                        try:
                            ai_evaluation = evaluate_learning_performance(
                                subject_name=subject.name,
                                attempts_history=attempts_history,
                            )
                            analytic.weak_topics = [t.model_dump() for t in ai_evaluation.weak_topics]
                            analytic.strong_topics = [t.model_dump() for t in ai_evaluation.strong_topics]
                            analytic.ai_feedback = ai_evaluation.ai_feedback
                            db.add(analytic)
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            print(f"Error on-the-fly analytics: {e}")
            
            # Tải lại danh sách phân tích sau khi đã cập nhật thành công
            analytics = (
                db.query(LearningAnalytic)
                .options(selectinload(LearningAnalytic.subject))
                .filter(LearningAnalytic.student_id == current_user.id)
                .all()
            )
            
    return {
        "user": current_user,
        "preference": current_user.preference,
        "learning_analytics": analytics,
    }
