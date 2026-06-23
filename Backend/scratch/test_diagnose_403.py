import requests
import json

api_key = "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"

# Test 1: List models (chỉ cần GET, ko cần quyền cao)
print("=== Test 1: GET /v1/models ===")
r = requests.get(
    "https://integrate.api.nvidia.com/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("Key is valid for listing models!")
else:
    print(f"Response: {r.text}")

# Test 2: Chat completions voi step-3.7-flash
print("\n=== Test 2: POST chat completions (step-3.7-flash) ===")
r2 = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={
        "model": "stepfun-ai/step-3.7-flash",
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 50
    }
)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:300]}")

# Test 3: Chat completions voi step-3.5-flash (model khac cung hop le)
print("\n=== Test 3: POST chat completions (step-3.5-flash) ===")
r3 = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={
        "model": "stepfun-ai/step-3.5-flash",
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 50
    }
)
print(f"Status: {r3.status_code}")
print(f"Response: {r3.text[:300]}")
