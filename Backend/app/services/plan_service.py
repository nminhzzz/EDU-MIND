"""
Giai đoạn 2 — Fix plan_service.py:
  + Thêm joinedload để tránh lazy load crash
  + Xóa biến thừa `created_tasks_tmp`
  + Đổi thiết kế: nhận danh sách tasks trực tiếp thay vì parse từ DB title
"""
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date, time

from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.agents.daily_planner.agent import generate_daily_plan


def generate_and_save_daily_plans(
    db: Session,
    goal_id: int,
    study_hours_per_day: float = None,
    preferred_time: str = None,
    off_days: list = None
) -> list:
    """
    Lấy lộ trình tuần của Phase 1 từ Database, gọi Daily Planner Agent
    sinh lịch học chi tiết theo ngày, xoá placeholder cũ và lưu mới vào MySQL.

    Args:
        db: SQLAlchemy Session
        goal_id: ID của StudyGoal cần lập lịch
        study_hours_per_day: Số giờ học mỗi ngày (tùy chọn)
        preferred_time: Khung giờ học ưa thích (tùy chọn, vd: "18:00-20:00")
        off_days: Danh sách ngày nghỉ (tùy chọn, vd: ["Thứ 7", "Chủ nhật"])
    """
    # 1. Query StudyGoal kèm eager load subject để tránh lazy load crash
    goal = (
        db.query(StudyGoal)
        .options(joinedload(StudyGoal.subject))
        .filter(StudyGoal.id == goal_id)
        .first()
    )
    if not goal:
        raise ValueError(f"Không tìm thấy mục tiêu học tập với ID: {goal_id}")

    # Lấy tùy chọn học tập của học sinh từ DB nếu thiếu tham số truyền vào
    from app.models.student_preference import StudentPreference
    pref = db.query(StudentPreference).filter(StudentPreference.student_id == goal.student_id).first()

    if study_hours_per_day is None:
        study_hours_per_day = float(pref.study_hours_per_day) if pref and pref.study_hours_per_day else 2.0

    if not preferred_time:
        pref_time_str = pref.preferred_study_time if pref and pref.preferred_study_time else "evening"
        mapping = {
            "morning": "08:00-10:00",
            "afternoon": "14:00-16:00",
            "evening": "18:00-20:00",
            "night": "21:00-23:00"
        }
        preferred_time = mapping.get(pref_time_str, "18:00-20:00")

    if off_days is None:
        off_days = []
        if pref and pref.available_schedule:
            day_mapping = {
                "mon": "Thứ 2",
                "tue": "Thứ 3",
                "wed": "Thứ 4",
                "thu": "Thứ 5",
                "fri": "Thứ 6",
                "sat": "Thứ 7",
                "sun": "Chủ nhật"
            }
            # available_schedule có thể ở dạng JSON dict
            for day_key, is_available in pref.available_schedule.items():
                if not is_available and day_key in day_mapping:
                    off_days.append(day_mapping[day_key])

    # 2. Lấy danh sách study_plans placeholder của Phase 1
    old_plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.goal_id == goal_id)
        .order_by(StudyPlan.study_date.asc())
        .all()
    )
    if not old_plans:
        raise ValueError(f"Mục tiêu ID {goal_id} chưa có lộ trình tuần. Hãy chạy Phase 1 trước.")

    # 3. Trích xuất nhiệm vụ gốc (bỏ prefix "Tuần X - ")
    weekly_tasks_list = []
    for plan in old_plans:
        title = plan.title
        weekly_tasks_list.append(title.split(" - ", 1)[1] if " - " in title else title)

    # 4. Tính số ngày còn lại
    today = date.today()
    days_left = max((goal.deadline - today).days, 1)

    # 5. Gọi Daily Planner Agent sinh lịch ngày chi tiết
    ai_schedule = generate_daily_plan(
        subject=goal.subject.name,
        target_score=float(goal.target_score),
        days_left=days_left,
        weekly_plans_list=weekly_tasks_list,
        study_hours_per_day=study_hours_per_day,
        preferred_time=preferred_time,
        off_days=off_days,
        current_date=today.strftime("%Y-%m-%d")
    )

    # 6. Xóa toàn bộ placeholder stubs của Phase 1
    db.query(StudyPlan).filter(StudyPlan.goal_id == goal_id).delete()
    db.commit()

    # 7. Lưu lịch học chi tiết mới
    created_plans = []
    for item in ai_schedule.schedule:
        try:
            study_date = datetime.strptime(item.date, "%Y-%m-%d").date()
        except (ValueError, AttributeError):
            study_date = today

        try:
            sh, sm = map(int, item.start_time.split(":"))
            start_time = time(sh, sm, 0)
        except (ValueError, AttributeError):
            start_time = time(18, 0, 0)

        try:
            eh, em = map(int, item.end_time.split(":"))
            end_time = time(eh, em, 0)
        except (ValueError, AttributeError):
            end_time = time(20, 0, 0)

        plan_title = item.task[:255] if len(item.task) > 255 else item.task
        plan_desc = item.description if hasattr(item, "description") and item.description else f"Lịch học chi tiết hàng ngày — môn {goal.subject.name}"

        db_plan = StudyPlan(
            student_id=goal.student_id,
            goal_id=goal.id,
            title=plan_title,
            task_description=plan_desc,
            study_date=study_date,
            start_time=start_time,
            end_time=end_time,
            ai_generated=True,
            status="todo"
        )
        db.add(db_plan)
        created_plans.append(db_plan)

    db.commit()
    return created_plans
