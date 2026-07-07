import sys, os, time, json

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

from app.agents.base import generate_content_nvidia

system_instruction = (
    "Bạn là chuyên gia giáo dục Việt Nam. "
    "Lập lộ trình mục tiêu 8/10 môn 'Toán Đại số' hạn 2026-07-07 (còn 14 ngày). "
    "Học 2h/ngày, khung buổi tối. Nghỉ: Chủ nhật. "
    "Trả về JSON: weeks (tuần+tasks), daily_schedule (date,start_time,end_time,task,description), "
    "curriculum_materials (topic,content), quizzes (title,questions). "
    "Chỉ trả về JSON thuần."
)

prompt = "Lập lộ trình môn 'Toán Đại số'."

print("Testing with max_tokens=2048...", flush=True)
t0 = time.time()
resp = generate_content_nvidia(
    messages=[{"role": "user", "content": prompt}],
    system_instruction=system_instruction,
    response_schema=None,
    temperature=0.2,
    tools=None,
    max_tokens=2048,
)
elapsed = time.time() - t0
print(f"Time: {elapsed:.1f}s, Response: {len(resp)} chars", flush=True)
print(f"First 200: {resp[:200]}", flush=True)

try:
    data = json.loads(resp)
    print(
        f"Has weeks: {len(data.get('weeks', []))}, daily: {len(data.get('daily_schedule', []))}"
    )
    print(
        f"Has materials: {len(data.get('curriculum_materials', []))}, quizzes: {len(data.get('quizzes', []))}"
    )
except Exception as e:
    print(f"JSON parse error: {e}")
