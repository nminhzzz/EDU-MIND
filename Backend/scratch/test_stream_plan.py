import sys, os, asyncio
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
student = db.query(User).filter(User.email == "student@test.com").first()
subject = db.query(Subject).filter(Subject.code == "TRIETHOC").first()
db.close()
print(
    f"2. Student={student.id if student else None}, Subject={subject.id if subject else None}"
)

from app.services.unified_service import generate_unified_draft_stream


async def test():
    # Force use working API key and model in Settings object directly
    from app.core.config import settings

    settings.NVIDIA_API_KEY = (
        "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"
    )
    settings.NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"
    print("3. Streaming generate_unified_draft...\n")
    i = 0
    async for msg_type, msg_data in generate_unified_draft_stream(
        student=student,
        subject_obj=subject,
        target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        user_message="Hay lap lo trinh",
        session_id=None,
    ):
        if msg_type == "progress":
            print(f"[{i}] PROGRESS: {msg_data}")
        elif msg_type == "token":
            if i % 20 == 0:
                print(f"[{i}] TOKEN: {msg_data[:50]}...")
        elif msg_type == "complete_plan":
            plan = msg_data["plan"]
            print(f"\n[{i}] COMPLETE: plan received")
            print(f"   weeks={len(plan.weeks)} daily={len(plan.daily_schedule)}")
            print(
                f"   quizzes={len(plan.quizzes)} materials={len(plan.curriculum_materials)}"
            )
        elif msg_type == "error":
            print(f"[{i}] ERROR: {msg_data}")
            return
        i += 1

    print("\n=== STREAM TEST DONE ===")


asyncio.run(test())
