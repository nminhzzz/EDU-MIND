from app.core.config import settings
from app.agents.base import get_nvidia_client


def test_raw_client():
    print("Testing raw OpenAI client with meta/llama-3.1-70b-instruct...")
    try:
        client = get_nvidia_client()
        print("Client initialized.")
        completion = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": "Hello, who are you?"}],
            temperature=0.2,
            max_tokens=50,
        )
        print("Response received:")
        print(completion.choices[0].message.content)
    except Exception as e:
        print("Error calling Llama 3.1 70b:")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_raw_client()
