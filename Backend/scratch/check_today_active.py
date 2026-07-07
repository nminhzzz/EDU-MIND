from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.study_goal import StudyGoal
from app.models.user import User
from datetime import date


def check():
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    today = date(2026, 7, 1)  # Ngày hôm nay trong DB

    plans = (
        db.query(StudyPlan)
        .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
        .filter(
            StudyPlan.student_id == student.id,
            StudyPlan.study_date == today,
            StudyGoal.status == "active",
        )
        .all()
    )
    print(f"Active today plans count: {len(plans)}")
    for p in plans:
        print(
            f"Plan ID: {p.id}, Title: {p.title}, Goal ID: {p.goal_id}, Status: {p.status}"
        )
    db.close()


if __name__ == "__main__":
    check()
