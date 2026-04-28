"""TC-S001-NFR-004-09 — fail-fast on missing LITELLM_PROXY_URL.

When LLM_BACKEND=internal and LITELLM_PROXY_URL is empty/blank, get_provider()
must raise ValueError before any HTTP attempt. The message must contain both
'LITELLM_PROXY_URL' and 'S001-NFR-004'.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.parametrize("url_value", ["", "   "])
def test_fail_fast_raises_value_error(fresh_modules, url_value):
    """get_provider() raises ValueError when LITELLM_PROXY_URL is empty."""
    _config, llm_provider = fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": url_value,
    })

    sentinel = AsyncMock(side_effect=AssertionError("litellm.acompletion must not be called"))
    with patch("litellm.acompletion", sentinel):
        with pytest.raises(ValueError) as exc_info:
            llm_provider.get_provider()

    msg = str(exc_info.value)
    assert "LITELLM_PROXY_URL" in msg, f"Message must mention LITELLM_PROXY_URL; got: {msg!r}"
    assert "S001-NFR-004" in msg, f"Message must mention S001-NFR-004; got: {msg!r}"
    sentinel.assert_not_called()


def test_fail_fast_not_triggered_when_url_set(fresh_modules):
    """get_provider() does NOT raise when LITELLM_PROXY_URL is set."""
    _config, llm_provider = fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://localhost:4000",
        "LITELLM_TOKEN": "sk-test",
        "LITELLM_MODEL": "gemma3:12b",
    })
    provider = llm_provider.get_provider()
    assert provider is not None
    assert provider.is_initialized()
