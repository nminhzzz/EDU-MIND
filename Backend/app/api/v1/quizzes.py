"""
API quản lý Đề thi và Chấm bài (Quizzes & Question Bank) — Giai đoạn 3 & 4.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.database.mongodb import get_mongodb_db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import QuizCreateRequest, QuizResponse, QuizDetailResponse
from app.schemas.quiz_attempt import QuizAttemptCreate, QuizAttemptResponse
from app.services.quiz_service import generate_and_save_quiz, submit_quiz_attempt
from app.services.analytic_service import update_student_analytics_and_recommend

router = APIRouter()


@router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh đề thi tự động dựa trên RAG (Tài liệu học tập + AI)",
    description="""
    Hệ thống sẽ thực hiện Vector Search trên MongoDB để tìm tài liệu liên quan đến chủ đề,
    sau đó chuyển làm ngữ cảnh cho AI Agent sinh đề thi bám sát tài liệu.
    Đề thi sau đó sẽ được lưu vào MySQL.
    """,
)
async def generate_new_quiz(
    body: QuizCreateRequest,
    db: Session = Depends(get_db),
    db_mongo: Any = Depends(get_mongodb_db),
    current_user: User = Depends(get_current_user),
):
    # Học sinh tự sinh hoặc Giáo viên sinh đề cho Học sinh
    student_id = current_user.id
    if current_user.role == "teacher":
        # Với giáo viên, sinh đề thi thử nghiệm cho chính họ
        student_id = current_user.id

    try:
        quiz = await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            student_id=student_id,
            subject_id=body.subject_id,
            topic=body.topic,
            difficulty=body.difficulty,
            total_questions=body.total_questions,
            study_plan_id=body.study_plan_id,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi sinh đề thi: {str(e)}",
        )

    return quiz


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
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đề thi."
        )
    return quiz


@router.get(
    "/{quiz_id}/review",
    response_model=QuizDetailResponse,
    summary="Xem chi tiết đề thi đầy đủ đáp án và giải thích",
)
def get_quiz_review(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đề thi."
        )

    # Quyền kiểm tra: giáo viên hoặc học sinh đã làm bài thi này
    if current_user.role != "teacher":
        attempt = (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.student_id == current_user.id,
            )
            .first()
        )
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chưa hoàn thành bài thi này nên không thể xem đáp án giải thích.",
            )

    return quiz


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
    quiz = (
        db.query(Quiz)
        .filter(Quiz.study_plan_id == study_plan_id, Quiz.student_id == current_user.id)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đề thi liên kết với lịch học này.",
        )
    return quiz


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
    # Kiểm tra quyền làm bài (chỉ học sinh)
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể nộp bài và làm đề thi.",
        )

    try:
        attempt = submit_quiz_attempt(
            db=db,
            quiz_id=quiz_id,
            student_id=current_user.id,
            submitted_answers=body.answers,
            duration_seconds=body.duration_seconds,
        )

        # Trigger AI evaluation and recommendation in background
        quiz_obj = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quiz_obj:
            background_tasks.add_task(
                update_student_analytics_and_recommend,
                db,
                current_user.id,
                quiz_obj.subject_id,
                quiz_id,
                float(attempt.score),
            )

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý chấm điểm bài thi: {str(e)}",
        )

    return attempt


@router.get(
    "/student/history",
    summary="Học sinh lấy danh sách toàn bộ các đề thi đã làm và điểm số",
)
def api_get_student_attempts_history(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    from app.services.quiz_service import get_student_quiz_attempts

    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể xem lịch sử làm bài luyện tập.",
        )
    return get_student_quiz_attempts(db=db, student_id=current_user.id)


# ── TEACHER ASSIGNMENTS & ATTEMPTS ──

from app.api.deps import get_current_teacher
from app.schemas.teacher import TeacherQuizCreate
from app.services.quiz_service import teacher_create_quiz, get_classroom_quiz_attempts


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
