"""
API quản lý Đề thi và Chấm bài (Quizzes & Question Bank).
"""

import os
import uuid
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher, get_current_user, get_db
from app.core.enums import UserRole
from app.database.mongodb import get_mongodb_db
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.quiz import QuizDetailResponse, QuizResponse, ClassroomQuizCreateRequest
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
from app.services.quiz import generate_classroom_quiz
from app.repositories.classroom_repository import classroom_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.classroom_student_repository import classroom_student_repository
from app.models.classroom_student import ClassroomStudent
from app.models.quiz import Quiz

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


# ============================================================================
# 1. SPECIFIC / STATIC PATH ROUTES (MUST COME BEFORE GENERAL /{quiz_id} PATHS)
# ============================================================================

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
    "/plan/{study_plan_id}/generate",
    response_model=QuizResponse,
    summary="Sinh đề kiểm tra nhanh cho nhiệm vụ ngày học sinh",
)
async def generate_quiz_for_plan(
    study_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể sinh đề luyện tập.",
        )
    
    from app.models.study_plan import StudyPlan
    plan = db.query(StudyPlan).filter(StudyPlan.id == study_plan_id, StudyPlan.student_id == current_user.id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhiệm vụ học tập này.",
        )

    # Kiểm tra xem đề thi đã tồn tại chưa
    existing_quiz = quiz_repository.get_for_student_by_plan(db, study_plan_id, current_user.id)
    if existing_quiz:
        return existing_quiz

    try:
        from app.database.unit_of_work import commit_or_rollback
        
        db_mongo = get_mongodb_db()
        quiz = await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            student_id=current_user.id,
            subject_id=plan.subject_id,
            topic=plan.title,
            difficulty="medium",
            total_questions=5,
            study_plan_id=study_plan_id,
        )
        commit_or_rollback(db)
        return quiz
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi sinh đề thi AI: {str(exc)}",
        ) from exc


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


@router.get(
    "/student/assigned",
    response_model=List[QuizResponse],
    summary="Học sinh lấy danh sách tất cả các bài tập/đề thi được giao từ các lớp học",
)
def get_student_assigned_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Chỉ học sinh mới có bài tập được giao.")

    classrooms = db.query(ClassroomStudent.classroom_id).filter(
        ClassroomStudent.student_id == current_user.id
    ).all()
    classroom_ids = [c[0] for c in classrooms]

    if not classroom_ids:
        return []

    quizzes = db.query(Quiz).filter(Quiz.classroom_id.in_(classroom_ids)).all()
    return quizzes


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


@router.post(
    "/classrooms/{classroom_id}/generate",
    response_model=QuizDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên sinh đề thi tự động cho lớp học bằng AI",
)
async def generate_classroom_quiz_api(
    classroom_id: int,
    body: ClassroomQuizCreateRequest,
    db: Session = Depends(get_db),
    db_mongo: Any = Depends(get_mongodb_db),
    current_teacher: User = Depends(get_current_teacher),
):
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")
    if classroom.teacher_id != current_teacher.id and current_teacher.role != "admin":
        raise HTTPException(status_code=403, detail="Bạn không phải là giáo viên của lớp học này.")

    try:
        return await generate_classroom_quiz(
            db=db,
            db_mongo=db_mongo,
            subject_id=body.subject_id,
            classroom_id=classroom_id,
            topic=body.topic,
            difficulty=body.difficulty,
            total_questions=body.total_questions,
            deadline=body.deadline,
            include_essay=body.include_essay,
            essay_count=body.essay_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi sinh đề thi: {str(exc)}",
        )


@router.get(
    "/classrooms/{classroom_id}",
    response_model=List[QuizResponse],
    summary="Lấy danh sách các đề thi được giao cho lớp học",
)
def get_classroom_quizzes_list(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "student":
        enrollment = classroom_student_repository.get_by_relation(db, classroom_id=classroom_id, student_id=current_user.id)
        if not enrollment:
            raise HTTPException(status_code=403, detail="Bạn không phải thành viên lớp học này.")
    elif current_user.role == "teacher":
        classroom = classroom_repository.get(db, classroom_id)
        if not classroom or (classroom.teacher_id != current_user.id and current_user.role != "admin"):
            raise HTTPException(status_code=403, detail="Bạn không phải giáo viên quản lý lớp học này.")

    return quiz_repository.get_by_classroom(db, classroom_id)


UPLOAD_DIR = "uploads/classroom_quizzes"


@router.post(
    "/upload-essay",
    summary="Tải lên tệp bài làm tự luận của học sinh (hình ảnh, PDF, Word, TXT)",
)
async def upload_essay_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng tệp không được hỗ trợ. Vui lòng chọn file ảnh, PDF, Word hoặc TXT.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi lưu tệp tin: {str(exc)}",
        ) from exc

    return {"file_path": file_path}


# ============================================================================
# 2. PARAMETERIZED /{quiz_id} PATH ROUTES (MUST COME LAST)
# ============================================================================

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
            essay_file_path=body.essay_file_path,
            tab_violations_count=body.tab_violations_count,
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
