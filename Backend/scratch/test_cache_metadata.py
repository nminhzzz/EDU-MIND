import sys, os, asyncio, json
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                key_clean = key.strip()
                val_clean = val.strip()
                if key_clean not in os.environ or not os.environ[key_clean].strip():
                    os.environ[key_clean] = val_clean

from app.database.redis import get_redis_client
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

student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
db.close()
print(f"3. Student={student.id}, Subject={subject.id}")

from app.services.unified_service import generate_unified_draft


async def test():
    print("4. Calling generate_unified_draft...")
    result = await generate_unified_draft(
        student=student,
        subject_obj=subject,
        target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        user_message="test",
        session_id=None,
    )
    sid = result["session_id"]
    print(f"5. Done! Session={sid}")
    print(
        f"   Weeks={len(result['plan'].weeks)} Daily={len(result['plan'].daily_schedule)}"
    )
    print(f"   Quizzes={len(result['plan'].quizzes)}")

    cached = redis_client.get(f"unified_draft:{sid}")
    data = json.loads(cached)
    print(f"6. Redis has _subject_id: {'_subject_id' in data}")
    print(f"   _target_score={data.get('_target_score')}")
    print("ALL OK")


asyncio.run(test())
