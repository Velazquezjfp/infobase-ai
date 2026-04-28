"""TC-S001-NFR-004-01 — subproject is gitignored.

After creating litellm/Dockerfile locally, git status must not list it and
git check-ignore must report the rule from .gitignore.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE = REPO_ROOT / "litellm" / "Dockerfile"


def test_litellm_dir_is_gitignored():
    """litellm/ appears in .gitignore."""
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore missing"
    lines = [l.strip() for l in gitignore.read_text().splitlines()]
    assert "litellm/" in lines, f"litellm/ not found in .gitignore; entries: {lines}"


def test_dockerfile_is_ignored_by_git():
    """git check-ignore exits 0 for litellm/Dockerfile."""
    assert DOCKERFILE.exists(), f"litellm/Dockerfile does not exist at {DOCKERFILE}"
    result = subprocess.run(
        ["git", "check-ignore", "-v", str(DOCKERFILE)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"git check-ignore returned {result.returncode} — "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    assert "litellm/" in result.stdout, (
        f"Expected 'litellm/' rule in git check-ignore output; got: {result.stdout!r}"
    )


def test_dockerfile_not_in_git_status():
    """git status --short does not list litellm/Dockerfile as tracked."""
    assert DOCKERFILE.exists(), f"litellm/Dockerfile does not exist at {DOCKERFILE}"
    result = subprocess.run(
        ["git", "status", "--short", str(DOCKERFILE)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git status failed: {result.stderr!r}"
    assert result.stdout.strip() == "", (
        f"litellm/Dockerfile appears in git status output: {result.stdout!r}. "
        "It should be ignored."
    )
