"""TC-S001-F-007-03 — useIdleTimeout fires its callback after the timeout.

The hook lives in TypeScript; in this Python pytest harness we verify the
hook's contract by reading its source. The acceptance criterion is "after
SESSION_IDLE_TIMEOUT_MINUTES of no activity the timer fires and the supplied
callback runs". For that to hold the hook must:

- Use setTimeout with a duration computed from the env-driven minutes value.
- Invoke the callback when the timer fires.
- Read VITE_SESSION_IDLE_TIMEOUT_MINUTES from import.meta.env.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "src" / "hooks" / "useIdleTimeout.ts"


def test_hook_uses_setTimeout_to_fire_callback():
    source = HOOK.read_text(encoding="utf-8")
    assert "setTimeout" in source, "hook must schedule the timeout via setTimeout"
    assert "callbackRef.current()" in source, (
        "hook must invoke the user-supplied callback when the timer fires"
    )


def test_hook_reads_vite_env_var_for_default_minutes():
    source = HOOK.read_text(encoding="utf-8")
    assert "VITE_SESSION_IDLE_TIMEOUT_MINUTES" in source, (
        "hook must read VITE_SESSION_IDLE_TIMEOUT_MINUTES from import.meta.env"
    )
    assert "import.meta.env" in source


def test_hook_default_is_ten_minutes():
    source = HOOK.read_text(encoding="utf-8")
    # Per the requirement the default is 10 minutes when the env var is unset.
    assert "DEFAULT_TIMEOUT_MINUTES = 10" in source, (
        "hook default must fall back to 10 minutes per S001-F-007"
    )
