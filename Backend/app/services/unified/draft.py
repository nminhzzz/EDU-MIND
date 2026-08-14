from datetime import date
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.roadmap_planner import generate_unified_plan
from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.study_document import StudyDocument
from app.models.subject import Subject
from app.models.user import User
from app.services.embedding_service import get_document_chunks_from_mongo
from app.services.unified.validators import load_student_preferences

logger = get_logger(__name__)


async def generate_unified_draft(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    classroom_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Sinh lộ trình hợp nhất (tùy chọn thu gọn theo Lớp học & Tài liệu Giáo viên upload).
    """
    db_mongo = get_mongodb_db()

    study_hours_per_day, preferred_time_vn, off_days, available_schedule = (
        load_student_preferences(student.id)
    )

    classroom_context: Optional[str] = None

    if classroom_id and db:
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if classroom:
            enrollment = db.query(ClassroomStudent.id).filter(
                ClassroomStudent.classroom_id == classroom_id,
                ClassroomStudent.student_id == student.id,
            ).first()
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không phải thành viên của lớp học này.",
                )
            if classroom.subject_id != subject_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Lớp học không thuộc môn học đã chọn.",
                )
            teacher_id = classroom.teacher_id
            # Lấy tất cả tài liệu do giáo viên của lớp học này upload trong môn học
            teacher_docs = (
                db.query(StudyDocument)
                .filter(
                    StudyDocument.created_by == teacher_id,
                    StudyDocument.subject_id == subject_obj.id,
                )
                .all()
            )

            all_chunks = []
            doc_titles = []
            for doc in teacher_docs:
                doc_titles.append(doc.title)
                chunks = await get_document_chunks_from_mongo(db_mongo, doc.id)
                all_chunks.extend(chunks)

            if all_chunks:
                joined_text = "\n\n".join(all_chunks)[:12000]
                classroom_context = (
                    f"--- TÀI LIỆU DẠY VÀ HỌC TRONG LỚP '{classroom.class_name}' (GIÁO VIÊN UPLOAD) ---\n"
                    f"Danh sách tài liệu của lớp: {', '.join(doc_titles)}\n"
                    f"Nội dung tài liệu trích xuất:\n{joined_text}\n"
                    f"----------------------------------------------------\n"
                    f"YÊU CẦU ĐẶC THÙ LỚP HỌC: Bắt buộc lập lộ trình học tập bám sát đúng danh sách tài liệu và nội dung trên của Lớp học!"
                )
            else:
                classroom_context = (
                    f"--- LƯU Ý LỚP HỌC '{classroom.class_name}' ---\n"
                    f"Giáo viên của lớp chưa tải lên tài liệu học tập riêng nào. Hãy lập lộ trình học tập dựa trên chuẩn kiến thức chung của môn học '{subject_obj.name}'."
                )

    current_date = date.today().strftime("%Y-%m-%d")
    try:
        plan = await generate_unified_plan(
            subject=subject_obj.name,
            target_score=target_score,
            deadline=deadline,
            student_id=student.id,
            subject_id=subject_obj.id,
            study_hours_per_day=study_hours_per_day,
            preferred_time=preferred_time_vn,
            off_days=off_days,
            current_date=current_date,
            available_schedule=available_schedule,
            db_mongo=db_mongo,
            classroom_context=classroom_context,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    return {"plan": plan}
