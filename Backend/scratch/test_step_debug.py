import requests
import json

old_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {old_key}", "Content-Type": "application/json"}

print("=== Debug step-3.7-flash response format ===\n")
r = requests.post(
    url,
    headers=headers,
    json={
        "model": "stepfun-ai/step-3.7-flash",
        "messages": [
            {"role": "user", "content": "Xin chào! Trả lời ngắn gọn bằng 1 câu."}
        ],
        "max_tokens": 200,
        "temperature": 0.5,
    },
)
print(f"Status: {r.status_code}")
print(f"\nFull JSON response:")
data = r.json()
print(json.dumps(data, ensure_ascii=False, indent=2))
