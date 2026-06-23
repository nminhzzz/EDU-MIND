import sys, os, time
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

print("Testing generate_content_nvidia...", flush=True)
t0 = time.time()
resp = generate_content_nvidia(
    messages=[{"role":"user","content":"Lap lo trinh hoc toan dai so tuyen tinh, chi can 5 dong"}],
    system_instruction="Ban la gia su toan. Tra loi bang tieng Viet ngan gon.",
    response_schema=None, temperature=0.2, tools=None
)
elapsed = time.time() - t0
print(f"OK time={elapsed:.1f}s len={len(resp)}", flush=True)
