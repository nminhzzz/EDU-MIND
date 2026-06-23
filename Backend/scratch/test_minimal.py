import sys, os, asyncio
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

print("A", flush=True)
from app.database.mysql import SessionLocal
from app.models.user import User
from app.models.subject import Subject
print("B", flush=True)
db = SessionLocal()
student = db.query(User).filter(User.email == "unified_student_test@test.com").first()
subject = db.query(Subject).filter(Subject.code == "MACLENIN_UNIFIED").first()
db.close()
print(f"C {student.id} {subject.id}", flush=True)

async def test():
    print("D", flush=True)
    await asyncio.sleep(0.1)
    print("E", flush=True)

asyncio.run(test())
print("F", flush=True)
