import sys, os

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

print("1. Starting...")
from app.database.redis import get_redis_client

print("2. Redis imported")
redis_client = get_redis_client()
print("3. Redis client got")
redis_client.ping()
print("4. Redis ping OK")
from app.database.mysql import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.subject import Subject

print("5. Models imported")
print("DONE")
