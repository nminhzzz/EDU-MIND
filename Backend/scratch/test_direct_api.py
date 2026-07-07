import os, sys, time, json
from openai import OpenAI

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

api_key = os.environ.get("NVIDIA_API_KEY", "")
print(f"Key: {api_key[:10]}...{api_key[-4:]}", flush=True)

client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

system_instruction = (
    "Bạn là chuyên gia giáo dục Việt Nam. "
    "Lập lộ trình mục tiêu 8/10 môn 'Toán Đại số' hạn 2026-07-07 (còn 14 ngày). "
    "Học 2h/ngày, khung buổi tối. Nghỉ: Chủ nhật. "
    "Trả về JSON: weeks (tuần+tasks), daily_schedule (date,start_time,end_time,task,description). "
    "Chỉ trả về JSON thuần."
)

messages = [
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": "Lập lộ trình môn 'Toán Đại số'."},
]

print("Calling API directly...", flush=True)
t0 = time.time()
try:
    completion = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
        timeout=60,
    )
    elapsed = time.time() - t0
    resp = completion.choices[0].message.content
    print(f"OK - {elapsed:.1f}s, {len(resp)} chars", flush=True)
    print(resp[:300], flush=True)
except Exception as e:
    elapsed = time.time() - t0
    print(f"FAIL - {elapsed:.1f}s: {e}", flush=True)
