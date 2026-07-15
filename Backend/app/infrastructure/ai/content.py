"""
NVIDIA NIM chat completion — sync, async, and streaming generation with optional tool-calling.
"""

import json
from typing import Any, Dict, Generator, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai.nim_client import get_nvidia_client

logger = get_logger(__name__)


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





from pydantic import BaseModel
from app.infrastructure.ai.nim_client import get_langchain_nvidia


def generate_content_nvidia(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Call the NVIDIA NIM chat completion API using LangChain.
    Supports JSON schema enforcement via structured outputs.
    """
    extra_params = {}
    if max_tokens:
        extra_params["max_tokens"] = max_tokens

    llm = get_langchain_nvidia(temperature=temperature, **extra_params)

    # If response_schema is provided, we use LangChain's structured output.
    # We still build and inject schema instruction as a fallback/safeguard for prompt guidelines.
    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    if response_schema:
        structured_llm = llm.with_structured_output(response_schema)
        response = structured_llm.invoke(formatted_messages)
        if isinstance(response, BaseModel):
            return response.model_dump_json()
        elif isinstance(response, dict):
            return json.dumps(response, ensure_ascii=False)
        else:
            return str(response)
    else:
        if tools:
            llm_with_tools = llm.bind_tools(tools)
            response = llm_with_tools.invoke(formatted_messages)
            return response.content
        else:
            response = llm.invoke(formatted_messages)
            return response.content


def generate_content_nvidia_stream(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """Stream NVIDIA NIM chat completion token by token (raw API for performance)."""
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
    Async version of generate_content_nvidia using LangChain's ainvoke.
    """
    extra_params = {}
    if max_tokens:
        extra_params["max_tokens"] = max_tokens

    llm = get_langchain_nvidia(temperature=temperature, **extra_params)

    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    if response_schema:
        structured_llm = llm.with_structured_output(response_schema)
        response = await structured_llm.ainvoke(formatted_messages)
        if isinstance(response, BaseModel):
            return response.model_dump_json()
        elif isinstance(response, dict):
            return json.dumps(response, ensure_ascii=False)
        else:
            return str(response)
    else:
        response = await llm.ainvoke(formatted_messages)
        return response.content

