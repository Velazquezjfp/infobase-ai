"""
LLM provider abstraction for BAMF ACTE Companion.

This module decouples the application from any specific LLM SDK by exposing a
single async interface (LLMProvider) and dispatching to one concrete
implementation chosen at process start via the LLM_BACKEND environment
variable:

- LLM_BACKEND=internal (default): LiteLLMProvider, talking to a self-hosted
  LiteLLM proxy via the OpenAI-compatible /chat/completions endpoint. This is
  the only supported path in the closed-environment deployment.
- LLM_BACKEND=external: GeminiProvider, wrapping google.generativeai. Provided
  as a developer opt-in for environments that can reach the public Gemini API.

Exclusivity is the contract: get_provider() reads LLM_BACKEND once, returns a
cached singleton, and never falls back from one backend to the other. Unknown
LLM_BACKEND values raise ValueError at import time on the first get_provider()
call.

Note: google.generativeai is imported lazily inside GeminiProvider.__init__ so
that the internal/LiteLLM path never pulls the Google SDK into sys.modules.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional

from backend.config import (
    GEMINI_API_KEY,
    LITELLM_MODEL,
    LITELLM_PROXY_URL,
    LITELLM_TOKEN,
    LLM_BACKEND,
)

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class every concrete LLM provider must implement.

    Implementations translate the kwargs (temperature, top_p, top_k,
    max_output_tokens) into whatever the underlying SDK expects.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Return the full completion text for a single-prompt request."""

    @abstractmethod
    async def generate_streaming(
        self, prompt: str, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Yield text chunks as they arrive from the model."""

    @abstractmethod
    def is_initialized(self) -> bool:
        """Return True when the provider has the configuration it needs."""


class LiteLLMProvider(LLMProvider):
    """Routes calls through a LiteLLM proxy via the OpenAI-compatible API.

    The proxy is configured via LITELLM_PROXY_URL / LITELLM_TOKEN and the
    underlying model via LITELLM_MODEL. This provider never imports or
    contacts google.generativeai.
    """

    def __init__(self) -> None:
        if not LITELLM_PROXY_URL:
            logger.warning(
                "LiteLLMProvider instantiated without LITELLM_PROXY_URL set; "
                "is_initialized() will return False"
            )
        self._proxy_url = LITELLM_PROXY_URL
        self._token = LITELLM_TOKEN
        self._model = LITELLM_MODEL
        # The "openai/" prefix tells LiteLLM to use its OpenAI-compatible
        # transport against the given api_base, regardless of the real
        # underlying engine (Ollama, vLLM, etc.) sitting behind the proxy.
        self._litellm_model = f"openai/{self._model}" if self._model else None
        logger.info(
            "LiteLLMProvider configured: model=%s, proxy=%s",
            self._model,
            self._proxy_url,
        )

    def is_initialized(self) -> bool:
        return bool(self._proxy_url and self._model)

    @staticmethod
    def _map_kwargs(kwargs: dict) -> dict:
        """Translate the provider-neutral kwargs to OpenAI/LiteLLM keys."""
        mapped: dict = {}
        if "temperature" in kwargs:
            mapped["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            mapped["top_p"] = kwargs["top_p"]
        # top_k is silently dropped — not a standard OpenAI parameter and
        # LiteLLM rejects unknown kwargs for some providers.
        if "max_output_tokens" in kwargs:
            mapped["max_tokens"] = kwargs["max_output_tokens"]
        elif "max_tokens" in kwargs:
            mapped["max_tokens"] = kwargs["max_tokens"]
        return mapped

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        import litellm

        params = self._map_kwargs(kwargs)
        response = await litellm.acompletion(
            model=self._litellm_model,
            api_base=self._proxy_url,
            api_key=self._token or "sk-no-key",
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        # OpenAI-shape response: choices[0].message.content
        return response["choices"][0]["message"]["content"] or ""

    async def generate_streaming(
        self, prompt: str, **kwargs: Any
    ) -> AsyncIterator[str]:
        import litellm

        params = self._map_kwargs(kwargs)
        stream = await litellm.acompletion(
            model=self._litellm_model,
            api_base=self._proxy_url,
            api_key=self._token or "sk-no-key",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **params,
        )
        async for chunk in stream:
            try:
                delta = chunk["choices"][0]["delta"]
            except (KeyError, IndexError, TypeError):
                continue
            content = delta.get("content") if isinstance(delta, dict) else getattr(delta, "content", None)
            if content:
                yield content


class GeminiProvider(LLMProvider):
    """Wraps google.generativeai. Imported lazily so the internal path stays
    free of any Google dependency in sys.modules.
    """

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            logger.error("GeminiProvider requires GEMINI_API_KEY")
            raise ValueError("GEMINI_API_KEY not configured for external backend")

        # Lazy imports keep google.generativeai out of sys.modules on the
        # internal path.
        import google.generativeai as genai
        from google.generativeai.types import GenerationConfig

        self._genai = genai
        self._GenerationConfig = GenerationConfig
        genai.configure(api_key=GEMINI_API_KEY)
        self._model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("GeminiProvider configured: model=gemini-2.5-flash")

    def is_initialized(self) -> bool:
        return self._model is not None

    def _build_config(self, kwargs: dict):
        return self._GenerationConfig(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.8),
            top_k=kwargs.get("top_k", 40),
            max_output_tokens=kwargs.get("max_output_tokens", 2048),
        )

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        config = self._build_config(kwargs)
        # google.generativeai's generate_content is synchronous; that's fine
        # here because higher layers already run inside FastAPI's worker
        # threads. Awaiting a sync call would be the wrong fix.
        response = self._model.generate_content(prompt, generation_config=config)
        return response.text or ""

    async def generate_streaming(
        self, prompt: str, **kwargs: Any
    ) -> AsyncIterator[str]:
        config = self._build_config(kwargs)
        stream = self._model.generate_content(
            prompt, generation_config=config, stream=True
        )
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text


_provider_singleton: Optional[LLMProvider] = None


def _build_provider() -> LLMProvider:
    backend = (LLM_BACKEND or "internal").strip().lower()
    if backend == "internal":
        if not LITELLM_PROXY_URL or not LITELLM_PROXY_URL.strip():
            raise ValueError(
                "LITELLM_PROXY_URL is required when LLM_BACKEND=internal — "
                "start the LiteLLM container per S001-NFR-004 or set LLM_BACKEND=external"
            )
        return LiteLLMProvider()
    if backend == "external":
        return GeminiProvider()
    raise ValueError(
        f"Invalid LLM_BACKEND={backend!r}; expected 'internal' or 'external'"
    )


def get_provider() -> LLMProvider:
    """Return the process-wide LLM provider, instantiating once.

    The choice of provider is locked in on the first call. Re-reading
    LLM_BACKEND mid-process is not supported by design; restart the app to
    change backends.
    """
    global _provider_singleton
    if _provider_singleton is None:
        _provider_singleton = _build_provider()
    return _provider_singleton


def reset_provider_for_tests() -> None:
    """Clear the cached singleton. Tests use this between scenarios."""
    global _provider_singleton
    _provider_singleton = None
