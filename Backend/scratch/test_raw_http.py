import requests
import json

api_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "stepfun-ai/step-3.7-flash",
    "messages": [{"role": "user", "content": "hello"}],
    "temperature": 0.5,
    "max_tokens": 100
}

try:
    print("Sending POST request to NVIDIA API...")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response text:")
    print(response.text)
except Exception as e:
    print(f"HTTP request failed: {e}")
