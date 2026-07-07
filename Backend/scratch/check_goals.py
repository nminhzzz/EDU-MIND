from app.database.mysql import SessionLocal
from app.models.study_goal import StudyGoal
from app.models.user import User


def check():
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    if not student:
        print("Student not found")
        return
    print(f"Student ID: {student.id}")

    goals = db.query(StudyGoal).filter(StudyGoal.student_id == student.id).all()
    print(f"Total goals (roadmaps): {len(goals)}")
    for g in goals:
        print(
            f"ID: {g.id}, Subject ID: {g.subject_id}, Target Score: {g.target_score}, Status: {g.status}, Created At: {g.created_at}"
        )
    db.close()


if __name__ == "__main__":
    check()
