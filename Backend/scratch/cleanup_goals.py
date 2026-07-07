from app.database.mysql import SessionLocal
from app.models.study_goal import StudyGoal
from app.models.user import User


def cleanup():
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    if not student:
        print("Student not found")
        return
    print(f"Cleaning up data for Student ID: {student.id}")

    # Lấy tất cả active goals của môn Triết học Mác - Lênin (Subject ID: 1)
    goals = (
        db.query(StudyGoal)
        .filter(
            StudyGoal.student_id == student.id,
            StudyGoal.subject_id == 1,
            StudyGoal.status == "active",
        )
        .order_by(StudyGoal.created_at.desc())
        .all()
    )

    if len(goals) > 1:
        print(
            f"Found {len(goals)} active roadmaps. Keeping the latest one (ID: {goals[0].id}) and cancelling others."
        )
        for g in goals[1:]:
            g.status = "cancelled"
            print(f"Cancelled StudyGoal ID: {g.id}")
        db.commit()
        print("Cleanup completed successfully!")
    else:
        print("No cleanup needed (1 or fewer active roadmaps).")
    db.close()


if __name__ == "__main__":
    cleanup()
