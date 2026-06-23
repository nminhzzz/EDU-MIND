from sqlalchemy.orm import Session
from datetime import date, time, timedelta, datetime
from typing import Optional, Dict, Any
import json

from app.database.redis import redis_client
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.agents.goal_planner.agent import generate_goal_plan
from app.agents.goal_planner.schemas import GoalPlannerResponse
from app.repositories.chat_repository import (
    create_chat_session,
    get_chat_messages,
    add_chat_message,
    get_last_assistant_message
)


def create_goal_and_schedule_plans(
    db: Session,
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    available_schedule: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Tạo mục tiêu học tập (StudyGoal) và lập lộ trình học tuần (StudyPlan) lưu vào MySQL.

    Args:
        db: SQLAlchemy session
        student: User object của học sinh
        subject_obj: Subject object của môn học
        target_score: Điểm mục tiêu (thang 10)
        deadline: Hạn chót đạt mục tiêu
        available_schedule: Lịch rảnh học sinh {"mon": true, "tue": false, ...}
    """
    ai_plan = generate_goal_plan(
        subject=subject_obj.name,
        target_score=target_score,
        deadline=deadline,
        student_id=student.id,
        subject_id=subject_obj.id,
        available_schedule=available_schedule
    )

    # ── 2. Lưu vào bảng study_goals ───────────────────────────
    goal_title = f"Đạt {target_score} điểm {subject_obj.name}"
    if len(goal_title) > 255:
        goal_title = goal_title[:251] + "..."

    db_goal = StudyGoal(
        student_id=student.id,
        subject_id=subject_obj.id,
        title=goal_title,
        target_score=target_score,
        deadline=deadline,
        status="active"
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    # ── 3. Lấy lịch rảnh từ StudentPreference nếu không được truyền vào ──
    if not available_schedule:
        from app.models.student_preference import StudentPreference
        pref = db.query(StudentPreference).filter(StudentPreference.student_id == student.id).first()
        if pref and pref.available_schedule:
            available_schedule = pref.available_schedule
        else:
            # Mặc định học Thứ 2 đến Thứ 6 nếu không cấu hình preference
            available_schedule = {
                "mon": True, "tue": True, "wed": True, "thu": True, "fri": True,
                "sat": False, "sun": False
            }

    WEEKDAY_MAP = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}

    def is_study_day(d: date) -> bool:
        if not available_schedule:
            return True
        day_key = WEEKDAY_MAP.get(d.weekday(), "")
        return bool(available_schedule.get(day_key, True))

    # ── 4. Thu thập toàn bộ ngày học hợp lệ từ hôm nay đến deadline ──
    today = date.today()
    if deadline < today:
        deadline = today

    all_study_days = []
    created_tasks = []
    temp_date = today
    while temp_date <= deadline:
        if is_study_day(temp_date):
            all_study_days.append(temp_date)
        temp_date += timedelta(days=1)

    # Nếu không có ngày học hợp lệ nào, sử dụng tất cả các ngày từ hôm nay đến deadline làm dự phòng
    if not all_study_days:
        temp_date = today
        while temp_date <= deadline:
            all_study_days.append(temp_date)
            temp_date += timedelta(days=1)

    # ── 5. Thu thập toàn bộ nhiệm vụ từ các tuần của AI thành danh sách phẳng ──
    all_tasks = []
    for week_plan in ai_plan.weeks:
        week_num = week_plan.week
        for task in week_plan.tasks:
            all_tasks.append((week_num, task))

    num_tasks = len(all_tasks)
    num_days = len(all_study_days)

    # ── 6. Phân bổ đều các nhiệm vụ lên các ngày học và lưu vào study_plans ──
    for idx, (week_num, task) in enumerate(all_tasks):
        if num_tasks <= num_days:
            # Nếu đủ ngày, xếp mỗi ngày 1 task từ ngày đầu tiên
            assigned_date = all_study_days[idx]
        else:
            # Nếu thiếu ngày, phân bổ đều nhiều task vào các ngày học
            day_idx = int(idx * num_days / num_tasks)
            day_idx = min(day_idx, num_days - 1)
            assigned_date = all_study_days[day_idx]

        plan_title = f"Tuần {week_num} - {task}"
        if len(plan_title) > 255:
            plan_title = plan_title[:251] + "..."

        db_plan = StudyPlan(
            student_id=student.id,
            goal_id=db_goal.id,
            title=plan_title,
            task_description=f"Nhiệm vụ tuần {week_num} của môn {subject_obj.name}",
            study_date=assigned_date,
            start_time=time(19, 0, 0),
            end_time=time(21, 0, 0),
            ai_generated=True,
            status="todo"
        )
        db.add(db_plan)
        created_tasks.append(db_plan)

    db.commit()

    return {
        "goal": db_goal,
        "plans": created_tasks,
        "total_weeks": len(ai_plan.weeks),
        "total_plans": len(created_tasks)
    }


def _calculate_and_cache_plans(
    student_id: int,
    subject_id: int,
    target_score: float,
    deadline: date,
    session_id: str,
    ai_plan: GoalPlannerResponse,
    available_schedule: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> None:
    """
    Tính toán phân bổ các task lên các ngày rảnh của học sinh
    và lưu toàn bộ dữ liệu lộ trình chi tiết vào Redis Cache (TTL = 30 phút).
    """
    # 1. Lấy lịch rảnh từ StudentPreference nếu không có sẵn
    if not available_schedule and db:
        from app.models.student_preference import StudentPreference
        pref = db.query(StudentPreference).filter(StudentPreference.student_id == student_id).first()
        if pref and pref.available_schedule:
            available_schedule = pref.available_schedule
            
    if not available_schedule:
        available_schedule = {
            "mon": True, "tue": True, "wed": True, "thu": True, "fri": True,
            "sat": False, "sun": False
        }

    WEEKDAY_MAP = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}

    def is_study_day(d: date) -> bool:
        day_key = WEEKDAY_MAP.get(d.weekday(), "")
        return bool(available_schedule.get(day_key, True))

    # 2. Thu thập ngày học hợp lệ
    today = date.today()
    temp_deadline = deadline
    if temp_deadline < today:
        temp_deadline = today

    all_study_days = []
    temp_date = today
    while temp_date <= temp_deadline:
        if is_study_day(temp_date):
            all_study_days.append(temp_date)
        temp_date += timedelta(days=1)

    if not all_study_days:
        temp_date = today
        while temp_date <= temp_deadline:
            all_study_days.append(temp_date)
            temp_date += timedelta(days=1)

    # 3. Phân bổ các nhiệm vụ
    all_tasks = []
    for week_plan in ai_plan.weeks:
        week_num = week_plan.week
        for task in week_plan.tasks:
            all_tasks.append((week_num, task))

    num_tasks = len(all_tasks)
    num_days = len(all_study_days)

    plans_data = []
    for idx, (week_num, task) in enumerate(all_tasks):
        if num_tasks <= num_days:
            assigned_date = all_study_days[idx]
        else:
            day_idx = int(idx * num_days / num_tasks)
            day_idx = min(day_idx, num_days - 1)
            assigned_date = all_study_days[day_idx]

        plans_data.append({
            "title": f"Tuần {week_num} - {task}",
            "task_description": f"Nhiệm vụ tuần {week_num} của môn",
            "study_date": assigned_date.strftime("%Y-%m-%d"),
            "start_time": "19:00:00",
            "end_time": "21:00:00",
            "ai_generated": True,
            "status": "todo"
        })

    # 4. Gom dữ liệu cache
    draft_data = {
        "student_id": student_id,
        "subject_id": subject_id,
        "target_score": target_score,
        "deadline": deadline.strftime("%Y-%m-%d"),
        "plans": plans_data,
        "total_weeks": len(ai_plan.weeks)
    }

    # 5. Lưu vào Redis Cache (TTL = 30 phút = 1800 giây)
    cache_key = f"goal_draft:{session_id}"
    redis_client.setex(
        name=cache_key,
        time=1800,
        value=json.dumps(draft_data, ensure_ascii=False)
    )
    print(f"-> Cached goal draft in Redis for session {session_id} (TTL: 1800s)")


async def generate_goal_plan_draft(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    user_message: Optional[str] = None,
    session_id: Optional[str] = None,
    available_schedule: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> dict:
    """
    Sinh lộ trình học tập nháp và hỗ trợ thảo luận tinh chỉnh lộ trình qua MongoDB + Redis Cache.
    """
    if not session_id:
        # --- Lượt đầu: Tạo phiên chat mới trong MongoDB ---
        session_id = await create_chat_session(
            student_id=student.id,
            title=f"Lộ trình nháp môn {subject_obj.name}"
        )
        
        # Gọi Agent lập lộ trình lần đầu
        ai_plan = generate_goal_plan(
            subject=subject_obj.name,
            target_score=target_score,
            deadline=deadline,
            student_id=student.id,
            subject_id=subject_obj.id,
            available_schedule=available_schedule
        )
        
        # Lưu cuộc hội thoại vào MongoDB
        user_prompt = f"Hãy lập lộ trình học tập đạt mục tiêu {target_score}/10 cho môn học '{subject_obj.name}'."
        await add_chat_message(session_id, "user", user_prompt)
        await add_chat_message(session_id, "assistant", json.dumps(ai_plan.model_dump(), ensure_ascii=False))
    else:
        # --- Lượt sau: Học sinh thảo luận tinh chỉnh lộ trình ---
        if not user_message:
            raise ValueError("user_message là bắt buộc khi thực hiện tinh chỉnh lộ trình.")
            
        # Lấy lịch sử chat cũ từ MongoDB
        history = await get_chat_messages(session_id)
        
        # Lưu tin nhắn mới của học sinh
        await add_chat_message(session_id, "user", user_message)
        
        # Thêm tin nhắn mới vào history gửi cho AI
        history.append({"role": "user", "content": user_message})
        
        # Gọi Agent với lịch sử hội thoại để tinh chỉnh
        ai_plan = generate_goal_plan(
            subject=subject_obj.name,
            target_score=target_score,
            deadline=deadline,
            student_id=student.id,
            subject_id=subject_obj.id,
            available_schedule=available_schedule,
            history=history
        )
        
        # Lưu phản hồi lộ trình đã được tinh chỉnh của AI vào MongoDB
        await add_chat_message(session_id, "assistant", json.dumps(ai_plan.model_dump(), ensure_ascii=False))
        
    # Tính toán lại phân bổ ngày và ghi đè vào Redis Cache
    _calculate_and_cache_plans(
        student_id=student.id,
        subject_id=subject_obj.id,
        target_score=target_score,
        deadline=deadline,
        session_id=session_id,
        ai_plan=ai_plan,
        available_schedule=available_schedule,
        db=db
    )
        
    return {
        "session_id": session_id,
        "plan": ai_plan
    }


async def confirm_goal_plan_draft(
    db: Session,
    student: User,
    subject_obj: Subject,
    session_id: str,
    target_score: float,
    deadline: date,
    available_schedule: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Xác nhận lộ trình học nháp cuối cùng từ MongoDB và lưu chính thức vào MySQL study_goals & study_plans.
    Hỗ trợ đọc nhanh từ Redis Cache, tự động Fallback đọc từ MongoDB nếu cache hết hạn.
    """
    cache_key = f"goal_draft:{session_id}"
    cached_data_str = redis_client.get(cache_key)
    
    if cached_data_str:
        print(f"-> Redis Cache HIT for key {cache_key}. Loading draft directly from Redis.")
        try:
            draft_data = json.loads(cached_data_str)
            
            # 2.1 Lưu vào bảng study_goals (MySQL)
            goal_title = f"Đạt {draft_data['target_score']} điểm {subject_obj.name}"
            if len(goal_title) > 255:
                goal_title = goal_title[:251] + "..."

            db_goal = StudyGoal(
                student_id=student.id,
                subject_id=draft_data["subject_id"],
                title=goal_title,
                target_score=draft_data["target_score"],
                deadline=datetime.strptime(draft_data["deadline"], "%Y-%m-%d").date(),
                status="active"
            )
            db.add(db_goal)
            db.commit()
            db.refresh(db_goal)

            # 2.2 Lưu vào bảng study_plans (MySQL)
            created_tasks = []
            for p in draft_data["plans"]:
                db_plan = StudyPlan(
                    student_id=student.id,
                    goal_id=db_goal.id,
                    title=p["title"],
                    task_description=f"Nhiệm vụ tuần của môn {subject_obj.name}",
                    study_date=datetime.strptime(p["study_date"], "%Y-%m-%d").date(),
                    start_time=time(19, 0, 0),
                    end_time=time(21, 0, 0),
                    ai_generated=p["ai_generated"],
                    status=p["status"]
                )
                db.add(db_plan)
                created_tasks.append(db_plan)

            db.commit()
            
            # Xóa cache Redis
            redis_client.delete(cache_key)
            print(f"-> Deleted cache key {cache_key} after successful confirmation.")

            return {
                "goal": db_goal,
                "plans": created_tasks,
                "total_weeks": draft_data["total_weeks"],
                "total_plans": len(created_tasks)
            }
        except Exception as e:
            print(f"WARNING: Lỗi khi xử lý dữ liệu Redis Cache: {e}. Fallback sang MongoDB.")
            # Tiếp tục chạy xuống logic Fallback MongoDB bên dưới
            
    # --- FALLBACK LAYER: Đọc từ MongoDB ---
    print(f"-> Redis Cache MISS or expired for key {cache_key}. Fallback to MongoDB.")
    
    # 1. Lấy phản hồi lộ trình nháp cuối cùng của AI từ MongoDB
    last_msg = await get_last_assistant_message(session_id)
    if not last_msg:
        raise ValueError("Không tìm thấy lộ trình nháp nào trong phiên chat này. Vui lòng tạo bản nháp trước.")
        
    # Parse lộ trình JSON
    try:
        data = json.loads(last_msg)
        ai_plan = GoalPlannerResponse(**data)
    except Exception as e:
        raise ValueError(f"Không thể phân tích dữ liệu lộ trình nháp từ MongoDB: {e}")
        
    # 2. Lưu vào bảng study_goals (MySQL)
    goal_title = f"Đạt {target_score} điểm {subject_obj.name}"
    if len(goal_title) > 255:
        goal_title = goal_title[:251] + "..."

    db_goal = StudyGoal(
        student_id=student.id,
        subject_id=subject_obj.id,
        title=goal_title,
        target_score=target_score,
        deadline=deadline,
        status="active"
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    # 3. Lấy lịch rảnh từ StudentPreference nếu không có sẵn
    if not available_schedule:
        from app.models.student_preference import StudentPreference
        pref = db.query(StudentPreference).filter(StudentPreference.student_id == student.id).first()
        if pref and pref.available_schedule:
            available_schedule = pref.available_schedule
        else:
            available_schedule = {
                "mon": True, "tue": True, "wed": True, "thu": True, "fri": True,
                "sat": False, "sun": False
            }

    WEEKDAY_MAP = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}

    def is_study_day(d: date) -> bool:
        if not available_schedule:
            return True
        day_key = WEEKDAY_MAP.get(d.weekday(), "")
        return bool(available_schedule.get(day_key, True))

    # 4. Thu thập toàn bộ ngày học hợp lệ
    today = date.today()
    if deadline < today:
        deadline = today

    all_study_days = []
    created_tasks = []
    temp_date = today
    while temp_date <= deadline:
        if is_study_day(temp_date):
            all_study_days.append(temp_date)
        temp_date += timedelta(days=1)

    if not all_study_days:
        temp_date = today
        while temp_date <= deadline:
            all_study_days.append(temp_date)
            temp_date += timedelta(days=1)

    # 5. Phân bổ các nhiệm vụ đã chốt từ AI và lưu vào MySQL
    all_tasks = []
    for week_plan in ai_plan.weeks:
        week_num = week_plan.week
        for task in week_plan.tasks:
            all_tasks.append((week_num, task))

    num_tasks = len(all_tasks)
    num_days = len(all_study_days)

    for idx, (week_num, task) in enumerate(all_tasks):
        if num_tasks <= num_days:
            assigned_date = all_study_days[idx]
        else:
            day_idx = int(idx * num_days / num_tasks)
            day_idx = min(day_idx, num_days - 1)
            assigned_date = all_study_days[day_idx]

        plan_title = f"Tuần {week_num} - {task}"
        if len(plan_title) > 255:
            plan_title = plan_title[:251] + "..."

        db_plan = StudyPlan(
            student_id=student.id,
            goal_id=db_goal.id,
            title=plan_title,
            task_description=f"Nhiệm vụ tuần {week_num} của môn {subject_obj.name}",
            study_date=assigned_date,
            start_time=time(19, 0, 0),
            end_time=time(21, 0, 0),
            ai_generated=True,
            status="todo"
        )
        db.add(db_plan)
        created_tasks.append(db_plan)

    db.commit()

    return {
        "goal": db_goal,
        "plans": created_tasks,
        "total_weeks": len(ai_plan.weeks),
        "total_plans": len(created_tasks)
    }
