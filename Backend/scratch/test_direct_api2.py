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

# Test 1: Simple
print("T1 Simple...", flush=True)
t0 = time.time()
r = client.chat.completions.create(model="meta/llama-3.1-70b-instruct", messages=[{"role":"user","content":"Say 3 words"}], max_tokens=10, timeout=30)
print(f"  OK {time.time()-t0:.1f}s: {r.choices[0].message.content}", flush=True)

# Test 2: With system instruction
print("T2 With system...", flush=True)
t0 = time.time()
r = client.chat.completions.create(model="meta/llama-3.1-70b-instruct", messages=[{"role":"system","content":"Ban la gia su toan."},{"role":"user","content":"Lap lo trinh 3 dong."}], max_tokens=100, timeout=30)
print(f"  OK {time.time()-t0:.1f}s: {r.choices[0].message.content[:100]}", flush=True)

# Test 3: With system + response_format json_object
print("T3 JSON...", flush=True)
t0 = time.time()
r = client.chat.completions.create(model="meta/llama-3.1-70b-instruct", messages=[{"role":"system","content":"Ban la gia su toan. Tra loi JSON."},{"role":"user","content":"Lap lo trinh 3 ngay: ngay,mon,gio"}], response_format={"type":"json_object"}, max_tokens=200, timeout=30)
print(f"  OK {time.time()-t0:.1f}s: {r.choices[0].message.content[:100]}", flush=True)

# Test 4: RAG-like long context
print("T4 Long context...", flush=True)
t0 = time.time()
r = client.chat.completions.create(model="meta/llama-3.1-70b-instruct", messages=[{"role":"user","content":"Tom tat: " + "X"*3000}], max_tokens=50, timeout=30)
print(f"  OK {time.time()-t0:.1f}s", flush=True)

print("ALL DONE", flush=True)
