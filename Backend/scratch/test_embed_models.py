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
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

embed_models = [
    "nvidia/nv-embed-v1",
    "nvidia/embed-qa-4",
    "nvidia/nv-embedqa-e5-v5"
]

for model in embed_models:
    try:
        print(f"Trying embedding with {model}...")
        response = client.embeddings.create(
            input=["Hello world"],
            model=model
        )
        print(f"Success! Vector length: {len(response.data[0].embedding)}")
    except Exception as e:
        print(f"Failed with {model}: {e}")
