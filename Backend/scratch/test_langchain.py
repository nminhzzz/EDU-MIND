from app.core.config import settings
from app.agents.base import get_langchain_nvidia


def test_call():
    print("Testing get_langchain_nvidia call...")
    try:
        llm = get_langchain_nvidia()
        print("Instantiated LLM client successfully.")
        print(f"Calling with NVIDIA_MODEL: {settings.NVIDIA_MODEL}")
        response = llm.invoke("Hello, who are you?")
        print("Response received:")
        print(response.content)
    except Exception as e:
        print("Error calling LangChain NVIDIA:")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_call()
