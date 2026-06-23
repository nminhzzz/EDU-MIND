import os, sys, json, time
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

import requests
api_key = os.environ.get("NVIDIA_API_KEY", "")
print(f"Using key: {api_key[:10]}...{api_key[-4:]}")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
payload = {
    "model": "meta/llama-3.1-70b-instruct",
    "messages": [{"role":"user","content":"Say hello in 3 words"}],
    "temperature": 0.2, "max_tokens": 50
}
t0 = time.time()
r = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", json=payload, headers=headers, timeout=60)
elapsed = time.time() - t0
print(f"Status: {r.status_code}, Time: {elapsed:.1f}s")
if r.status_code == 200:
    print(f"Response: {r.json()['choices'][0]['message']['content'][:100]}")
else:
    print(f"Error: {r.text[:300]}")
