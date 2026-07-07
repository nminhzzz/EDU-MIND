from openai import OpenAI

old_api_key = "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"
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=old_api_key)

try:
    print("Testing chat completion with old key and meta/llama-3.1-8b-instruct...")
    completion = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": "Xin chào! Trả lời ngắn gọn."}],
        temperature=0.5,
        max_tokens=100,
    )
    print("Success!")
    print(f"Response: {completion.choices[0].message.content}")
except Exception as e:
    print(f"Failed: {e}")
