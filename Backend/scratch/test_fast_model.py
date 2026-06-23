import os, sys, time
from openai import OpenAI

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
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

models_to_test = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "mistralai/mistral-7b-instruct-v0.3",
]

for model in models_to_test:
    print(f"Testing {model}...", flush=True)
    t0 = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia giáo dục. Lập lộ trình học JSON: weeks (week, tasks), daily_schedule (date, start_time, end_time, task). Chỉ JSON."},
                {"role": "user", "content": "Lập lộ trình học Toán 8/10 trong 7 ngày, 2h/ngày buổi tối."}
            ],
            max_tokens=1024,
            temperature=0.2,
            timeout=60
        )
        elapsed = time.time() - t0
        resp = r.choices[0].message.content
        print(f"  OK {elapsed:.1f}s - {len(resp)} chars", flush=True)
        print(f"  Preview: {resp[:100]}", flush=True)
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAIL {elapsed:.1f}s: {e}", flush=True)
