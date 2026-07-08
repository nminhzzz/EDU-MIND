"""
Backward-compatible re-exports — prefer app.infrastructure.ai.
"""

from app.infrastructure.ai import (  # noqa: F401
    function_to_openai_tool,
    generate_content_nvidia,
    generate_content_nvidia_async,
    generate_content_nvidia_stream,
    get_langchain_nvidia,
    get_nvidia_async_client,
    get_nvidia_client,
)
