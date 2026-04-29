"""Shared fixtures for S001-F-007 tests.

Sets up a sandboxed environment so the seed-reset logic operates on temp
directories instead of the live project state. The real `root_docs/` and
`backend/data/contexts/templates/` trees are copied into the sandbox; the
case dir, documents path and manifest live entirely in the sandbox.
"""

from __future__ import annotations

import importlib
import shutil
import sys
from pathlib import Path
from typing import Iterator

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


_RESET_MODULES = [
    "backend.config",
    "backend.services.session_manager",
    "backend.services.document_registry",
    "backend.api.session",
]


@pytest.fixture
def session_sandbox(monkeypatch, tmp_path) -> Iterator[dict]:
    """Build an isolated copy of the assets needed by reset_case_to_seed.

    Yields a dict with:
        - documents_path: Path to the sandbox's documents dir
        - cases_dir: Path to the sandbox's contexts/cases dir
        - templates_dir: Path to the sandbox's contexts/templates dir
        - root_docs_dir: Path to the sandbox's root_docs dir
        - manifest_path: Path to the sandbox's manifest file
        - case_id: The default case id seeded ("ACTE-2024-001")
        - session_manager: freshly imported module bound to the sandbox
    """
    # 1. Copy real templates + root_docs into the sandbox so we don't depend on
    #    fragile cwd state.
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    real_templates = REPO_ROOT / "backend" / "data" / "contexts" / "templates"
    real_root_docs = REPO_ROOT / "root_docs"

    sandbox_templates = sandbox / "templates"
    sandbox_root_docs = sandbox / "root_docs"
    shutil.copytree(real_templates, sandbox_templates)
    # root_docs has a few binary files; copy only the six the mapping needs to
    # keep tests independent of unrelated additions to root_docs/.
    sandbox_root_docs.mkdir()
    for fname in [
        "Aufenthalstitel.png",
        "Geburtsurkunde.jpg",
        "Personalausweis.png",
        "Sprachzeugnis-Zertifikat.pdf",
        "Anmeldeformular.pdf",
        "Notenspiegel.pdf",
    ]:
        src = real_root_docs / fname
        if src.exists():
            shutil.copy2(src, sandbox_root_docs / fname)
        else:
            # Last-resort placeholder so tests can still exercise the path
            # logic when the binary asset is missing locally.
            (sandbox_root_docs / fname).write_bytes(b"placeholder")

    sandbox_cases = sandbox / "cases"
    sandbox_cases.mkdir()
    sandbox_documents = sandbox / "documents"
    sandbox_documents.mkdir()
    sandbox_manifest = sandbox / "data" / "document_manifest.json"
    sandbox_manifest.parent.mkdir(parents=True, exist_ok=True)

    # 2. Force the doc-storage env var before re-importing so backend.config
    #    picks it up and DOCUMENTS_BASE_PATH points at the sandbox.
    monkeypatch.setenv("DOCUMENTS_PATH", str(sandbox_documents))

    for mod in _RESET_MODULES:
        sys.modules.pop(mod, None)

    config_mod = importlib.import_module("backend.config")
    document_registry = importlib.import_module("backend.services.document_registry")
    session_manager = importlib.import_module("backend.services.session_manager")

    # 3. Redirect every path the session manager reaches for at runtime to the
    #    sandbox copies.
    monkeypatch.setattr(session_manager, "ROOT_DOCS_DIR", sandbox_root_docs)
    monkeypatch.setattr(session_manager, "CASES_DIR", sandbox_cases)
    monkeypatch.setattr(session_manager, "TEMPLATES_DIR", sandbox_templates)
    monkeypatch.setattr(session_manager, "DOCUMENTS_BASE_PATH", str(sandbox_documents))
    monkeypatch.setattr(document_registry, "MANIFEST_PATH", sandbox_manifest)

    case_id = "ACTE-2024-001"

    yield {
        "documents_path": sandbox_documents,
        "cases_dir": sandbox_cases,
        "templates_dir": sandbox_templates,
        "root_docs_dir": sandbox_root_docs,
        "manifest_path": sandbox_manifest,
        "case_id": case_id,
        "session_manager": session_manager,
        "document_registry": document_registry,
        "config": config_mod,
    }
