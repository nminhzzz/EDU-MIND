"""
NVIDIA NIM client factories — OpenAI-compatible sync/async clients and LangChain adapter.
"""

from openai import AsyncOpenAI, OpenAI

from app.core.config import settings

_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def get_nvidia_client() -> OpenAI:
    """Return a synchronous OpenAI-compatible client pointed at NVIDIA NIM."""
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY chưa được thiết lập.")
    return OpenAI(base_url=_NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY)


def get_nvidia_async_client() -> AsyncOpenAI:
    """Return an asynchronous OpenAI-compatible client pointed at NVIDIA NIM."""
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY chưa được thiết lập.")
    return AsyncOpenAI(base_url=_NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY)


def get_langchain_nvidia(temperature: float = 0.2):
    """Return a LangChain ChatOpenAI model backed by NVIDIA NIM."""
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY chưa được thiết lập.")
    from langchain_openai import ChatOpenAI  # optional dependency

    return ChatOpenAI(
        model=settings.NVIDIA_MODEL,
        openai_api_key=settings.NVIDIA_API_KEY,
        openai_api_base=_NVIDIA_BASE_URL,
        temperature=temperature,
    )
