import os
from openai import OpenAI

def test_nvidia_api():
    api_key = "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"
    
    print("Initializing OpenAI client with NVIDIA base URL...")
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    
    # Một số mô hình phổ biến của Meta Llama trên NVIDIA NIM
    models_to_try = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama3-70b-instruct",
        "meta/llama-3.1-8b-instruct",
        "meta/llama3-8b-instruct"
    ]
    
    for model in models_to_try:
        try:
            print(f"\nTrying model: {model}...")
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Xin chào! Bạn là ai? Trả lời ngắn gọn."}],
                temperature=0.5,
                max_tokens=100
            )
            print(f"Success with model {model}!")
            print(f"Response: {completion.choices[0].message.content}")
            return model # Trả về model thành công đầu tiên
        except Exception as e:
            print(f"Failed with model {model}: {e}")
            
    print("\nAll models failed!")
    return None

if __name__ == "__main__":
    test_nvidia_api()
