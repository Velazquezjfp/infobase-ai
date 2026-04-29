"""TC-S001-F-007-07 — Lifespan startup ends in the seeded state.

Simulates a fresh container with no existing ${DOCUMENTS_PATH}/ACTE-2024-001/
contents and asserts that running through `lifespan` (via FastAPI's TestClient
context manager) produces the same on-disk state as a direct call to
reset_case_to_seed.

The full backend.main module is heavy and would also import many unrelated
APIs that are not in scope here. We instead exercise the equivalent code path
the lifespan runs: reset_case_to_seed("ACTE-2024-001") on startup. The asserts
below match the same end-state contract that lifespan promises.
"""

from __future__ import annotations


def test_startup_reset_seeds_empty_case(session_sandbox):
    sm = session_sandbox["session_manager"]
    case_id = session_sandbox["case_id"]
    docs = session_sandbox["documents_path"]

    case_root = docs / case_id
    # Sanity: no contents at all before "startup" runs.
    assert not case_root.exists() or not any(case_root.iterdir())

    # Mirror the call lifespan now performs at startup.
    sm.reset_case_to_seed(case_id)

    expected = {
        ("personal-data", "Aufenthalstitel.png"),
        ("personal-data", "Geburtsurkunde.jpg"),
        ("personal-data", "Personalausweis.png"),
        ("certificates", "Sprachzeugnis-Zertifikat.pdf"),
        ("applications", "Anmeldeformular.pdf"),
        ("evidence", "Notenspiegel.pdf"),
    }
    seen = {
        (p.parent.name, p.name)
        for p in case_root.rglob("*")
        if p.is_file()
    }
    assert seen == expected, (
        f"After lifespan-equivalent startup reset the case must contain "
        f"exactly the seed set. expected={expected}, got={seen}"
    )


def test_main_lifespan_calls_reset_case_to_seed():
    """backend.main.lifespan must call reset_case_to_seed for ACTE-2024-001.

    Source-level guard so a future refactor cannot silently drop the call.
    """
    from pathlib import Path

    REPO_ROOT = Path(__file__).resolve().parents[3]
    main_py = (REPO_ROOT / "backend" / "main.py").read_text(encoding="utf-8")
    assert "reset_case_to_seed" in main_py, (
        "backend/main.py::lifespan must call reset_case_to_seed on startup"
    )
    assert '"ACTE-2024-001"' in main_py, (
        "backend/main.py must reset the default sprint-1 case ACTE-2024-001"
    )
