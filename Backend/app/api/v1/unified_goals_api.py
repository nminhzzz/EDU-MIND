from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_student, rate_limiter
from app.models.user import User
from app.models.subject import Subject
from app.schemas.study_goal import StudyGoalDraftCreate, StudyGoalConfirm
from app.services.unified_service import (
    generate_unified_draft,
    confirm_unified_draft,
    generate_materials_and_quizzes_for_plans_bg,
)

router = APIRouter()


@router.post(
    "/unified/draft",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limiter(limit=5, period_seconds=600))],
    summary="Tạo bản nháp hoặc thảo luận tinh chỉnh lộ trình học tập hợp nhất (Phase 1 + 2 + 3)",
    description="Nhập mục tiêu + deadline + lịch rảnh, sinh trọn gói: Lộ trình tuần, Lịch ngày, Giáo trình RAG và Quizzes.",
)
async def create_or_update_unified_draft(
    body: StudyGoalDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    # Kiểm tra môn học tồn tại
    subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID={body.subject_id}.",
        )

    # --- XÁC THỰC MỤC TIÊU & HẠN CHÓT BẤT KHẢ THI (TC-01) ---
    from datetime import date

    today = date.today()
    if body.deadline < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hạn chót không được nằm trong quá khứ.",
        )

    days_left = (body.deadline - today).days
    if days_left < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Hạn chót quá ngắn! Lộ trình học tập cho môn '{subject.name}' cần tối thiểu 3 ngày rảnh. "
                "Vui lòng lùi ngày hạn chót xa hơn để đảm bảo việc tiếp thu kiến thức hiệu quả."
            ),
        )

    if body.target_score >= 8.0 and days_left < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Mục tiêu điểm số quá cao ({body.target_score}/10) cho một khoảng thời gian học quá ngắn ({days_left} ngày). "
                "Vui lòng lùi ngày hạn chót xa hơn (tối thiểu 5 ngày) hoặc giảm điểm mục tiêu xuống để lộ trình khả thi hơn."
            ),
        )
    # --------------------------------------------------------

    try:
        result = await generate_unified_draft(
            student=current_user,
            subject_obj=subject,
            target_score=body.target_score,
            deadline=body.deadline,
            user_message=body.user_message,
            session_id=body.session_id,
        )
        return {
            "message": "Sinh lộ trình nháp hợp nhất thành công!",
            "session_id": result["session_id"],
            "plan": result["plan"],
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý lộ trình hợp nhất nháp: {str(e)}",
        )


@router.post(
    "/unified/confirm",
    status_code=status.HTTP_201_CREATED,
    summary="Xác nhận lưu chính thức lộ trình nháp hợp nhất vào MySQL",
    description="Đọc cache Redis hoặc Mongo của session_id, ghi MySQL đồng thời (StudyGoal, StudyPlans, Quiz, QuestionBank).",
)
async def confirm_unified(
    body: StudyGoalConfirm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    from app.database.redis import get_redis_client

    redis_client = get_redis_client()
    lock_key = f"lock:confirm:{body.session_id}"

    if not redis_client.set(lock_key, "locked", nx=True, ex=10):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yêu cầu xác nhận lộ trình đang được xử lý. Vui lòng không nhấn liên tục.",
        )

    lock_acquired = True
    try:
        # Kiểm tra môn học tồn tại
        subject = db.query(Subject).filter(Subject.id == body.subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy môn học với ID={body.subject_id}.",
            )

        result = await confirm_unified_draft(
            db=db,
            student=current_user,
            subject_obj=subject,
            session_id=body.session_id,
            target_score=body.target_score,
            deadline=body.deadline,
        )

        goal = result["goal"]

        # Kích hoạt sinh tài liệu và đề thi ngầm cho từng ngày học
        background_tasks.add_task(
            generate_materials_and_quizzes_for_plans_bg,
            goal.id,
            current_user.id,
            subject.id,
        )
        return {
            "message": "Xác nhận và lưu lộ trình hợp nhất chính thức thành công!",
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "subject_id": goal.subject_id,
                "target_score": float(goal.target_score),
                "deadline": str(goal.deadline),
                "status": goal.status,
                "created_at": str(goal.created_at),
            },
            "total_plans": result["total_plans"],
            "total_quizzes": result["total_quizzes"],
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xác nhận và lưu lộ trình học tập hợp nhất: {str(e)}",
        )
    finally:
        if lock_acquired:
            try:
                redis_client.delete(lock_key)
            except Exception as le:
                print(f"[Warning] Failed to release Redis lock {lock_key}: {le}")
