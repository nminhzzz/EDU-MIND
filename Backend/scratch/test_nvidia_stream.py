import os
from openai import OpenAI


def test_nvidia_stream():
    api_key = "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"
    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

    model = "meta/llama-3.1-70b-instruct"

    print("Calling NVIDIA NIM with stream=True...")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Xin chào! Trả lời ngắn gọn."}],
            temperature=0.5,
            stream=True,
        )
        print("Response stream: ", end="", flush=True)
        for chunk in completion:
            if (
                chunk.choices
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\nSuccess!")
    except Exception as e:
        print("\nError:", e)


if __name__ == "__main__":
    test_nvidia_stream()
