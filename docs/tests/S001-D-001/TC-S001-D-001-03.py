"""TC-S001-D-001-03: no leakage — no real secrets or non-public hosts.

Spec text (verbatim): "grep the file for `AIza`, `sk-`, real API key prefixes,
and any host that is not `localhost` or a public registry; the result is empty."
"""

from __future__ import annotations

import re


# Common API-key prefixes that should NEVER appear in a checked-in template.
# - AIza... : Google API keys (Gemini, Maps, Firebase, etc.)
# - sk-...  : OpenAI / Anthropic / many other "sk-" prefixed secret keys
# - ghp_... : GitHub personal access tokens
# - xox[abp]-... : Slack tokens
# - AKIA... : AWS access key IDs
SECRET_PREFIX_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[abpr]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}"),
)

# Hosts considered safe to appear in a public template.
ALLOWED_HOST_SUBSTRINGS: tuple[str, ...] = (
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "registry.npmjs.org",
    "pypi.org",
    "docker.io",
    "ghcr.io",
    "registry-1.docker.io",
)

# Recognise URLs in any context (including inside comments) so we catch a
# real Artifactory URL even if someone forgot to remove it from a comment.
URL_RE = re.compile(r"https?://([A-Za-z0-9.\-]+)(?::\d+)?(?:/[^\s]*)?")


def test_no_known_secret_prefixes(env_example_text: str) -> None:
    hits: list[tuple[str, str]] = []
    for pattern in SECRET_PREFIX_PATTERNS:
        for match in pattern.finditer(env_example_text):
            hits.append((pattern.pattern, match.group(0)))
    assert not hits, f"likely secret values found in .env.example: {hits}"


def test_only_allowed_hosts_in_urls(env_example_text: str) -> None:
    bad: list[str] = []
    for match in URL_RE.finditer(env_example_text):
        host = match.group(1).lower()
        if not any(allowed in host for allowed in ALLOWED_HOST_SUBSTRINGS):
            bad.append(host)
    assert not bad, (
        f"non-public, non-localhost hosts found in .env.example: {sorted(set(bad))}. "
        f"Replace with placeholder or one of {ALLOWED_HOST_SUBSTRINGS}."
    )


def test_sensitive_values_use_placeholder(env_example_text: str) -> None:
    """Sensitive vars must hold a placeholder, not anything that looks like a real value."""
    sensitive_keys = ("GEMINI_API_KEY", "LITELLM_TOKEN")
    placeholder_tokens = ("replace-me", "changeme", "your-", "example", "<", "(required)")
    for key in sensitive_keys:
        m = re.search(rf"^{re.escape(key)}=(.*)$", env_example_text, flags=re.MULTILINE)
        assert m, f"{key} is not assigned in .env.example"
        value = m.group(1).strip().strip('"').strip("'")
        assert any(tok in value.lower() for tok in (t.lower() for t in placeholder_tokens)), (
            f"{key} value {value!r} does not look like a placeholder"
        )
