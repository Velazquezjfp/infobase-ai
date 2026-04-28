"""TC-S001-D-001-01: happy path — .env.example is copy-able and consumable.

The "happy path" in the requirement is: copy `.env.example` to `.env`, start
backend and frontend, both come up without complaining about missing env vars
(other than the documented `GEMINI_API_KEY` requirement).

Spinning up real uvicorn and Vite servers inside a unit test is heavy and
non-deterministic, so this test verifies the precondition for that flow:

  1. `.env.example` exists at the repo root.
  2. It is plain UTF-8 text (so `cp .env.example .env` produces a usable file).
  3. Every non-comment, non-blank line is a valid `KEY=VALUE` assignment that
     a POSIX shell, Python `python-dotenv`, and Vite's loader will all accept.
  4. The keys used by `backend/config.py` are present (so the backend will not
     fall back to hard-coded values when started against a copy of this file).
"""

from __future__ import annotations

import re
from pathlib import Path


KEY_LINE = re.compile(r"^[A-Z][A-Z0-9_]*=.*$")
BACKEND_REQUIRED_KEYS = {
    "LOG_LEVEL",
    "DOCUMENTS_PATH",
    "GEMINI_API_KEY",
    "IDIRS_BASE_URL",
    "INIT_TEST_DOCS",
    "SKIP_INTEGRATION_TESTS",
}


def _parse(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        assert KEY_LINE.match(line), f"non-comment line is not a KEY=VALUE: {raw!r}"
        key, _, value = line.partition("=")
        pairs[key] = value
    return pairs


def test_env_example_exists(env_example_path: Path) -> None:
    assert env_example_path.is_file(), f"missing {env_example_path}"


def test_env_example_is_utf8(env_example_path: Path) -> None:
    env_example_path.read_text(encoding="utf-8")


def test_every_non_comment_line_is_keyvalue(env_example_text: str) -> None:
    parsed = _parse(env_example_text)
    assert parsed, "no KEY=VALUE entries found"


def test_backend_config_keys_present(env_example_text: str) -> None:
    parsed = _parse(env_example_text)
    missing = BACKEND_REQUIRED_KEYS - parsed.keys()
    assert not missing, f"backend/config.py keys missing from .env.example: {sorted(missing)}"
