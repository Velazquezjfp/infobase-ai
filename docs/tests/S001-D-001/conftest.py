"""Shared fixtures for S001-D-001 tests."""

from pathlib import Path

import pytest


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / ".env.example").exists() and (parent / "backend").is_dir():
            return parent
    raise RuntimeError("could not locate repo root containing .env.example")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return _find_repo_root()


@pytest.fixture(scope="session")
def env_example_path(repo_root: Path) -> Path:
    return repo_root / ".env.example"


@pytest.fixture(scope="session")
def env_example_text(env_example_path: Path) -> str:
    return env_example_path.read_text(encoding="utf-8")
