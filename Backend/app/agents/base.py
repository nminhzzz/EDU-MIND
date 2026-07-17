"""
Backward-compatible re-exports — prefer app.infrastructure.ai.
"""

from app.infrastructure.ai import (  # noqa: F401
    generate_content_deepseek,
    generate_content_deepseek_async,
    generate_content_deepseek_stream,
    get_langchain_deepseek,
    get_deepseek_client,
)
