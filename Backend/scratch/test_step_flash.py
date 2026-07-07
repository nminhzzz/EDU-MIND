import os
from openai import OpenAI

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

api_key = os.environ.get("NVIDIA_API_KEY")
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

try:
    print("Testing chat completion with stepfun-ai/step-3.7-flash...")
    completion = client.chat.completions.create(
        model="stepfun-ai/step-3.7-flash",
        messages=[
            {"role": "user", "content": "Xin chào! Bạn là ai? Trả lời ngắn gọn."}
        ],
        temperature=0.5,
        max_tokens=100,
    )
    print("Success!")
    print(f"Response: {completion.choices[0].message.content}")
except Exception as e:
    print(f"Failed: {e}")
