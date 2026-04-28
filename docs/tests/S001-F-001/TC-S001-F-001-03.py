"""TC-S001-F-001-03 — config error.

LLM_BACKEND=foobar must cause llm_provider.get_provider() to raise ValueError.
The requirement specifies "import time" failure: the failure happens on the
first call to get_provider(), which is what main.py / chat.py / admin.py
trigger at startup. uvicorn would surface that ValueError before binding
to a port.
"""

from __future__ import annotations

import pytest


def test_invalid_llm_backend_raises(fresh_modules):
    _config, llm_provider = fresh_modules({
        "LLM_BACKEND": "foobar",
    })

    with pytest.raises(ValueError) as excinfo:
        llm_provider.get_provider()

    msg = str(excinfo.value)
    assert "foobar" in msg or "LLM_BACKEND" in msg, msg
    assert "internal" in msg and "external" in msg, msg
