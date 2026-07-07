import sys, os, asyncio

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

from app.agents.chat_tutor.intent import (
    detect_intent,
    extract_subject,
    extract_target_score,
    extract_deadline,
)
from app.services.unified_service import format_plan_as_text
from app.schemas.unified_goal import UnifiedGoalPlanResponse


async def test():
    r1 = await detect_intent("Toi muon hoc Triet hoc dat 8.0 trong 2 tuan")
    d = r1["data"]
    print(
        f"Intent 1: {r1['type']} | subject={d.get('subject')} score={d.get('target_score')} deadline={d.get('deadline')}"
    )

    r2 = await detect_intent("OK luu lai", session_id="test123")
    print(f"Intent 2: {r2['type']}")

    r3 = await detect_intent("Giai thich quy luat phu dinh cua phu dinh")
    print(f"Intent 3: {r3['type']}")

    print(f"Subject: {extract_subject('Hoc Triet hoc')}")
    print(f"Score: {extract_target_score('Muon dat 8.0 diem')}")
    print(f"Deadline: {extract_deadline('Trong 2 tuan')}")

    sample = UnifiedGoalPlanResponse(
        weeks=[{"week": 1, "tasks": ["Doc chuong 1", "Lam bai tap"]}],
        daily_schedule=[
            {
                "date": "2026-06-24",
                "start_time": "19:00",
                "end_time": "21:00",
                "task": "Hoc chuong 1",
                "description": "Doc sach",
            }
        ],
        curriculum_materials=[
            {"topic": "Chuong 1: Triet hoc", "content": "Noi dung..."}
        ],
        quizzes=[
            {
                "title": "Bai kiem tra",
                "questions": [
                    {
                        "question_text": "Hoi?",
                        "question_type": "true_false",
                        "options": [
                            {"key": "True", "value": "Dung"},
                            {"key": "False", "value": "Sai"},
                        ],
                        "correct_answer": "True",
                        "explanation": "Giai thich",
                        "difficulty": "easy",
                    }
                ],
            }
        ],
    )
    text = format_plan_as_text(sample)
    print(f"Format OK ({len(text)} chars)")
    print(text[:200])


asyncio.run(test())
