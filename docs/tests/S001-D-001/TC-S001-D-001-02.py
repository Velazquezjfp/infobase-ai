"""TC-S001-D-001-02: completeness — every variable named in the Description.

The Description of S001-D-001 enumerates 20 variable names across five
sections. The patched test case explicitly says: iterate over the list rather
than hard-coding a count, so the test stays correct if a future polish
changes which names are in scope.
"""

from __future__ import annotations

import re


# The explicit list, copied from the requirement Description (sections 1–5).
# Order matches the document. Total: 20 names.
EXPECTED_VARIABLES: tuple[str, ...] = (
    # Section 1: Registry & package sources
    "DOCKER_REGISTRY",
    "NPM_REGISTRY",
    "PIP_INDEX_URL",
    # Section 2: LLM backend
    "LLM_BACKEND",
    "LITELLM_PROXY_URL",
    "LITELLM_TOKEN",
    "LITELLM_MODEL",
    "ENABLE_OLLAMA_CONTAINER",
    "GEMINI_API_KEY",
    # Section 3: Feature flags
    "ENABLE_ANONYMIZATION",
    "ENABLE_DOCUMENT_SEARCH",
    "ENABLE_UPLOAD",
    # Section 4: Session lifecycle
    "SESSION_IDLE_TIMEOUT_MINUTES",
    # Section 5: Ports & paths
    "BACKEND_PORT",
    "FRONTEND_PORT",
    "DOCUMENTS_PATH",
    "LOG_LEVEL",
    "IDIRS_BASE_URL",
    "INIT_TEST_DOCS",
    "SKIP_INTEGRATION_TESTS",
)


def test_expected_list_has_20_names() -> None:
    """Sanity-check the test's own input — the Description says 20 names."""
    assert len(EXPECTED_VARIABLES) == 20
    assert len(set(EXPECTED_VARIABLES)) == 20  # no duplicates


def test_every_variable_is_defined_as_assignment(env_example_text: str) -> None:
    """Each name appears as a `KEY=` assignment, not just inside a comment."""
    missing: list[str] = []
    for name in EXPECTED_VARIABLES:
        pattern = re.compile(rf"^{re.escape(name)}=", re.MULTILINE)
        if not pattern.search(env_example_text):
            missing.append(name)
    assert not missing, f"missing assignments in .env.example: {missing}"


def test_no_duplicate_assignments(env_example_text: str) -> None:
    """A variable should only be assigned once; otherwise dotenv loaders pick the last one."""
    counts: dict[str, int] = {}
    for line in env_example_text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, _ = line.partition("=")
        if sep:
            counts[key] = counts.get(key, 0) + 1
    duplicates = {k: c for k, c in counts.items() if c > 1}
    assert not duplicates, f"duplicate assignments: {duplicates}"
