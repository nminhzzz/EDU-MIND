"""
API quản lý Đề thi và Chấm bài (Quizzes & Question Bank).
"""

import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher, get_current_user, get_db
from app.core.enums import UserRole
from app.core.security import create_essay_upload_token, decode_essay_upload_token
from app.database.mongodb import get_mongodb_db
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.quiz import QuizDetailResponse, QuizResponse, ClassroomQuizCreateRequest, QuizUpdateRequest
from app.schemas.quiz_attempt import QuizAttemptCreate, QuizAttemptResponse
from app.schemas.teacher import TeacherQuizCreate
from app.services.analytic_service import update_student_analytics_and_recommend
from app.services.quiz_service import (
    generate_and_save_quiz,
    generate_classroom_quiz_from_file,
    get_classroom_quiz_attempts,
    get_quiz,
    get_quiz_for_study_plan,
    get_quiz_review,
    get_student_assigned_quizzes_service,
    get_student_quiz_attempts,
    submit_student_quiz,
    teacher_create_quiz,
    update_quiz_by_teacher,
)
from app.services.quiz import generate_classroom_quiz
from app.repositories.classroom_repository import classroom_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.classroom_student_repository import classroom_student_repository
from app.models.classroom_student import ClassroomStudent
from app.models.quiz import Quiz
from app.infrastructure.uploader import validate_file_signature

router = APIRouter()

# Deduplicate self-healing background tasks cho AI assessment
_ai_assessment_healing: set[int] = set()


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
    except HTTPException:
        raise
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
    
    from app.repositories.plan_repository import plan_repository
    plan = plan_repository.get(db, study_plan_id)
    if not plan or plan.student_id != current_user.id:
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
            total_questions=10,
            study_plan_id=study_plan_id,
        )
        commit_or_rollback(db)
        return quiz
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể sinh đề thi AI lúc này.",
        ) from exc


@router.get(
    "/student/history",
    summary="Học sinh lấy danh sách toàn bộ các đề thi đã làm và điểm số",
)
def api_get_student_attempts_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_str.lower() != "student":
        return []
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
    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_str.lower() != "student":
        return []

    return get_student_assigned_quizzes_service(db=db, student_id=current_user.id)


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


