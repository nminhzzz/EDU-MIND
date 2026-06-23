import sys, os, asyncio
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                k, v = line_str.split("=", 1)
                k2, v2 = k.strip(), v.strip()
                if k2 not in os.environ or not os.environ[k2].strip():
                    os.environ[k2] = v2

from app.database.mysql import SessionLocal
from app.models.user import User
from app.models.subject import Subject
db = SessionLocal()
student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
db.close()
print(f"1. {student.id} {subject.id}", flush=True)

from app.services.unified_service import generate_unified_draft_stream

async def test():
    print("2. entering async for", flush=True)
    gen = generate_unified_draft_stream(
        student=student, subject_obj=subject,
        target_score=7.0,
        deadline=date.today() + timedelta(days=7),
        user_message="test", session_id=None
    )
    print("3. got generator", flush=True)
    i = 0
    try:
        async for msg_type, msg_data in gen:
            print(f"[{i}] {msg_type}: {str(msg_data)[:80]}", flush=True)
            i += 1
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
    print("4. DONE", flush=True)

asyncio.run(test())
