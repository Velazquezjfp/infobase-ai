"""TC-S001-F-009-01 — single canonical Vite env-var name.

`VITE_API_URL` must be removed from `src/`; the only `VITE_API_BASE_URL`
declaration via `import.meta.env` should live in `src/lib/apiConfig.ts`.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"


def _walk_source_files() -> list[Path]:
    return [
        p
        for p in SRC_DIR.rglob("*")
        if p.is_file() and p.suffix in {".ts", ".tsx", ".js", ".jsx"}
    ]


def test_vite_api_url_is_gone():
    matches = []
    for path in _walk_source_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "VITE_API_URL" in line:
                matches.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
    assert not matches, "VITE_API_URL should be removed from src/, found:\n" + "\n".join(matches)


def test_vite_api_base_url_has_single_source_declaration():
    declarations = []
    for path in _walk_source_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "import.meta.env.VITE_API_BASE_URL" in line:
                declarations.append((path.relative_to(REPO_ROOT), lineno, line.strip()))

    assert len(declarations) == 1, (
        "expected exactly one import.meta.env.VITE_API_BASE_URL declaration, got:\n"
        + "\n".join(f"{p}:{ln}: {ln_text}" for p, ln, ln_text in declarations)
    )
    only = declarations[0]
    assert str(only[0]) == "src/lib/apiConfig.ts", (
        f"expected the declaration in src/lib/apiConfig.ts, got {only[0]}"
    )
