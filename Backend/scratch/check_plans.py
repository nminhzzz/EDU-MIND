from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.user import User


def check():
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    if not student:
        print("Student not found")
        return
    print(f"Student ID: {student.id}")

    plans = db.query(StudyPlan).filter(StudyPlan.student_id == student.id).all()
    print(f"Total plans for student: {len(plans)}")
    for p in plans:
        print(
            f"ID: {p.id}, Date: {p.study_date}, Title: {p.title}, AI Generated: {p.ai_generated}, Status: {p.status}"
        )
    db.close()


if __name__ == "__main__":
    check()
