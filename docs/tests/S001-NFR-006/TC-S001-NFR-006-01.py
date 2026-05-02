"""
S001-NFR-006 TC-01 — `resolve_document_path()` unit tests.

Confirms the helper translates legacy `public/documents/<rest>` to
`${DOCUMENTS_BASE_PATH}/<rest>` and passes everything else through.
Four sub-cases: container path, already-absolute, host-dev, non-legacy relative.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


def _reload_config_with(monkeypatch: pytest.MonkeyPatch, documents_path: str):
    """Reload backend.config with a specific DOCUMENTS_PATH so DOCUMENTS_BASE_PATH picks it up."""
    monkeypatch.setenv("DOCUMENTS_PATH", documents_path)
    # Drop cached module so the top-level DOCUMENTS_BASE_PATH gets re-evaluated.
    sys.modules.pop("backend.config", None)
    return importlib.import_module("backend.config")


def test_legacy_prefix_resolves_to_container_base(monkeypatch):
    """Container scenario: `public/documents/x.pdf` → `/var/app/documents/x.pdf`."""
    cfg = _reload_config_with(monkeypatch, "/var/app/documents")
    result = cfg.resolve_document_path("public/documents/ACTE-2024-001/applications/Anmeldeformular.pdf")
    assert result == Path("/var/app/documents/ACTE-2024-001/applications/Anmeldeformular.pdf"), (
        f"Container scenario failed: got {result!r}"
    )


def test_already_absolute_path_passes_through(monkeypatch):
    """Already-absolute container path: returned unchanged."""
    cfg = _reload_config_with(monkeypatch, "/var/app/documents")
    result = cfg.resolve_document_path("/var/app/documents/ACTE-2024-001/applications/Anmeldeformular.pdf")
    assert result == Path("/var/app/documents/ACTE-2024-001/applications/Anmeldeformular.pdf"), (
        f"Absolute pass-through failed: got {result!r}"
    )


def test_host_dev_translation_is_noop(monkeypatch):
    """Host-dev scenario (DOCUMENTS_BASE_PATH=='public/documents'): translation is a no-op."""
    cfg = _reload_config_with(monkeypatch, "public/documents")
    result = cfg.resolve_document_path("public/documents/x.pdf")
    assert result == Path("public/documents/x.pdf"), (
        f"Host-dev no-op failed: got {result!r}"
    )


def test_non_legacy_relative_passes_through(monkeypatch):
    """Non-legacy relative path (e.g. `root_docs/x.pdf`): returned unchanged."""
    cfg = _reload_config_with(monkeypatch, "/var/app/documents")
    result = cfg.resolve_document_path("root_docs/Anmeldeformular.pdf")
    assert result == Path("root_docs/Anmeldeformular.pdf"), (
        f"Non-legacy relative pass-through failed: got {result!r}"
    )
