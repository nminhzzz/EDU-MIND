"""
Backward-compatible re-exports — prefer app.infrastructure.ai.
"""

from app.infrastructure.ai import (  # noqa: F401
    generate_content_nvidia,
    generate_content_nvidia_async,
    generate_content_nvidia_stream,
    get_langchain_nvidia,
    get_nvidia_client,
)
