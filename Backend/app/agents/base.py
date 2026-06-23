import os
import inspect
import json
from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.core.config import settings

def function_to_openai_tool(func):
    """
    Tự động chuyển đổi một hàm Python thành định nghĩa OpenAI Tool (JSON Schema).
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    
    # Dòng đầu tiên của docstring làm mô tả
    description = doc.split("\n")[0].strip() if doc else f"Hàm {func.__name__}"
    
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ["self", "db"]:  # Bỏ qua 'self' và 'db' session
            continue
            
        # Xác định kiểu dữ liệu
        param_type = "string"
        if param.annotation == int:
            param_type = "integer"
        elif param.annotation == float:
            param_type = "number"
        elif param.annotation == bool:
            param_type = "boolean"
        elif param.annotation == list:
            param_type = "array"
            
        # Tìm mô tả cho tham số
        properties[name] = {
            "type": param_type,
            "description": f"Tham số {name}"
        }
        
        # Nếu tham số không có giá trị mặc định, nó là bắt buộc
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }

def get_nvidia_client() -> OpenAI:
    """
    Khởi tạo và cấu hình OpenAI Client kết nối tới NVIDIA NIM API.
    """
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY chưa được thiết lập.")
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=settings.NVIDIA_API_KEY
    )

def generate_content_nvidia(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    max_tokens: Optional[int] = None
) -> str:
    """
    Hàm gọi trực tiếp NVIDIA NIM API bằng OpenAI SDK, hỗ trợ:
    1. System Instruction.
    2. ReAct Tool-calling loop nếu có tools.
    3. Trả về JSON khớp với response_schema.
    4. Timeout 45 giây để tránh treo kết nối.
    """
    client = get_nvidia_client()
    model_name = settings.NVIDIA_MODEL
    
    # 1. Bổ sung JSON Schema instructions vào system prompt nếu cần
    sys_prompt = system_instruction or "Bạn là một trợ lý AI hữu ích."
    schema_instruction = ""
    if response_schema:
        try:
            if hasattr(response_schema, "model_json_schema"):
                json_schema = response_schema.model_json_schema()
            elif hasattr(response_schema, "schema"):
                json_schema = response_schema.schema()
            else:
                json_schema = None
                
            if json_schema:
                schema_instruction = (
                    f"\n\n[CRITICAL FORMATTING REQUIREMENT]\n"
                    f"Bạn PHẢI trả về một đối tượng JSON hợp lệ khớp chính xác 100% với JSON Schema dưới đây:\n"
                    f"{json.dumps(json_schema, ensure_ascii=False, indent=2)}\n"
                    f"Hãy chắc chắn tất cả các trường bắt buộc (required) đều có mặt và đúng kiểu dữ liệu. "
                    f"Chỉ trả về JSON thuần túy, tuyệt đối không kèm lời dẫn hay ký tự định dạng nào khác ngoài JSON."
                )
        except Exception as e:
            print(f"Lỗi phân tích JSON Schema: {e}")
            
    if schema_instruction:
        sys_prompt += schema_instruction
        
    # Xây dựng danh sách messages gửi cho OpenAI
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": sys_prompt})
    
    # Thêm các message từ đầu vào
    for msg in messages:
        if isinstance(msg, dict):
            formatted_messages.append(msg)
        else:
            # Hỗ trợ nếu input truyền dạng object Content (để backward-compatible)
            role = "assistant" if getattr(msg, "role", "user") in ["model", "assistant"] else "user"
            content_text = ""
            if hasattr(msg, "parts") and msg.parts:
                parts_list = []
                for p in msg.parts:
                    if hasattr(p, "text") and p.text:
                        parts_list.append(p.text)
                    elif isinstance(p, str):
                        parts_list.append(p)
                content_text = "\n".join(parts_list)
            else:
                content_text = str(msg)
            formatted_messages.append({"role": role, "content": content_text})

    # 2. Xử lý Tools và ReAct loop
    available_functions = {f.__name__: f for f in tools} if tools else {}
    openai_tools = [function_to_openai_tool(f) for f in tools] if tools else None
    
    iterations = 0
    max_iterations = 5
    text_response = ""
    
    # Nếu có response_schema, định nghĩa JSON object response format
    response_format = {"type": "json_object"} if response_schema else None
    
    while iterations < max_iterations:
        # Nếu có tools, không được truyền response_format (theo hạn chế của NVIDIA NIM)
        current_tools = openai_tools
        current_format = response_format if not current_tools else None
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            temperature=temperature,
            tools=current_tools,
            response_format=current_format,
            max_tokens=max_tokens,
            timeout=180.0
        )
        
        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # Lưu tin nhắn assistant chứa tool calls vào lịch sử
            assistant_msg = {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            }
            formatted_messages.append(assistant_msg)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name in available_functions:
                    func_to_call = available_functions[function_name]
                    try:
                        print(f"-> AI Agent calling tool: {function_name} with args {function_args}")
                        result = func_to_call(**function_args)
                        result_str = json.dumps(result, ensure_ascii=False)
                    except Exception as ex:
                        result_str = f"Error executing tool: {ex}"
                        print(f"Error executing tool {function_name}: {ex}")
                else:
                    result_str = f"Error: Tool '{function_name}' is not available."
                    print(f"-> AI Agent tried to call undefined tool: {function_name}")
                    
                formatted_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": result_str
                })
            iterations += 1
        else:
            text_response = response_message.content or ""
            break
            
    # Làm sạch markdown blocks nếu LLM tự động bao bọc bằng ```json ... ```
    text_response = text_response.strip()
    if text_response.startswith("```"):
        lines = text_response.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            if lines[-1].startswith("```"):
                text_response = "\n".join(lines[1:-1]).strip()
            else:
                text_response = "\n".join(lines[1:]).strip()
                
    return text_response

def generate_content_nvidia_stream(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    temperature: float = 0.7
):
    """
    Gọi NVIDIA NIM API qua OpenAI SDK hỗ trợ streaming từng token.
    """
    client = get_nvidia_client()
    model_name = settings.NVIDIA_MODEL
    
    sys_prompt = system_instruction or "Bạn là một trợ lý AI hữu ích."
    
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": sys_prompt})
    
    for msg in messages:
        if isinstance(msg, dict):
            formatted_messages.append(msg)
        else:
            role = "assistant" if getattr(msg, "role", "user") in ["model", "assistant"] else "user"
            content_text = ""
            if hasattr(msg, "parts") and msg.parts:
                parts_list = []
                for p in msg.parts:
                    if hasattr(p, "text") and p.text:
                        parts_list.append(p.text)
                    elif isinstance(p, str):
                        parts_list.append(p)
                content_text = "\n".join(parts_list)
            else:
                content_text = str(msg)
            formatted_messages.append({"role": role, "content": content_text})

    completion = client.chat.completions.create(
        model=model_name,
        messages=formatted_messages,
        temperature=temperature,
        stream=True,
        timeout=180.0
    )

    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def get_langchain_nvidia(temperature: float = 0.2):
    """
    Trả về Chat Model tương ứng của NVIDIA NIM qua LangChain ChatOpenAI.
    """
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY chưa được thiết lập.")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.NVIDIA_MODEL,
        openai_api_key=settings.NVIDIA_API_KEY,
        openai_api_base="https://integrate.api.nvidia.com/v1",
        temperature=temperature
    )
