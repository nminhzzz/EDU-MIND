"""
Quiz read access and submission helpers.
"""

from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.models.classroom_student import ClassroomStudent
from app.models.study_plan import StudyPlan
from app.repositories.classroom_repository import classroom_repository
from app.repositories.attempt_repository import attempt_repository
from app.repositories.quiz_repository import quiz_repository
from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.services.quiz.attempts import submit_quiz_attempt


def get_quiz(db: Session, quiz_id: int) -> Quiz:
    """Return a quiz by id."""
    quiz = quiz_repository.get(db, quiz_id)
    if not quiz:
        raise ValueError("Không tìm thấy đề thi.")
    return quiz


def authorize_student_quiz_access(db: Session, quiz: Quiz, student_id: int) -> None:
    """Enforce object-level access for every student quiz read/submit flow."""
    if quiz.student_id is not None:
        if quiz.student_id != student_id:
            raise PermissionError("Bạn không có quyền truy cập đề thi này.")
        return

    if quiz.study_plan_id is not None:
        owns_plan = db.query(StudyPlan.id).filter(
            StudyPlan.id == quiz.study_plan_id,
            StudyPlan.student_id == student_id,
        ).first()
        if not owns_plan:
            raise PermissionError("Bạn không có quyền truy cập đề thi này.")
        return

    if quiz.classroom_id is not None:
        enrolled = db.query(ClassroomStudent.id).filter(
            ClassroomStudent.classroom_id == quiz.classroom_id,
            ClassroomStudent.student_id == student_id,
        ).first()
        if not enrolled:
            raise PermissionError("Bạn không phải thành viên lớp học được giao đề thi này.")
        return

    raise PermissionError("Đề thi chưa được giao cho tài khoản của bạn.")


def get_quiz_review(db: Session, quiz_id: int, current_user: User) -> Quiz:
    """Return a quiz with answers for review after permission checks."""
    quiz = get_quiz(db, quiz_id)

    if current_user.role == UserRole.STUDENT:
        authorize_student_quiz_access(db, quiz, current_user.id)
        if not attempt_repository.has_attempt(db, quiz_id, current_user.id):
            raise PermissionError(
                "Bạn chưa hoàn thành bài thi này nên không thể xem đáp án giải thích."
            )
    elif current_user.role == UserRole.TEACHER:
        if not quiz.classroom_id:
            raise PermissionError("Bạn không có quyền xem đáp án đề thi này.")
        classroom = classroom_repository.get(db, quiz.classroom_id)
        if not classroom or classroom.teacher_id != current_user.id:
            raise PermissionError("Bạn không có quyền xem đáp án đề thi này.")
    elif current_user.role != UserRole.ADMIN:
        raise PermissionError("Bạn không có quyền xem đáp án đề thi này.")

    # Lấy lượt làm bài gần nhất của học sinh
    latest_attempt = None
    if current_user.role == UserRole.STUDENT:
        latest_attempt = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == current_user.id)
            .order_by(QuizAttempt.submitted_at.desc())
            .first()
        )

    quiz.latest_attempt = latest_attempt
    return quiz


def get_quiz_for_study_plan(
    db: Session, study_plan_id: int, student_id: int
) -> Quiz:
    """Return the quiz linked to a student's study plan."""
    quiz = quiz_repository.get_for_student_by_plan(db, study_plan_id, student_id)
    if not quiz:
        raise ValueError("Không tìm thấy đề thi liên kết với lịch học này.")
    return quiz


def submit_student_quiz(
    db: Session,
    *,
    quiz_id: int,
    student_id: int,
    submitted_answers: list[QuizAttemptAnswer],
    duration_seconds: int,
    essay_file_path: Optional[str] = None,
    tab_violations_count: int = 0,
) -> Tuple[QuizAttempt, Optional[int], str, list, list]:
    """
    Submit a quiz attempt and return the attempt, subject_id, quiz_title, questions_list, and answers_json.
    """
    attempt, quiz_title, questions_list, answers_json = submit_quiz_attempt(
        db=db,
        quiz_id=quiz_id,
        student_id=student_id,
        submitted_answers=submitted_answers,
        duration_seconds=duration_seconds,
        essay_file_path=essay_file_path,
        tab_violations_count=tab_violations_count,
    )
    quiz = quiz_repository.get(db, quiz_id)
    subject_id = quiz.subject_id if quiz else None
    return attempt, subject_id, quiz_title, questions_list, answers_json


def get_student_assigned_quizzes_service(db: Session, student_id: int) -> list[Quiz]:
    """Retrieve all classroom quizzes assigned to a student."""
    from app.models.classroom_student import ClassroomStudent
    classrooms = db.query(ClassroomStudent.classroom_id).filter(
        ClassroomStudent.student_id == student_id
    ).all()
    classroom_ids = [c[0] for c in classrooms]

    if not classroom_ids:
        return []

    return db.query(Quiz).filter(Quiz.classroom_id.in_(classroom_ids)).all()