@router.put(
    "/{quiz_id}",
    response_model=QuizDetailResponse,
    summary="Giáo viên cập nhật đề thi (tiêu đề, độ khó, hạn chót, danh sách câu hỏi)",
)
def api_update_quiz(
    quiz_id: int,
    body: QuizUpdateRequest,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    try:
        return update_quiz_by_teacher(
            db=db,
            quiz_id=quiz_id,
            teacher_id=current_teacher.id,
            update_data=body,
            current_user_role=current_teacher.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc



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
            time_limit_minutes=body.time_limit_minutes,
            max_tab_violations=body.max_tab_violations,
            document_id=body.document_id,
            document_ids=body.document_ids,
            custom_prompt=body.custom_prompt,
            include_essay=body.include_essay,
            essay_count=body.essay_count,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể sinh đề thi lúc này.",
        )


@router.post(
    "/classrooms/{classroom_id}/generate-from-file",
    response_model=QuizDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Giáo viên sinh đề thi tự động từ nhiều file tải lên (PDF/Word/TXT) bằng AI RAG",
)
async def generate_classroom_quiz_from_file_api(
    classroom_id: int,
    files: Optional[List[UploadFile]] = File(default=None),
    file: Optional[UploadFile] = File(default=None),
    subject_id: int = Form(...),
    topic: Optional[str] = Form(default=None),
    difficulty: str = Form(default="medium"),
    total_questions: int = Form(default=5),
    deadline: Optional[datetime] = Form(default=None),
    time_limit_minutes: Optional[int] = Form(default=30),
    max_tab_violations: Optional[int] = Form(default=3),
    custom_prompt: Optional[str] = Form(default=None),
    include_essay: bool = Form(default=False),
    essay_count: int = Form(default=0),
    db: Session = Depends(get_db),
    current_teacher: User = Depends(get_current_teacher),
):
    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")
    if classroom.teacher_id != current_teacher.id and current_teacher.role != "admin":
        raise HTTPException(status_code=403, detail="Bạn không phải là giáo viên của lớp học này.")

    upload_files = files or ([file] if file else [])
    if not upload_files:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên ít nhất 1 tệp tài liệu (PDF, Word, TXT).")

    try:
        from app.services.quiz.generation import generate_classroom_quiz_from_files

        file_tuples = []
        total_upload_bytes = 0
        for f in upload_files:
            filename = f.filename or "tai_lieu.pdf"
            ext = os.path.splitext(filename)[1].lower()
            if ext not in {".pdf", ".doc", ".docx", ".txt"}:
                raise HTTPException(status_code=400, detail="Định dạng tài liệu không được hỗ trợ.")
            content = await f.read(20 * 1024 * 1024 + 1)
            if len(content) > 20 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="Mỗi tài liệu không được vượt quá 20 MB.")
            total_upload_bytes += len(content)
            if total_upload_bytes > 50 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="Tổng dung lượng tài liệu vượt quá 50 MB.")
            if not validate_file_signature(content, ext):
                raise HTTPException(status_code=400, detail="Nội dung tệp không khớp định dạng khai báo.")
            file_tuples.append((content, filename))

        return await generate_classroom_quiz_from_files(
            db=db,
            subject_id=subject_id,
            classroom_id=classroom_id,
            files=file_tuples,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
            deadline=deadline,
            time_limit_minutes=time_limit_minutes,
            max_tab_violations=max_tab_violations,
            custom_prompt=custom_prompt,
            include_essay=include_essay,
            essay_count=essay_count,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể sinh đề thi từ tệp lúc này.",
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
MAX_ESSAY_UPLOAD_BYTES = 20 * 1024 * 1024


@router.post(
    "/upload-essay",
    summary="Tải lên tệp bài làm tự luận của học sinh (hình ảnh, PDF, Word, TXT)",
)
async def upload_essay_file(
    file: UploadFile = File(...),
    quiz_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Chỉ học sinh mới có thể tải bài tự luận.")
    quiz_obj = quiz_repository.get(db, quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")
    from app.services.quiz.queries import authorize_student_quiz_access
    try:
        authorize_student_quiz_access(db, quiz_obj, current_user.id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng tệp không được hỗ trợ. Vui lòng chọn file ảnh, PDF, Word hoặc TXT.",
        )

    upload_root = (Path.cwd() / UPLOAD_DIR).resolve()
    upload_root.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_root / filename

    try:
        content = await file.read(MAX_ESSAY_UPLOAD_BYTES + 1)
        if len(content) > MAX_ESSAY_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Tệp tự luận vượt quá giới hạn 20 MB.",
            )
        if not validate_file_signature(content, ext):
            raise HTTPException(status_code=400, detail="Nội dung tệp không khớp định dạng khai báo.")
        with file_path.open("wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lưu tệp tin.",
        ) from exc

    # Preserve the response field name for frontend compatibility, but return
    # an opaque signed reference rather than a filesystem path.
    return {
        "file_path": create_essay_upload_token(
            user_id=current_user.id,
            quiz_id=quiz_id,
            storage_name=filename,
        )
    }


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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        quiz = get_quiz_review(db, quiz_id, current_user)

        # Self-healing: nếu ai_assessment bị null do background task lỗi trước đó,
        # tự động kích hoạt lại background task (chỉ 1 lần duy nhất mỗi attempt)
        if (
            current_user.role == UserRole.STUDENT
            and hasattr(quiz, "latest_attempt")
            and quiz.latest_attempt
            and quiz.latest_attempt.ai_assessment is None
            and quiz.latest_attempt.id not in _ai_assessment_healing
        ):
            attempt = quiz.latest_attempt
            _ai_assessment_healing.add(attempt.id)
            from app.workers.tasks import task_generate_attempt_assessment
            task_generate_attempt_assessment.delay(attempt.id)

        return quiz
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

    quiz_obj = quiz_repository.get(db, quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")

    from app.services.quiz.queries import authorize_student_quiz_access
    try:
        authorize_student_quiz_access(db, quiz_obj, current_user.id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    if quiz_obj and quiz_obj.deadline:
        now = datetime.now(timezone.utc)
        dl = quiz_obj.deadline if quiz_obj.deadline.tzinfo else quiz_obj.deadline.replace(tzinfo=timezone.utc)
        if now > dl:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Đề thi đã quá hạn chót nộp bài. Bạn không thể nộp bài làm nữa.",
            )

    try:
        essay_file_path = None
        if body.essay_file_path:
            storage_name = decode_essay_upload_token(
                body.essay_file_path,
                user_id=current_user.id,
                quiz_id=quiz_id,
            )
            if not storage_name:
                raise HTTPException(status_code=400, detail="Mã tệp tự luận không hợp lệ hoặc đã hết hạn.")
            upload_root = (Path.cwd() / UPLOAD_DIR).resolve()
            candidate = (upload_root / storage_name).resolve()
            try:
                candidate.relative_to(upload_root)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Mã tệp tự luận không hợp lệ.") from exc
            if not candidate.is_file():
                raise HTTPException(status_code=400, detail="Không tìm thấy tệp tự luận đã tải lên.")
            essay_file_path = str(candidate)

        attempt, subject_id, quiz_title, questions_list, answers_json = submit_student_quiz(
            db=db,
            quiz_id=quiz_id,
            student_id=current_user.id,
            submitted_answers=body.answers,
            duration_seconds=body.duration_seconds,
            essay_file_path=essay_file_path,
            tab_violations_count=body.tab_violations_count,
        )

        # Xóa cache dashboard của học sinh ngay lập tức để đồng bộ điểm số mới
        try:
            get_redis().delete(f"dashboard_snapshot:{current_user.id}")
        except Exception:
            pass
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xử lý chấm điểm bài thi.",
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
    quiz_obj = quiz_repository.get(db, quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đề thi.")

    if quiz_obj.deadline and current_user.role == UserRole.STUDENT:
        now = datetime.now(timezone.utc)
        dl = quiz_obj.deadline if quiz_obj.deadline.tzinfo else quiz_obj.deadline.replace(tzinfo=timezone.utc)
        if now > dl:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Đề thi đã quá hạn chót nộp bài. Bạn không thể làm đề thi này nữa.",
            )

    if current_user.role == UserRole.STUDENT:
        from app.services.quiz.queries import authorize_student_quiz_access
        try:
            authorize_student_quiz_access(db, quiz_obj, current_user.id)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    try:
        return get_quiz(db, quiz_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
