"""
API quản lý Đề thi và Chấm bài (Quizzes & Question Bank) — Giai đoạn 3.
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user
from app.database.mongodb import get_mongodb_db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import QuizCreateRequest, QuizResponse, QuizDetailResponse, QuestionBankResponse, QuestionBankDetailResponse
from app.schemas.quiz_attempt import QuizAttemptCreate, QuizAttemptResponse
from app.services.quiz_service import generate_and_save_quiz, submit_quiz_attempt
from app.services.analytic_service import update_student_analytics_and_recommend

router = APIRouter()


# ── POST /quizzes/generate — Sinh đề thi tự động bằng RAG ───────────
@router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh đề thi tự động dựa trên RAG (Tài liệu học tập + AI)",
    description="""
    Hệ thống sẽ thực hiện Vector Search trên MongoDB để tìm tài liệu liên quan đến chủ đề,
    sau đó chuyển làm ngữ cảnh cho AI Agent sinh đề thi bám sát tài liệu.
    Đề thi sau đó sẽ được lưu vào MySQL.
    """
)
async def generate_new_quiz(
    body: QuizCreateRequest,
    db: Session = Depends(get_db),
    db_mongo: Any = Depends(get_mongodb_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Nếu là giáo viên, truyền teacher_id của họ. Nếu học sinh tự sinh, teacher_id = None
        teacher_id = current_user.id if current_user.role == "teacher" else None

        quiz = await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            classroom_id=body.classroom_id,
            subject_id=body.subject_id,
            topic=body.topic,
            difficulty=body.difficulty,
            total_questions=body.total_questions,
            question_type=body.question_type,
            teacher_id=teacher_id
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi sinh đề thi: {str(e)}"
        )

    # Nạp câu hỏi từ junction table để khớp response model
    questions_list = []
    for q_junction in quiz.questions:
        qb_item = q_junction.question_bank_item
        if qb_item:
            questions_list.append(qb_item)

    # Gán tạm để serialize qua response_model
    quiz.questions = questions_list
    return quiz


# ── GET /quizzes/{quiz_id} — Xem chi tiết đề thi (không hiện đáp án) ───
@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
    summary="Xem chi tiết một đề thi (ẩn đáp án đúng)"
)
def get_quiz_by_id(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(Question.question_bank_item))
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đề thi."
        )

    # Nạp câu hỏi
    questions_list = []
    for q_junction in quiz.questions:
        qb_item = q_junction.question_bank_item
        if qb_item:
            questions_list.append(qb_item)

    quiz.questions = questions_list
    return quiz


# ── GET /quizzes/{quiz_id}/review — Xem chi tiết đề thi có đáp án (Giáo viên / Học sinh đã nộp) ───
@router.get(
    "/{quiz_id}/review",
    response_model=QuizDetailResponse,
    summary="Xem chi tiết đề thi đầy đủ đáp án và giải thích"
)
def get_quiz_review(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Lấy đề thi
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(Question.question_bank_item))
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đề thi."
        )

    # Quyền kiểm tra: giáo viên hoặc học sinh đã làm bài thi này
    if current_user.role != "teacher":
        attempt = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == current_user.id)
            .first()
        )
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chưa hoàn thành bài thi này nên không thể xem đáp án giải thích."
            )

    # Nạp câu hỏi đầy đủ đáp án
    questions_list = []
    for q_junction in quiz.questions:
        qb_item = q_junction.question_bank_item
        if qb_item:
            questions_list.append(qb_item)

    quiz.questions = questions_list
    return quiz


# ── POST /quizzes/{quiz_id}/submit — Nộp bài thi và chấm điểm ───────
@router.post(
    "/{quiz_id}/submit",
    response_model=QuizAttemptResponse,
    summary="Nộp bài thi và chấm điểm tự động"
)
def submit_quiz(
    quiz_id: int,
    body: QuizAttemptCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Kiểm tra quyền làm bài (chỉ học sinh)
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh mới có thể nộp bài và làm đề thi."
        )

    try:
        attempt = submit_quiz_attempt(
            db=db,
            quiz_id=quiz_id,
            student_id=current_user.id,
            submitted_answers=body.answers,
            duration_seconds=body.duration_seconds
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
                float(attempt.score)
            )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý chấm điểm bài thi: {str(e)}"
        )

    return attempt
