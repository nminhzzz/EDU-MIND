import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

from app.database.mysql import Base, engine, SessionLocal
from app.agents.tools.db_tools import (
    get_student_analytics_db,
    get_student_study_plans_db,
)


def test():
    Base.metadata.create_all(bind=engine)
    print("Testing db tools...")
    try:
        res = get_student_analytics_db(student_id="3", subject_id="4")
        print("Analytics Success! Result:", res)
        plans = get_student_study_plans_db(student_id=3)
        print("Plans Success! Result:", plans)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    test()
