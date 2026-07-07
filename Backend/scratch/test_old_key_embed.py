from openai import OpenAI

old_api_key = "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"
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=old_api_key)

try:
    print("Testing embedding with old key...")
    response = client.embeddings.create(
        input=["Hello world"], model="nvidia/nv-embed-v1"
    )
    print(f"Success! Vector length: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"Failed: {e}")
