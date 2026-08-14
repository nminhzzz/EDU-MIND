"""
AI chat completion — sync, async, and streaming generation with optional
structured JSON output.

Supports any OpenAI-compatible provider configured via .env.
Response-format differences (e.g. cline-pass wrapping) are handled at the
transport layer in nim_client.py — this module stays provider-agnostic.
"""

import json
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, Generator, List, Optional

from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai.nim_client import get_langchain_deepseek, get_deepseek_client

logger = get_logger(__name__)
_usage_recorder: ContextVar[Optional[Callable[[dict], None]]] = ContextVar(
    "ai_usage_recorder", default=None
)


@contextmanager
def capture_ai_usage(recorder: Callable[[dict], None]):
    token = _usage_recorder.set(recorder)
    try:
        yield
    finally:
        _usage_recorder.reset(token)


def _record_response_usage(response: Any) -> None:
    recorder = _usage_recorder.get()
    if recorder is None:
        return
    usage = getattr(response, "usage_metadata", None) or {}
    response_metadata = getattr(response, "response_metadata", None) or {}
    token_usage = response_metadata.get("token_usage", {})
    prompt_tokens = usage.get("input_tokens", token_usage.get("prompt_tokens", 0)) or 0
    completion_tokens = usage.get("output_tokens", token_usage.get("completion_tokens", 0)) or 0
    payload = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": (
            usage.get("total_tokens", token_usage.get("total_tokens", 0))
            or prompt_tokens + completion_tokens
        ),
        "cached_tokens": (
            usage.get("input_token_details", {}).get("cache_read", 0)
            or token_usage.get("prompt_cache_hit_tokens", 0)
        ),
    }
    try:
        recorder(payload)
    except Exception:
        logger.exception("Could not persist AI usage metadata")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


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
            content = "\n".join(
                p.text if hasattr(p, "text") and p.text else str(p)
                for p in msg.parts
            )
        else:
            content = str(msg)

        formatted.append({"role": role, "content": content})

    return formatted


def _build_schema_instruction(response_schema: Optional[Any]) -> str:
    """
    Return a prompt suffix that instructs the LLM to output JSON conforming
    to *response_schema*.  Returns an empty string when no schema is provided.
    """
    if response_schema is None:
        return ""

    try:
        if hasattr(response_schema, "model_json_schema"):
            json_schema = response_schema.model_json_schema()
        elif hasattr(response_schema, "schema"):
            json_schema = response_schema.schema()
        else:
            return ""

        def compact(value):
            if isinstance(value, dict):
                return {
                    key: compact(item)
                    for key, item in value.items()
                    if key not in {"title", "description", "default", "examples"}
                }
            if isinstance(value, list):
                return [compact(item) for item in value]
            return value

        json_schema = compact(json_schema)
        return (
            "\n\n[CRITICAL FORMATTING REQUIREMENT]\n"
            "Bạn PHẢI trả về một đối tượng JSON hợp lệ khớp chính xác 100% với JSON Schema dưới đây:\n"
            f"{json.dumps(json_schema, ensure_ascii=False, separators=(',', ':'))}\n"
            "Hãy chắc chắn tất cả các trường bắt buộc (required) đều có mặt và đúng kiểu dữ liệu. "
            "Chỉ trả về JSON thuần túy, tuyệt đối không kèm lời dẫn hay ký tự định dạng nào khác ngoài JSON."
        )
    except Exception as exc:
        logger.warning("Lỗi phân tích JSON Schema: %s", exc)
        return ""


def _serialise_structured_response(response: Any) -> str:
    """Serialise a Pydantic model, dict, or other object to a JSON string."""
    if isinstance(response, BaseModel):
        return response.model_dump_json()
    if isinstance(response, dict):
        return json.dumps(response, ensure_ascii=False)
    return str(response)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_content_deepseek(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    max_tokens: Optional[int] = None,
    request_timeout: int = 150,
) -> str:
    """
    Call the configured OpenAI-compatible AI provider via LangChain (sync).

    When *response_schema* is supplied the schema is injected into the system
    prompt (via ``_build_schema_instruction``) and the model is asked to return
    plain JSON.  We intentionally do NOT use ``with_structured_output`` because
    that path relies on the OpenAI SDK's internal choice-parsing which crashes
    on providers (e.g. cline-pass) that wrap the payload in a ``data`` field.
    """
    extra_params: Dict[str, Any] = {}
    if max_tokens:
        extra_params["max_tokens"] = max_tokens

    llm = get_langchain_deepseek(
        temperature=temperature,
        request_timeout=request_timeout,
        **extra_params,
    )

    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    sys_instruction_text = formatted_messages[0]["content"] if formatted_messages else ""
    user_msgs_text = json.dumps(formatted_messages[1:], ensure_ascii=False, indent=2) if len(formatted_messages) > 1 else ""

    logger.info(
        "AI request prepared: system_chars=%d user_chars=%d",
        len(sys_instruction_text),
        len(user_msgs_text),
    )

    if tools:
        response = llm.bind_tools(tools).invoke(formatted_messages)
        _record_response_usage(response)
        return response.content

    response = llm.invoke(formatted_messages)
    _record_response_usage(response)
    return response.content


def generate_content_deepseek_stream(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """Stream chat completion token by token using the raw OpenAI client."""
    client = get_deepseek_client()
    formatted_messages = _format_messages(messages, system_instruction)

    completion = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=formatted_messages,
        temperature=temperature,
        stream=True,
        timeout=180.0,
    )

    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def generate_content_deepseek_async(
    messages: List[Dict[str, str]],
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    request_timeout: int = 150,
) -> str:
    """Async version of ``generate_content_deepseek`` — see sync version for full docs."""
    extra_params: Dict[str, Any] = {}
    if max_tokens:
        extra_params["max_tokens"] = max_tokens

    llm = get_langchain_deepseek(
        temperature=temperature,
        request_timeout=request_timeout,
        **extra_params,
    )

    schema_instruction = _build_schema_instruction(response_schema)
    formatted_messages = _format_messages(messages, system_instruction, schema_instruction)

    response = await llm.ainvoke(formatted_messages)
    _record_response_usage(response)
    return response.content
