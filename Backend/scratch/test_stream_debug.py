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
                key_clean = key.strip(); val_clean = val.strip()
                if key_clean not in os.environ or not os.environ[key_clean].strip():
                    os.environ[key_clean] = val_clean

from app.database.redis import get_redis_client
from app.database.mysql import SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject
from app.database.mysql import engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()
student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
db.close()

from app.agents.base import generate_content_nvidia, generate_content_nvidia_stream
from app.agents.unified_agent import generate_unified_plan

async def test():
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # First test: sync version to see what it outputs
    print("=== Testing sync version ===")
    plan = await generate_unified_plan(
        subject=subject.name, target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        student_id=student.id, subject_id=subject.id,
        study_hours_per_day=2, preferred_time="buoi toi",
        off_days=["sun"], current_date=date.today().strftime("%Y-%m-%d"),
        db_mongo=None
    )
    print(f"Sync OK: weeks={len(plan.weeks)} daily={len(plan.daily_schedule)}")

    # Now test streaming with clean collection
    print("\n=== Testing stream tokens ===")
    from app.agents.unified_agent import generate_unified_plan_stream
    tokens = []
    async for msg_type, msg_data in generate_unified_plan_stream(
        subject=subject.name, target_score=8.0,
        deadline=date.today() + timedelta(days=14),
        student_id=student.id, subject_id=subject.id,
        study_hours_per_day=2, preferred_time="buoi toi",
        off_days=["sun"], current_date=date.today().strftime("%Y-%m-%d"),
        db_mongo=None
    ):
        if msg_type == "token":
            tokens.append(msg_data)
        elif msg_type == "complete":
            print(f"Stream complete: weeks={len(msg_data.weeks)} daily={len(msg_data.daily_schedule)}")
        elif msg_type == "error":
            full_text = "".join(tokens)
            print(f"Stream ERROR: {msg_data}")
            print(f"Full collected text ({len(full_text)} chars):")
            print(repr(full_text[:1000]))

    if tokens:
        full = "".join(tokens)
        print(f"\nTotal tokens collected: {len(tokens)}, total chars: {len(full)}")
        # Show first and last 200 chars
        print(f"START: {repr(full[:200])}")
        print(f"END:   {repr(full[-200:])}")

asyncio.run(test())
