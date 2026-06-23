import os
import json
from openai import OpenAI

def test_nvidia_tools():
    api_key = "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"
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    
    model = "meta/llama-3.1-70b-instruct"
    
    # 1. Định nghĩa tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_student_analytics_db",
                "description": "Truy vấn phân tích học lực",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer"},
                        "subject_id": {"type": "integer"}
                    },
                    "required": ["student_id"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": "Bạn phải sử dụng tool get_student_analytics_db để tra cứu học lực học sinh trước khi trả lời."},
        {"role": "user", "content": "Hãy phân tích học lực của học sinh ID=3 môn ID=4 và chào họ."}
    ]
    
    print("Calling NVIDIA NIM (Iteration 1)...")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=0.2
        )
        msg = completion.choices[0].message
        print("Iteration 1 response content:", msg.content)
        print("Iteration 1 tool calls:", msg.tool_calls)
        
        if msg.tool_calls:
            # Lưu tool calls vào messages
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            })
            # Giả lập kết quả tool
            tool_result = {"average_score": 7.5, "weak_topics": ["Triết học Mác-Lênin"]}
            messages.append({
                "role": "tool",
                "tool_call_id": msg.tool_calls[0].id,
                "name": "get_student_analytics_db",
                "content": json.dumps(tool_result)
            })
            
            print("\nCalling NVIDIA NIM (Iteration 2)...")
            completion2 = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=0.2
            )
            print("Iteration 2 response content:", completion2.choices[0].message.content)
            print("Success!")
        else:
            print("No tool calls generated!")
    except Exception as e:
        print("Error during tool calling test:", e)

if __name__ == "__main__":
    test_nvidia_tools()
