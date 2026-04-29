"""TC-S001-F-007-04 — useIdleTimeout resets its timer on user activity.

Verifies the source-level contract that a tracked DOM event clears the running
setTimeout and schedules a fresh one (so a `mousemove` at t=30s does not lead
to a logout at t=61s).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "src" / "hooks" / "useIdleTimeout.ts"


def test_hook_listens_for_required_activity_events():
    source = HOOK.read_text(encoding="utf-8")
    for event in ("mousemove", "keydown", "scroll", "click"):
        assert f"'{event}'" in source, (
            f"hook must register a listener for the '{event}' DOM event"
        )


def test_activity_listener_triggers_resetTimer():
    source = HOOK.read_text(encoding="utf-8")
    # The hook must register the activity events with the resetTimer handler.
    assert "addEventListener(event, resetTimer" in source, (
        "activity events must be wired to resetTimer so each event restarts "
        "the idle countdown"
    )


def _extract_arrow_function_body(source: str, declaration: str) -> str:
    """Return the {...} body that follows ``declaration`` in ``source``.

    Walks braces so nested blocks (e.g. an inner ``if {...}``) don't terminate
    the match early — re's ``[^}]*`` pattern can't handle nesting.
    """
    idx = source.index(declaration)
    brace_start = source.index("{", idx)
    depth = 0
    for i in range(brace_start, len(source)):
        c = source[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start: i + 1]
    raise AssertionError(f"unbalanced braces after {declaration!r}")


def test_resetTimer_clears_running_timeout_before_rescheduling():
    source = HOOK.read_text(encoding="utf-8")
    body = _extract_arrow_function_body(source, "const resetTimer")
    assert "clearTimeout(timerId)" in body, (
        "resetTimer must call clearTimeout on the previous timer before "
        "scheduling a new one — otherwise activity does not actually reset"
    )
    assert "setTimeout(fireTimeout" in body, (
        "resetTimer must reschedule via setTimeout(fireTimeout, ...)"
    )
