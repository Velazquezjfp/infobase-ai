"""TC-S001-NFR-004-10 — env cutover.

Verifies the post-NFR-004 state of .env.example:
- LLM_BACKEND=internal (was external)
- LITELLM_PROXY_URL=http://localhost:4000 (already set in wave 1)
- All # 🔒 markers preserved
- All # introduced by S001- tags preserved
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_EXAMPLE = REPO_ROOT / ".env.example"


def _parse_env_values(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def test_llm_backend_is_internal():
    """LLM_BACKEND defaults to internal after env cutover."""
    content = ENV_EXAMPLE.read_text()
    values = _parse_env_values(content)
    assert values.get("LLM_BACKEND") == "internal", (
        f"Expected LLM_BACKEND=internal, got: {values.get('LLM_BACKEND')!r}"
    )


def test_litellm_proxy_url_is_set():
    """LITELLM_PROXY_URL is http://localhost:4000."""
    content = ENV_EXAMPLE.read_text()
    values = _parse_env_values(content)
    assert values.get("LITELLM_PROXY_URL") == "http://localhost:4000", (
        f"Expected LITELLM_PROXY_URL=http://localhost:4000, got: {values.get('LITELLM_PROXY_URL')!r}"
    )


def test_lock_markers_preserved():
    """# 🔒 markers are present in .env.example."""
    content = ENV_EXAMPLE.read_text()
    assert "# 🔒" in content, "# 🔒 markers must be preserved in .env.example"


def test_introduced_by_tags_preserved():
    """# introduced by S001- tags are present in .env.example."""
    content = ENV_EXAMPLE.read_text()
    assert "# introduced by S001-" in content, (
        "# introduced by S001- tags must be preserved in .env.example"
    )
