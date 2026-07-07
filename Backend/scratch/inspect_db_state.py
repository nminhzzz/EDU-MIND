from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from datetime import date

db = SessionLocal()
try:
    print("--- STUDY PLANS FOR TODAY ---")
    plans = db.query(StudyPlan).filter(StudyPlan.study_date == date.today()).all()
    for p in plans:
        print(f"Plan ID: {p.id}, Title: {p.title}, Status: {p.status}")

    print("\n--- QUIZZES ---")
    quizzes = db.query(Quiz).all()
    for q in quizzes:
        print(f"Quiz ID: {q.id}, Title: {q.title}, Study Plan ID: {q.study_plan_id}")

    print("\n--- QUIZ ATTEMPTS ---")
    attempts = db.query(QuizAttempt).order_by(QuizAttempt.submitted_at.desc()).all()
    for a in attempts:
        print(
            f"Attempt ID: {a.id}, Quiz ID: {a.quiz_id}, Score: {a.score}, Correct: {a.correct_count}, Wrong: {a.wrong_count}, Submitted: {a.submitted_at}"
        )
finally:
    db.close()
