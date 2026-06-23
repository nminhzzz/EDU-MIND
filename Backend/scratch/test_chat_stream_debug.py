import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

from app.agents.chat_tutor.agent import chat_with_tutor_stream
import app.agents.chat_tutor.memory as tutor_memory

async def main():
    print("Starting chat stream debug...")
    try:
        print("Creating tutor session...")
        session_id = await tutor_memory.create_tutor_session(
            student_id=1,
            subject_id=1,
            title="Debug Stream Session"
        )
        print(f"Session created: {session_id}")
        
        print("Calling chat_with_tutor_stream...")
        generator = chat_with_tutor_stream(
            user_message="Xin chào! Bạn là ai? Trả lời ngắn gọn.",
            history=None,
            student_id=1,
            session_id=session_id
        )
        print("Iterating stream...")
        async for token in generator:
            print(token, end="", flush=True)
        print("\nFinished stream!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
