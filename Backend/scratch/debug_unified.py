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

redis_client = get_redis_client()
redis_client.ping()
print("1. Redis OK")

Base.metadata.create_all(bind=engine)
db = SessionLocal()
print("2. MySQL OK")

db_mongo = get_mongodb_db()
print("3. MongoDB OK")

student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
print(f"4. Student: {student is not None}, ID={student.id if student else None}")

subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
print(f"5. Subject: {subject is not None}, ID={subject.id if subject else None}")

pref = db.query(StudentPreference).filter(StudentPreference.student_id == student.id).first()
print(f"6. Pref: {pref is not None}")
db.close()

print("7. Calling generate_unified_draft...")
from app.services.unified_service import generate_unified_draft

async def test():
    draft = await generate_unified_draft(
        student=student,
        subject_obj=subject,
        target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        user_message="Hay lap cho toi mot lo trinh hoc hieu qua.",
        session_id=None
    )
    print(f"8. Done! Session: {draft['session_id']}")
    print(f"   Weeks: {len(draft['plan'].weeks)}")
    print(f"   Daily tasks: {len(draft['plan'].daily_schedule)}")
    print(f"   Materials: {len(draft['plan'].curriculum_materials)}")
    print(f"   Quizzes: {len(draft['plan'].quizzes)}")

asyncio.run(test())
