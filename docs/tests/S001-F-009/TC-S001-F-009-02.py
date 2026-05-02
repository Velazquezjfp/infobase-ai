"""TC-S001-F-009-02 — frontend modules route via the canonical helper.

Every frontend module that previously read `VITE_API_URL` (or its own copy of
the constant) must now reference `API_BASE_URL` imported from `@/lib/apiConfig`.

This is a static guarantee that the runtime value of every backend-targeting
fetch() resolves to the same source — i.e. a single
`VITE_API_BASE_URL=http://localhost:8000` value drives every call.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"


REQUIRED_IMPORTERS = [
    "src/components/workspace/AdminConfigPanel.tsx",
    "src/components/workspace/AIChatInterface.tsx",
    "src/components/workspace/CaseContextDialog.tsx",
    "src/components/workspace/CaseTreeExplorer.tsx",
    "src/components/workspace/ContextHierarchyDialog.tsx",
    "src/components/workspace/SubmitCaseDialog.tsx",
    "src/components/workspace/DocumentViewer.tsx",
    "src/lib/adminApi.ts",
    "src/lib/fileApi.ts",
    "src/contexts/AppContext.tsx",
]


_IMPORT_RE = re.compile(
    r"""import\s*\{[^}]*\bAPI_BASE_URL\b[^}]*\}\s*from\s*['"](?:@/lib/apiConfig|\./apiConfig|\.\./lib/apiConfig)['"]"""
)


def test_all_consumers_import_api_base_url_from_apiconfig():
    missing = []
    for rel in REQUIRED_IMPORTERS:
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        if not _IMPORT_RE.search(text):
            missing.append(rel)
    assert not missing, "modules missing API_BASE_URL import from apiConfig:\n" + "\n".join(missing)


def test_no_local_api_base_url_constant_definitions():
    """The `const API_BASE_URL = ...` pattern must not coexist with the import.

    A re-introduction of the inline constant would be a regression.
    """
    offenders = []
    bad = re.compile(r"const\s+API_BASE_URL\s*=\s*import\.meta\.env")
    for path in SRC_DIR.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        if path.name == "apiConfig.ts":
            continue
        if bad.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, "stray inline API_BASE_URL constants:\n" + "\n".join(offenders)


def test_apiconfig_default_matches_documented_fallback():
    text = (REPO_ROOT / "src/lib/apiConfig.ts").read_text(encoding="utf-8")
    assert "http://localhost:8000" in text, "apiConfig.ts must keep the documented dev fallback"
