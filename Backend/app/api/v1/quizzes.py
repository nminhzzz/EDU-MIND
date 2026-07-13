"""
API quản lý Đề thi và Chấm bài (Quizzes & Question Bank).
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher, get_current_user, get_db
from app.core.enums import UserRole
from app.database.mongodb import get_mongodb_db
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.quiz import QuizCreateRequest, QuizDetailResponse, QuizResponse
from app.schemas.quiz_attempt import QuizAttemptCreate, QuizAttemptResponse
from app.schemas.teacher import TeacherQuizCreate
from app.services.analytic_service import update_student_analytics_and_recommend
from app.services.quiz_service import (
    generate_and_save_quiz,
    get_classroom_quiz_attempts,
    get_quiz,
    get_quiz_for_study_plan,
    get_quiz_review,
    get_student_quiz_attempts,
    submit_student_quiz,
    teacher_create_quiz,
)

router = APIRouter()


async def _analytics_background(
    student_id: int, subject_id: int, quiz_id: int, score: float
) -> None:
    """Run analytics update in a dedicated DB session to avoid using a closed request session."""
    from app.database.mysql import SessionLocal

    with SessionLocal() as db:
        await update_student_analytics_and_recommend(
            db=db,
            student_id=student_id,
            subject_id=subject_id,
            quiz_id=quiz_id,
            score=score,
        )


@router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh đề thi tự động dựa trên RAG (Tài liệu học tập + AI)",
)
async def generate_new_quiz(
    body: QuizCreateRequest,
    db: Session = Depends(get_db),
    db_mongo: Any = Depends(get_mongodb_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            student_id=current_user.id,
            subject_id=body.subject_id,
            topic=body.topic,
            difficulty=body.difficulty,
            total_questions=body.total_questions,
            study_plan_id=body.study_plan_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi sinh đề thi: {str(exc)}",
        ) from exc


@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
    summary="Xem chi tiết một đề thi (ẩn đáp án đúng)",
)
def get_quiz_by_id(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_quiz(db, quiz_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/{quiz_id}/review",
    response_model=QuizDetailResponse,
    summary="Xem chi tiết đề thi đầy đủ đáp án và giải thích",
)
def get_quiz_review_by_id(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_quiz_review(db, quiz_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get(
    "/plan/{study_plan_id}",
    response_model=QuizResponse,
    summary="Lấy đề thi luyện tập đã liên kết sẵn với lịch học cụ thể",
)
def get_quiz_by_study_plan(
    study_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_quiz_for_study_plan(db, study_plan_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/{quiz_id}/submit",
    response_model=QuizAttemptResponse,
    summary="Nộp bài thi và chấm điểm tự động",
)
def submit_quiz(
    quiz_id: int,
    body: QuizAttemptCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể nộp bài và làm đề thi.",
        )

    try:
        attempt, subject_id = submit_student_quiz(
            db=db,
            quiz_id=quiz_id,
            student_id=current_user.id,
            submitted_answers=body.answers,
            duration_seconds=body.duration_seconds,
        )
        if subject_id is not None:
            background_tasks.add_task(
                _analytics_background,
                current_user.id,
                subject_id,
                quiz_id,
                float(attempt.score),
            )
        
        # Xóa cache dashboard của học sinh ngay lập tức để đồng bộ điểm số mới
        try:
            get_redis().delete(f"dashboard_snapshot:{current_user.id}")
        except Exception:
            pass
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý chấm điểm bài thi: {str(exc)}",
        ) from exc

    return attempt


@router.get(
    "/student/history",
    summary="Học sinh lấy danh sách toàn bộ các đề thi đã làm và điểm số",
)
def api_get_student_attempts_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể xem lịch sử làm bài luyện tập.",
        )
    return get_student_quiz_attempts(db=db, student_id=current_user.id)


@router.post(
    "/teacher/create",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên tự tạo đề thi/bài tập tự soạn gán cho lớp học",
)
def api_teacher_create_quiz(
    body: TeacherQuizCreate,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    return teacher_create_quiz(
        db=db,
        teacher_id=current_teacher.id,
        obj_in=body,
        current_user_role=current_teacher.role,
    )


@router.get(
    "/classroom/{classroom_id}/attempts",
    summary="Giáo viên xem toàn bộ lịch sử điểm số bài làm của học sinh trong lớp",
)
def api_get_classroom_quiz_attempts(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    return get_classroom_quiz_attempts(
        db=db,
        classroom_id=classroom_id,
        current_teacher_id=current_teacher.id,
        current_user_role=current_teacher.role,
    )
