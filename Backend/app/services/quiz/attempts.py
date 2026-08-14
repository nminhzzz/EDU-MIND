"""
Quiz attempt submission and attempt history queries.
"""

import logging

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.enums import UserRole
from app.database.unit_of_work import commit_or_rollback
from app.models.quiz_attempt import QuizAttempt
from app.repositories.attempt_repository import attempt_repository
from app.repositories.classroom_repository import classroom_repository
from app.repositories.plan_repository import plan_repository
from app.repositories.quiz_repository import quiz_repository
from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.services.quiz.grading import (
    PLAN_PASS_SCORE_THRESHOLD,
    generate_ai_attempt_feedback,
    grade_submission,
)
from app.services.outbox_service import stage_outbox_job

DAILY_TASK_QUIZ_LABEL = "NHIỆM VỤ NGÀY"
_INVALID_QUIZ_TITLES = frozenset({"quizresponse", ""})


def resolve_quiz_display_title(quiz) -> str:
    """Tên hiển thị trong lịch sử: nhiệm vụ ngày vs đề luyện thi."""
    if quiz.study_plan_id:
        return DAILY_TASK_QUIZ_LABEL

    title = (quiz.title or "").strip()
    if title.lower() not in _INVALID_QUIZ_TITLES:
        return title

    subject_name = quiz.subject.name if getattr(quiz, "subject", None) else "môn học"
    return f"Đề luyện thi {subject_name}"


def process_ai_quiz_assessment_background(
    attempt_id: int,
    quiz_title: str,
    questions_list: List[Dict[str, Any]],
    answers_json: List[Dict[str, Any]],
    score: float,
    correct_count: int,
    wrong_count: int,
) -> None:
    """
    Background Task: Generate AI Diagnostic Assessment asynchronously and update QuizAttempt.ai_assessment in MySQL.
    """
    from app.database.mysql import SessionLocal
    from app.models.quiz_attempt import QuizAttempt as DBQuizAttempt

    db = SessionLocal()
    try:
        logger.info("Chạy ngầm AI Assessment cho attempt_id=%d...", attempt_id)
        ai_assessment = generate_ai_attempt_feedback(
            quiz_title=quiz_title,
            questions_list=questions_list,
            answers_json=answers_json,
            score=score,
            correct_count=correct_count,
            wrong_count=wrong_count,
        )
        attempt = db.query(DBQuizAttempt).filter(DBQuizAttempt.id == attempt_id).first()
        if attempt:
            attempt.ai_assessment = ai_assessment
            db.commit()
            logger.info("Đã hoàn tất sinh AI Assessment ngầm cho attempt_id=%d!", attempt_id)
    except Exception as exc:
        db.rollback()
        logger.error("Lỗi khi sinh AI Assessment ngầm cho attempt_id=%d: %s", attempt_id, exc)
        raise
    finally:
        db.close()


def submit_quiz_attempt(
    db: Session,
    quiz_id: int,
    student_id: int,
    submitted_answers: List[QuizAttemptAnswer],
    duration_seconds: int,
    essay_file_path: Optional[str] = None,
    tab_violations_count: int = 0,
) -> Tuple[QuizAttempt, str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Auto-grade a quiz submission instantly (<50ms), store the attempt with ai_assessment=None,
    and return metadata for background AI evaluation.
    """
    quiz = quiz_repository.get(db, quiz_id)
    if not quiz:
        raise ValueError(f"Không tìm thấy đề thi với ID={quiz_id}")

    question_count = len(quiz.questions or [])
    indices = [answer.question_index for answer in submitted_answers]
    if len(indices) != len(set(indices)):
        raise ValueError("Danh sách câu trả lời chứa chỉ mục câu hỏi bị trùng.")
    if any(index >= question_count for index in indices):
        raise ValueError("Danh sách câu trả lời chứa chỉ mục ngoài phạm vi đề thi.")
    if quiz.time_limit_minutes and duration_seconds > quiz.time_limit_minutes * 60 + 60:
        raise ValueError("Thời gian làm bài vượt quá giới hạn cho phép.")

    score, correct_count, wrong_count, answers_json = grade_submission(
        quiz.questions or [], submitted_answers, essay_file_path
    )

    db_attempt = attempt_repository.stage_attempt(
        db,
        quiz_id=quiz_id,
        student_id=student_id,
        answers=answers_json,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
        duration_seconds=duration_seconds,
        tab_violations_count=tab_violations_count,
        ai_assessment=None,
    )
    db.flush()
    stage_outbox_job(
        db,
        task_name="app.workers.tasks.task_generate_attempt_assessment",
        args=[db_attempt.id],
        unique_key=f"attempt-assessment:{db_attempt.id}",
    )
    if quiz.subject_id is not None:
        stage_outbox_job(
            db,
            task_name="app.workers.tasks.task_update_analytics",
            args=[student_id, quiz.subject_id, quiz_id, float(score)],
            unique_key=f"attempt-analytics:{db_attempt.id}",
        )
    commit_or_rollback(db)
    db.refresh(db_attempt)

    if quiz.study_plan_id and score >= PLAN_PASS_SCORE_THRESHOLD:
        plan = plan_repository.get(db, quiz.study_plan_id)
        if plan:
            plan_repository.mark_completed(
                db, plan, student_id, datetime.now(timezone.utc)
            )
            commit_or_rollback(db)

    return db_attempt, quiz.title or "Đề thi", quiz.questions or [], answers_json


def get_classroom_quiz_attempts(
    db: Session,
    classroom_id: int,
    current_teacher_id: int,
    current_user_role: str,
) -> List[Dict]:
    """Teacher or admin retrieves all student quiz attempts for a classroom."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lớp học.",
        )

    if current_user_role != UserRole.ADMIN and classroom.teacher_id != current_teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thông tin điểm số lớp học này.",
        )

    attempts = attempt_repository.get_classroom_attempts_with_users(db, classroom_id)

    return [
        {
            "attempt_id": att.id,
            "quiz_id": qz.id,
            "quiz_title": resolve_quiz_display_title(qz),
            "student_id": usr.id,
            "student_name": usr.full_name,
            "student_email": usr.email,
            "score": float(att.score),
            "correct_count": att.correct_count,
            "wrong_count": att.wrong_count,
            "duration_seconds": att.duration_seconds,
            "tab_violations_count": att.tab_violations_count,
            "submitted_at": att.submitted_at,
        }
        for att, qz, usr in attempts
    ]


def get_student_quiz_attempts(db: Session, student_id: int) -> List[Dict]:
    """Return all quiz attempts for a student, ordered by most recent."""
    attempts = attempt_repository.get_with_quiz_by_student(db, student_id)

    return [
        {
            "attempt_id": att.id,
            "quiz_id": qz.id,
            "quiz_title": resolve_quiz_display_title(qz),
            "score": float(att.score),
            "correct_count": att.correct_count,
            "wrong_count": att.wrong_count,
            "duration_seconds": att.duration_seconds,
            "tab_violations_count": att.tab_violations_count,
            "submitted_at": att.submitted_at,
        }
        for att, qz in attempts
    ]
