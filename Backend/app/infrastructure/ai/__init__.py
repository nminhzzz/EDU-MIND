"""NVIDIA NIM adapters — client factories and content generation."""

from app.infrastructure.ai.content import (
    function_to_openai_tool,
    generate_content_nvidia,
    generate_content_nvidia_async,
    generate_content_nvidia_stream,
)
from app.infrastructure.ai.nim_client import (
    get_langchain_nvidia,
    get_nvidia_async_client,
    get_nvidia_client,
)

__all__ = [
    "function_to_openai_tool",
    "generate_content_nvidia",
    "generate_content_nvidia_async",
    "generate_content_nvidia_stream",
    "get_langchain_nvidia",
    "get_nvidia_async_client",
    "get_nvidia_client",
]
