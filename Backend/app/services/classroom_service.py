"""
Service xử lý các nghiệp vụ liên quan đến Lớp học (Classrooms).
"""

from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.database.unit_of_work import commit_or_rollback
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.user import User
from app.repositories.attempt_repository import attempt_repository
from app.repositories.classroom_repository import classroom_repository
from app.repositories.classroom_student_repository import classroom_student_repository
from app.repositories.goal_repository import goal_repository
from app.repositories.subject_repository import subject_repository
from app.repositories.user_repository import user_repository
from app.schemas.classroom import ClassroomCreate


def create_classroom(
    db: Session, teacher_id: int, obj_in: ClassroomCreate
) -> Classroom:
    """Giáo viên tạo lớp học mới."""
    existing = classroom_repository.get_by_code(db, obj_in.class_code)
    if existing:
        raise ValueError(f"Mã lớp học '{obj_in.class_code}' đã tồn tại trong hệ thống.")

    if not subject_repository.get(db, obj_in.subject_id):
        raise ValueError(f"Không tìm thấy môn học với ID={obj_in.subject_id}.")

    db_obj = classroom_repository.stage_classroom(
        db,
        teacher_id=teacher_id,
        subject_id=obj_in.subject_id,
        class_name=obj_in.class_name,
        class_code=obj_in.class_code,
        description=obj_in.description,
    )
    commit_or_rollback(db)
    db.refresh(db_obj)
    return db_obj


def get_classrooms_for_user(db: Session, user: User) -> List[dict]:
    """Lấy danh sách các lớp học của người dùng dựa theo vai trò."""
    from app.schemas.classroom import ClassroomResponse

    if user.role == UserRole.TEACHER:
        classrooms = classroom_repository.get_by_teacher(db, user.id)
    elif user.role == UserRole.STUDENT:
        classrooms = classroom_repository.get_by_student(db, user.id)
    else:
        return []

    return [
        ClassroomResponse.model_validate(cls).model_dump()
        | {
            "student_count": classroom_student_repository.count_by_classroom(
                db, cls.id
            )
        }
        for cls in classrooms
    ]


def get_classroom_detail(db: Session, classroom_id: int, user: User) -> Dict[str, Any]:
    """Xem chi tiết lớp học kèm danh sách học sinh và môn học."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise ValueError(f"Không tìm thấy lớp học với ID={classroom_id}.")

    if user.role == UserRole.TEACHER:
        if classroom.teacher_id != user.id:
            raise PermissionError("Bạn không có quyền quản lý lớp học này.")
    elif user.role == UserRole.STUDENT:
        relation = classroom_student_repository.get_by_relation(
            db, classroom_id, user.id
        )
        if not relation:
            raise PermissionError("Bạn chưa tham gia lớp học này.")

    students_list = [cs.student for cs in classroom.students if cs.student]

    return {
        "classroom": classroom,
        "teacher": classroom.teacher,
        "students": students_list,
        "subject": classroom.subject,
    }


def add_student_to_classroom(
    db: Session, classroom_id: int, teacher_id: int, student_email: str
) -> ClassroomStudent:
    """Giáo viên chủ động thêm học sinh vào lớp bằng Email."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise ValueError(f"Không tìm thấy lớp học với ID={classroom_id}.")
    if classroom.teacher_id != teacher_id:
        raise PermissionError("Bạn không có quyền quản lý lớp học này.")

    student = user_repository.get_student_by_email(db, student_email)
    if not student:
        raise ValueError(f"Không tìm thấy học sinh có email: {student_email}")

    existing = classroom_student_repository.get_by_relation(
        db, classroom_id, student.id
    )
    if existing:
        raise ValueError(f"Học sinh '{student.full_name}' đã tham gia lớp học này rồi.")

    db_relation = classroom_student_repository.stage_enrollment(
        db, classroom_id, student.id
    )
    commit_or_rollback(db)
    db.refresh(db_relation)
    return db_relation


def student_join_classroom(
    db: Session, student_id: int, class_code: str
) -> ClassroomStudent:
    """Học sinh tự tham gia lớp học bằng mã lớp (class_code)."""
    classroom = classroom_repository.get_by_code(db, class_code)
    if not classroom:
        raise ValueError(f"Mã lớp học '{class_code}' không hợp lệ hoặc không tồn tại.")

    existing = classroom_student_repository.get_by_relation(
        db, classroom.id, student_id
    )
    if existing:
        raise ValueError(f"Bạn đã tham gia lớp học '{classroom.class_name}' này rồi.")

    db_relation = classroom_student_repository.stage_enrollment(
        db, classroom.id, student_id
    )
    commit_or_rollback(db)
    db.refresh(db_relation)
    return db_relation


def get_classroom_students_progress(
    db: Session, classroom_id: int, current_teacher_id: int, current_user_role: str
) -> List[Dict[str, Any]]:
    """Giáo viên hoặc Admin lấy báo cáo học tập của học sinh trong lớp học."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")

    if current_user_role != UserRole.ADMIN and classroom.teacher_id != current_teacher_id:
        raise HTTPException(
            status_code=403, detail="Bạn không có quyền quản lý lớp học này."
        )

    enrollments = classroom_student_repository.get_by_classroom(db, classroom_id)

    response = []
    for enrollment in enrollments:
        student = user_repository.get(db, enrollment.student_id)
        if not student:
            continue

        response.append(
            {
                "student_id": student.id,
                "email": student.email,
                "full_name": student.full_name,
                "total_goals": goal_repository.count_for_student(db, student.id),
                "completed_goals": goal_repository.count_completed_for_student(
                    db, student.id
                ),
                "total_attempts": attempt_repository.count_for_student(db, student.id),
                "average_score": attempt_repository.avg_score_for_student(
                    db, student.id
                ),
            }
        )

    return response


def remove_student_from_classroom(
    db: Session,
    classroom_id: int,
    student_id: int,
    current_user_id: int,
    current_user_role: str,
) -> None:
    """Giáo viên hoặc Admin xóa học sinh khỏi lớp học."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")

    if current_user_role != UserRole.ADMIN and classroom.teacher_id != current_user_id:
        raise HTTPException(
            status_code=403, detail="Bạn không có quyền quản lý lớp học này."
        )

    enrollment = classroom_student_repository.get_by_relation(
        db, classroom_id, student_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=404, detail="Học sinh không tham gia lớp học này."
        )

    db.delete(enrollment)
    commit_or_rollback(db)


def list_all_classrooms_admin(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Classroom]:
    """Admin lấy toàn bộ danh sách lớp học."""
    return classroom_repository.get_multi(db, skip=skip, limit=limit)
