"""
Teacher-managed quiz creation.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.database.unit_of_work import commit_or_rollback
from app.models.quiz import Quiz
from app.repositories.classroom_repository import classroom_repository
from app.repositories.quiz_repository import quiz_repository
from app.schemas.teacher import TeacherQuizCreate


def teacher_create_quiz(
    db: Session,
    teacher_id: int,
    obj_in: TeacherQuizCreate,
    current_user_role: str,
) -> Quiz:
    """Teacher or admin manually creates a quiz assigned to a classroom."""
    classroom = classroom_repository.get(db, obj_in.classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lớp học.",
        )

    if current_user_role != UserRole.ADMIN and classroom.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền đăng tải bài tập vào lớp học này.",
        )

    db_quiz = quiz_repository.stage_teacher_quiz(
        db,
        teacher_id=teacher_id,
        subject_id=obj_in.subject_id,
        classroom_id=obj_in.classroom_id,
        title=obj_in.title,
        difficulty=obj_in.difficulty,
        questions=obj_in.questions,
    )

    commit_or_rollback(db)
    db.refresh(db_quiz)
    return db_quiz
