import sys, os, time, asyncio, json

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
from app.database.mongodb import get_mongodb_db
from app.services.embedding_service import vector_search_materials
from app.agents.tools.db_tools import get_student_analytics_db, get_recent_attempts_db
from app.agents.base import generate_content_nvidia
from datetime import date

student_id = 3
subject_id = 4
subject = "MACLENIN_UNIFIED"
target_score = 8.0
deadline = date(2026, 7, 7)
study_hours_per_day = 2.0
preferred_time = "buổi tối"
off_days = ["sun"]
current_date = "2026-06-23"
days_left = 14

print("1. RAG search...", flush=True)
db_mongo = get_mongodb_db()
materials = asyncio.run(
    vector_search_materials(
        db_mongo=db_mongo, query_text=subject, subject_id=subject_id, top_k=3
    )
)
print(f"   Found {len(materials)} materials", flush=True)

context_parts = []
for i, m in enumerate(materials):
    content = m["content"]
    if len(content) > 500:
        content = content[:500] + "..."
    context_parts.append(f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{content}")
context_str = "\n\n".join(context_parts)
print(f"2. Context size: {len(context_str)} chars", flush=True)

print("3. Analytics...", flush=True)
analytics = get_student_analytics_db(student_id, subject_id)
recent_attempts = get_recent_attempts_db(student_id, limit=5)
analytics_str = f"Điểm TB: {analytics['average_score']}/10 Yếu: {','.join(analytics['weak_topics'])}"
print(f"   Analytics size: {len(analytics_str)} chars", flush=True)

system_instruction = (
    f"Bạn là chuyên gia giáo dục Việt Nam. "
    f"Lập lộ trình mục tiêu {target_score}/10 môn '{subject}' hạn {deadline} (còn {days_left} ngày). "
    f"Học {study_hours_per_day}h/ngày, khung {preferred_time}. "
    f"Nghỉ: {', '.join(off_days)}. "
    f"Trả về JSON: weeks, daily_schedule, curriculum_materials, quizzes. "
    f"Chỉ trả về JSON thuần."
)
if analytics_str:
    system_instruction += f" Học lực: {analytics_str[:200]}"
if context_str:
    system_instruction += f" Tài liệu: {context_str[:400]}"

print(f"4. System instruction: {len(system_instruction)} chars", flush=True)
print(f"   First 300: {system_instruction[:300]}", flush=True)

messages = [{"role": "user", "content": f"Lập lộ trình môn '{subject}'."}]

print("5. Calling API with 8B model...", flush=True)
t0 = time.time()
resp = generate_content_nvidia(
    messages=messages,
    system_instruction=system_instruction,
    response_schema=None,
    temperature=0.2,
    tools=None,
    max_tokens=2048,
)
elapsed = time.time() - t0
print(f"   OK {elapsed:.1f}s, {len(resp)} chars", flush=True)
print(f"   First 200: {resp[:200]}", flush=True)
