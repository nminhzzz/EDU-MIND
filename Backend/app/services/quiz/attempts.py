"""
Quiz attempt submission and attempt history queries.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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


def submit_quiz_attempt(
    db: Session,
    quiz_id: int,
    student_id: int,
    submitted_answers: List[QuizAttemptAnswer],
    duration_seconds: int,
    essay_file_path: Optional[str] = None,
    tab_violations_count: int = 0,
) -> QuizAttempt:
    """
    Auto-grade a quiz submission, store the attempt, and optionally mark the
    associated daily study plan as done when score >= 8.0.
    """
    quiz = quiz_repository.get(db, quiz_id)
    if not quiz:
        raise ValueError(f"Không tìm thấy đề thi với ID={quiz_id}")

    score, correct_count, wrong_count, answers_json = grade_submission(
        quiz.questions or [], submitted_answers, essay_file_path
    )

    ai_assessment = generate_ai_attempt_feedback(
        quiz_title=quiz.title or "Đề thi",
        questions_list=quiz.questions or [],
        answers_json=answers_json,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
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
        ai_assessment=ai_assessment,
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

    return db_attempt


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
