"""TC-S001-D-001-05: cross-reference — every `# introduced by S001-...` tag
maps to a polished requirement file in `docs/requirements/sprint-001/`.
"""

from __future__ import annotations

import re
from pathlib import Path


INTRO_RE = re.compile(r"#\s*introduced\s+by\s+(S001-[A-Z]+-\d{3})")


def _sprint_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "requirements" / "sprint-001"


def test_at_least_one_introduced_by_tag(env_example_text: str) -> None:
    """If no tags exist, the cross-reference test below is meaningless."""
    assert INTRO_RE.search(env_example_text), (
        "no `# introduced by S001-...` tags found in .env.example"
    )


def test_every_tag_resolves_to_polished_requirement(env_example_text: str, repo_root: Path) -> None:
    sprint_dir = _sprint_dir(repo_root)
    assert sprint_dir.is_dir(), f"sprint dir missing: {sprint_dir}"

    referenced_ids = sorted({m.group(1) for m in INTRO_RE.finditer(env_example_text)})
    assert referenced_ids, "no S001-... tags found"

    missing: list[str] = []
    for req_id in referenced_ids:
        req_file = sprint_dir / f"{req_id}.md"
        if not req_file.is_file():
            missing.append(req_id)
    assert not missing, (
        f".env.example references requirement IDs that have no file in {sprint_dir}: {missing}"
    )


def test_every_assignment_has_an_introduced_by_tag(env_example_text: str) -> None:
    """Each KEY= assignment must be preceded (within its block) by an `introduced by` tag.

    Walk the file line by line, resetting the "current tag" at each blank line.
    Every assignment must see a tag in its current block.
    """
    untagged: list[str] = []
    current_tag: str | None = None

    for raw in env_example_text.splitlines():
        line = raw.rstrip()

        if not line.strip():
            current_tag = None
            continue

        m = INTRO_RE.search(line)
        if m:
            current_tag = m.group(1)
            continue

        # KEY=VALUE assignment line
        if re.match(r"^[A-Z][A-Z0-9_]*=", line):
            if current_tag is None:
                key = line.split("=", 1)[0]
                untagged.append(key)

    assert not untagged, (
        f"these assignments have no preceding `# introduced by S001-...` tag in their block: {untagged}"
    )
