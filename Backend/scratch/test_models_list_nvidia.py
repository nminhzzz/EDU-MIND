import os
from openai import OpenAI

# Load .env variables
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

api_key = os.environ.get("NVIDIA_API_KEY")
print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

try:
    print("\n--- Listing NVIDIA NIM Models ---")
    models = client.models.list()
    for m in models.data:
        if "embed" in m.id or "step" in m.id:
            print(f"- {m.id}")
except Exception as e:
    print(f"Failed to list models: {e}")
