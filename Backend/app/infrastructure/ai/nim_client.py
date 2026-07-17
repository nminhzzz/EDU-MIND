"""
AI client factories — OpenAI-compatible sync/async clients and LangChain adapter.

The provider (base URL, model, API key) is fully controlled by .env so that
switching between NVIDIA NIM, cline-pass, OpenRouter, or any other
OpenAI-compatible gateway requires zero code changes.

Response normalisation
----------------------
Some gateways (e.g. cline-pass / api.cline.bot) wrap the OpenAI payload in a
``data`` sub-field instead of placing it at root level:

    { "choices": null, "data": { "choices": [...], ... }, "success": true }

``ClinePassChatOpenAI`` subclasses LangChain's ``ChatOpenAI`` and overrides
``_create_chat_result`` to unwrap ``data`` before the base class inspects the
``choices`` field.  All other behaviour (structured output, streaming, tool
calling, retries) is unchanged.
"""

import openai
from openai import AsyncOpenAI, OpenAI

from app.core.config import settings


# ---------------------------------------------------------------------------
# LangChain adapter with response-normalisation
# ---------------------------------------------------------------------------


class _ClinePassChatOpenAI:
    """
    Lazy-import wrapper that subclasses ``langchain_openai.ChatOpenAI``.

    Defined as a factory function (``_make_chat_class``) to avoid importing
    LangChain at module load time, keeping the container start-up fast when
    LangChain is an optional dependency.
    """


def _make_langchain_class():
    """Build and return a ChatOpenAI subclass that handles gateway-wrapped responses."""
    from langchain_openai import ChatOpenAI

    class _NormalisedChatOpenAI(ChatOpenAI):
        """
        ChatOpenAI subclass that normalises cline-pass (and similar gateways)
        response format before the base class parses ``choices``.

        cline-pass returns:
            { "choices": null, "data": { "choices": [...], ... }, "success": true }

        We detect the wrapped layout and promote ``data`` to root level before
        calling ``super()._create_chat_result()``.
        """

        def _create_chat_result(
            self,
            response: "dict | openai.BaseModel",
            generation_info: "dict | None" = None,
        ):
            # Normalise to dict for uniform inspection
            if isinstance(response, dict):
                resp_dict = response
            else:
                resp_dict = response.model_dump(
                    exclude={"choices": {"__all__": {"message": {"parsed"}}}},
                    warnings=False,
                )

            # Unwrap cline-pass ``data`` wrapper when root choices is null
            if resp_dict.get("choices") is None:
                data = resp_dict.get("data")
                if isinstance(data, dict) and data.get("choices"):
                    merged = {**resp_dict, **data}
                    merged.pop("data", None)
                    merged.pop("success", None)
                    resp_dict = merged

            return super()._create_chat_result(resp_dict, generation_info)

    return _NormalisedChatOpenAI


# ---------------------------------------------------------------------------
# Client factories
# ---------------------------------------------------------------------------


def get_deepseek_client() -> OpenAI:
    """Return a synchronous OpenAI-compatible client for the configured AI provider."""
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY chưa được thiết lập.")
    return OpenAI(base_url=settings.AI_BASE_URL, api_key=settings.DEEPSEEK_API_KEY)


def get_deepseek_async_client() -> AsyncOpenAI:
    """Return an async OpenAI-compatible client for the configured AI provider."""
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY chưa được thiết lập.")
    return AsyncOpenAI(base_url=settings.AI_BASE_URL, api_key=settings.DEEPSEEK_API_KEY)


def get_langchain_deepseek(temperature: float = 0.2, **kwargs):
    """
    Return a LangChain ChatOpenAI model backed by the configured AI provider.

    Uses ``_NormalisedChatOpenAI`` which transparently handles gateway-specific
    response wrapping (e.g. cline-pass) without affecting any other behaviour.
    """
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY chưa được thiết lập.")

    NormalisedChatOpenAI = _make_langchain_class()

    return NormalisedChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.AI_BASE_URL,
        temperature=temperature,
        **kwargs,
    )
