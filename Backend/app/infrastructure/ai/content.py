"""
NVIDIA NIM chat completion — sync, async, and streaming generation with optional tool-calling.
"""

import inspect
import json
from typing import Any, Dict, Generator, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai.nim_client import get_nvidia_async_client, get_nvidia_client

logger = get_logger(__name__)


def function_to_openai_tool(func) -> dict:
    """Convert a plain Python function into an OpenAI tool definition (JSON Schema)."""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    description = doc.split("\n")[0].strip() if doc else f"Hàm {func.__name__}"

    _TYPE_MAP = {int: "integer", float: "number", bool: "boolean", list: "array"}

    properties: dict = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        if name in {"self", "db"}:
            continue
        param_type = _TYPE_MAP.get(param.annotation, "string")
        properties[name] = {"type": param_type, "description": f"Tham số {name}"}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def _format_messages(
    messages: List[Any],
    system_instruction: Optional[str],
    schema_instruction: str = "",
) -> List[Dict[str, str]]:
    """
    Build the final OpenAI messages list by prepending the system prompt
    and normalising all incoming message objects to plain dicts.
    """
    sys_prompt = (system_instruction or "Bạn là một trợ lý AI hữu ích.") + schema_instruction

    formatted: List[Dict[str, str]] = [{"role": "system", "content": sys_prompt}]

    for msg in messages:
        if isinstance(msg, dict):
            formatted.append(msg)
            continue

        role = (
            "assistant"
            if getattr(msg, "role", "user") in {"model", "assistant"}
            else "user"
        )
        if hasattr(msg, "parts") and msg.parts:
            parts_text = "\n".join(
                p.text if hasattr(p, "text") and p.text else str(p)
                for p in msg.parts
            )
            content_text = parts_text
        else:
            content_text = str(msg)

        formatted.append({"role": role, "content": content_text})

    return formatted


def _build_schema_instruction(response_schema: Optional[Any]) -> str:
    if response_schema is None:
        return ""
    try:
        if hasattr(response_schema, "model_json_schema"):
            json_schema = response_schema.model_json_schema()
        elif hasattr(response_schema, "schema"):
            json_schema = response_schema.schema()
        else:
            return ""

        return (
            "\n\n[CRITICAL FORMATTING REQUIREMENT]\n"
            "Bạn PHẢI trả về một đối tượng JSON hợp lệ khớp chính xác 100% với JSON Schema dưới đây:\n"
            f"{json.dumps(json_schema, ensure_ascii=False, indent=2)}\n"
            "Hãy chắc chắn tất cả các trường bắt buộc (required) đều có mặt và đúng kiểu dữ liệu. "
            "Chỉ trả về JSON thuần túy, tuyệt đối không kèm lời dẫn hay ký tự định dạng nào khác ngoài JSON."
        )
    except Exception as exc:
        logger.warning("Lỗi phân tích JSON Schema: %s", exc)
        return ""


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers that some LLMs add around JSON output."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            end = -1 if lines[-1].startswith("```") else len(lines)
            text = "\n".join(lines[1:end]).strip()
    return text


def generate_content_nvidia(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Call the NVIDIA NIM chat completion API with optional ReAct tool-calling loop.
    Supports JSON schema enforcement via system-prompt injection.
    """
    client = get_nvidia_client()
    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    available_functions = {f.__name__: f for f in tools} if tools else {}
    openai_tools = [function_to_openai_tool(f) for f in tools] if tools else None
    response_format = {"type": "json_object"} if response_schema else None

    text_response = ""
    for _ in range(5):
        current_tools = openai_tools
        current_format = response_format if not current_tools else None

        completion = client.chat.completions.create(
            model=settings.NVIDIA_MODEL,
            messages=formatted_messages,
            temperature=temperature,
            tools=current_tools,
            response_format=current_format,
            max_tokens=max_tokens,
            timeout=180.0,
        )

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            text_response = response_message.content or ""
            break

        formatted_messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tc in tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            if fn_name in available_functions:
                try:
                    logger.debug("AI Agent calling tool: %s with args %s", fn_name, fn_args)
                    result_str = json.dumps(
                        available_functions[fn_name](**fn_args), ensure_ascii=False
                    )
                except Exception as exc:
                    logger.warning("Error executing tool %s: %s", fn_name, exc)
                    result_str = f"Error executing tool: {exc}"
            else:
                logger.warning("AI Agent tried to call undefined tool: %s", fn_name)
                result_str = f"Error: Tool '{fn_name}' is not available."

            formatted_messages.append(
                {"tool_call_id": tc.id, "role": "tool", "name": fn_name, "content": result_str}
            )

    return _strip_markdown_fences(text_response)


def generate_content_nvidia_stream(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """Stream NVIDIA NIM chat completion token by token."""
    client = get_nvidia_client()
    formatted_messages = _format_messages(messages, system_instruction)

    completion = client.chat.completions.create(
        model=settings.NVIDIA_MODEL,
        messages=formatted_messages,
        temperature=temperature,
        stream=True,
        timeout=180.0,
    )

    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def generate_content_nvidia_async(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Async version of generate_content_nvidia — uses AsyncOpenAI so the event loop
    is not blocked while waiting for the LLM response.

    Does NOT support tool-calling (ReAct loop) — use the sync version for agents
    that need tool use.  Suitable for single-turn JSON-schema generation tasks
    (quiz generation, analytics evaluation, recommendations).
    """
    client = get_nvidia_async_client()
    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    response_format = {"type": "json_object"} if response_schema else None

    completion = await client.chat.completions.create(
        model=settings.NVIDIA_MODEL,
        messages=formatted_messages,
        temperature=temperature,
        response_format=response_format,
        max_tokens=max_tokens,
        timeout=180.0,
    )
    return _strip_markdown_fences(completion.choices[0].message.content or "")
