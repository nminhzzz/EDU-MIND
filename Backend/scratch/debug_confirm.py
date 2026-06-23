import sys, os, asyncio
from datetime import date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                key_clean = key.strip(); val_clean = val.strip()
                if key_clean not in os.environ or not os.environ[key_clean].strip():
                    os.environ[key_clean] = val_clean

from app.database.redis import get_redis_client
from app.database.mongodb import get_mongodb_db
from app.database.mysql import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
from app.models.student_preference import StudentPreference
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.question_bank import QuestionBank

redis_client = get_redis_client()
redis_client.ping()
print("1. Redis OK")

Base.metadata.create_all(bind=engine)
db = SessionLocal()
print("2. MySQL OK")

db_mongo = get_mongodb_db()
print("3. MongoDB OK")

student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
print(f"4. Student ID={student.id}, Subject ID={subject.id}")

print("5. Calling generate_unified_draft...")
from app.services.unified_service import generate_unified_draft, confirm_unified_draft

async def test():
    draft = await generate_unified_draft(
        student=student,
        subject_obj=subject,
        target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        user_message="Hay lap cho toi mot lo trinh hoc hieu qua.",
        session_id=None
    )
    session_id = draft["session_id"]
    print(f"6. Draft generated! Session: {session_id}")
    print(f"   Weeks: {len(draft['plan'].weeks)}")
    print(f"   Daily tasks: {len(draft['plan'].daily_schedule)}")
    print(f"   Materials: {len(draft['plan'].curriculum_materials)}")
    print(f"   Quizzes: {len(draft['plan'].quizzes)}")

    # Confirm
    print("7. Calling confirm_unified_draft...")
    confirm = await confirm_unified_draft(
        db=db,
        student=student,
        subject_obj=subject,
        session_id=session_id,
        target_score=8.0,
        deadline=date.today() + timedelta(days=14)
    )
    print(f"8. Confirm success! Goal ID={confirm['goal'].id}")
    print(f"   Plans created: {confirm['total_plans']}")
    print(f"   Quizzes created: {confirm['total_quizzes']}")

    # Verify MySQL
    goal = db.query(StudyGoal).filter(StudyGoal.id == confirm['goal'].id).first()
    assert goal is not None, "Goal not found in MySQL"
    print(f"9. MySQL StudyGoal: title='{goal.title}', status={goal.status}, score={goal.target_score}")

    plans_count = db.query(StudyPlan).filter(StudyPlan.goal_id == goal.id).count()
    assert plans_count == confirm['total_plans'], "Plan count mismatch"
    print(f"10. MySQL StudyPlans: {plans_count} plans")

    quiz = db.query(Quiz).filter(Quiz.subject_id == subject.id).order_by(Quiz.id.desc()).first()
    assert quiz is not None, "Quiz not found"
    print(f"11. MySQL Quiz: id={quiz.id}, title='{quiz.title}', classroom_id={quiz.classroom_id}")

    questions_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    assert questions_count > 0, "No questions in quiz"
    print(f"12. MySQL Questions: {questions_count} questions")

    # Verify Redis cache cleared
    cached = redis_client.get(f"unified_draft:{session_id}")
    assert cached is None, "Redis cache not cleared"
    print("13. Redis cache cleared successfully!")

    print("\n=== ALL TESTS PASSED ===")

asyncio.run(test())
