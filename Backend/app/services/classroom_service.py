"""
Service xử lý các nghiệp vụ liên quan đến Lớp học (Classrooms) — Giai đoạn 4.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException


from app.models.user import User
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.schemas.classroom import ClassroomCreate
from app.repositories.classroom_repository import classroom_repository
from app.repositories.classroom_student_repository import classroom_student_repository


def create_classroom(
    db: Session, teacher_id: int, obj_in: ClassroomCreate
) -> Classroom:
    """Giáo viên tạo lớp học mới."""
    # Kiểm tra tính duy nhất của class_code
    existing = classroom_repository.get_by_code(db, obj_in.class_code)
    if existing:
        raise ValueError(f"Mã lớp học '{obj_in.class_code}' đã tồn tại trong hệ thống.")

    # Kiểm tra môn học tồn tại
    subject = db.query(Subject).filter(Subject.id == obj_in.subject_id).first()
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={obj_in.subject_id}.")

    # Tạo bản ghi
    db_obj = Classroom(
        teacher_id=teacher_id,
        subject_id=obj_in.subject_id,
        class_name=obj_in.class_name,
        class_code=obj_in.class_code,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_classrooms_for_user(db: Session, user: User) -> List[Classroom]:
    """Lấy danh sách các lớp học của người dùng dựa theo vai trò."""
    if user.role == "teacher":
        return classroom_repository.get_by_teacher(db, user.id)
    elif user.role == "student":
        return classroom_repository.get_by_student(db, user.id)
    return []


def get_classroom_detail(db: Session, classroom_id: int, user: User) -> Dict[str, Any]:
    """Xem chi tiết lớp học kèm danh sách học sinh và môn học."""
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise ValueError(f"Không tìm thấy lớp học với ID={classroom_id}.")

    # Kiểm tra quyền truy cập lớp học
    if user.role == "teacher":
        if classroom.teacher_id != user.id:
            raise PermissionError("Bạn không có quyền quản lý lớp học này.")
    elif user.role == "student":
        relation = classroom_student_repository.get_by_relation(
            db, classroom_id, user.id
        )
        if not relation:
            raise PermissionError("Bạn chưa tham gia lớp học này.")

    # Lấy danh sách học sinh và môn học từ các mối quan hệ
    students_list = [cs.student for cs in classroom.students if cs.student]
    subject = classroom.subject

    return {
        "classroom": classroom,
        "teacher": classroom.teacher,
        "students": students_list,
        "subject": subject,
    }


def add_student_to_classroom(
    db: Session, classroom_id: int, teacher_id: int, student_email: str
) -> ClassroomStudent:
    """Giáo viên chủ động thêm học sinh vào lớp bằng Email."""
    # 1. Kiểm tra lớp học và quyền giáo viên
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise ValueError(f"Không tìm thấy lớp học với ID={classroom_id}.")
    if classroom.teacher_id != teacher_id:
        raise PermissionError("Bạn không có quyền quản lý lớp học này.")

    # 2. Tìm học sinh
    student = (
        db.query(User)
        .filter(User.email == student_email, User.role == "student")
        .first()
    )
    if not student:
        raise ValueError(f"Không tìm thấy học sinh có email: {student_email}")

    # 3. Kiểm tra xem học sinh đã có trong lớp chưa
    existing = classroom_student_repository.get_by_relation(
        db, classroom_id, student.id
    )
    if existing:
        raise ValueError(f"Học sinh '{student.full_name}' đã tham gia lớp học này rồi.")

    # 4. Thêm học sinh
    db_relation = ClassroomStudent(classroom_id=classroom_id, student_id=student.id)
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def student_join_classroom(
    db: Session, student_id: int, class_code: str
) -> ClassroomStudent:
    """Học sinh tự tham gia lớp học bằng mã lớp (class_code)."""
    # 1. Tìm lớp học theo mã
    classroom = classroom_repository.get_by_code(db, class_code)
    if not classroom:
        raise ValueError(f"Mã lớp học '{class_code}' không hợp lệ hoặc không tồn tại.")

    # 2. Kiểm tra xem học sinh đã có trong lớp chưa
    existing = classroom_student_repository.get_by_relation(
        db, classroom.id, student_id
    )
    if existing:
        raise ValueError(f"Bạn đã tham gia lớp học '{classroom.class_name}' này rồi.")

    # 3. Cho tham gia lớp
    db_relation = ClassroomStudent(classroom_id=classroom.id, student_id=student_id)
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def get_classroom_students_progress(
    db: Session, classroom_id: int, current_teacher_id: int, current_user_role: str
) -> List[Dict[str, Any]]:
    """Giáo viên hoặc Admin lấy báo cáo học tập của học sinh trong lớp học."""
    from sqlalchemy import func
    from app.models.study_goal import StudyGoal
    from app.models.quiz_attempt import QuizAttempt
    from app.models.user import User as DBUser

    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")

    if current_user_role != "admin" and classroom.teacher_id != current_teacher_id:
        raise HTTPException(
            status_code=403, detail="Bạn không có quyền quản lý lớp học này."
        )

    enrollments = (
        db.query(ClassroomStudent)
        .filter(ClassroomStudent.classroom_id == classroom_id)
        .all()
    )

    response = []
    for en in enrollments:
        student = db.query(DBUser).filter(DBUser.id == en.student_id).first()
        if not student:
            continue

        total_goals = (
            db.query(StudyGoal).filter(StudyGoal.student_id == student.id).count()
        )
        completed_goals = (
            db.query(StudyGoal)
            .filter(StudyGoal.student_id == student.id, StudyGoal.status == "completed")
            .count()
        )
        total_attempts = (
            db.query(QuizAttempt).filter(QuizAttempt.student_id == student.id).count()
        )

        avg_score = (
            db.query(func.avg(QuizAttempt.score))
            .filter(QuizAttempt.student_id == student.id)
            .scalar()
        )
        if avg_score is not None:
            avg_score = float(avg_score)

        response.append(
            {
                "student_id": student.id,
                "email": student.email,
                "full_name": student.full_name,
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "total_attempts": total_attempts,
                "average_score": avg_score,
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

    if current_user_role != "admin" and classroom.teacher_id != current_user_id:
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
    db.commit()


def list_all_classrooms_admin(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Classroom]:
    """Admin lấy toàn bộ danh sách lớp học."""
    return classroom_repository.get_multi(db, skip=skip, limit=limit)
