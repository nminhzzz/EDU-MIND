import requests
import time

old_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {old_key}", "Content-Type": "application/json"}
prompt = [{"role": "user", "content": "Xin chào! Trả lời ngắn gọn."}]

models = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "stepfun-ai/step-3.7-flash",
    "stepfun-ai/step-3.5-flash",
]

for model in models:
    try:
        t0 = time.time()
        r = requests.post(
            url,
            headers=headers,
            json={
                "model": model,
                "messages": prompt,
                "max_tokens": 100,
                "temperature": 0.5,
            },
        )
        elapsed = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[{elapsed:.2f}s] ✅ {model}: {repr(content[:80])}")
        else:
            print(f"[{elapsed:.2f}s] ❌ {model}: HTTP {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"ERROR {model}: {e}")
