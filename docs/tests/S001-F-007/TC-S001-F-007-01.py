"""TC-S001-F-007-01 — Logout-equivalent reset wipes anonymized renders.

Acceptance criterion exercised: after the user "logs out" (i.e. the backend's
reset_case_to_seed runs), the personal-data folder contains exactly the three
seed files and no `__anonymized` renders.
"""

from __future__ import annotations


def test_logout_reset_clears_anonymized_renders(session_sandbox):
    sm = session_sandbox["session_manager"]
    case_id = session_sandbox["case_id"]
    docs = session_sandbox["documents_path"]

    # Pre-populate the personal-data folder with junk that should be wiped:
    # an extra anonymized render and an unrelated file.
    personal_data = docs / case_id / "personal-data"
    personal_data.mkdir(parents=True, exist_ok=True)
    (personal_data / "Personalausweis__anonymized.png").write_bytes(b"anon")
    (personal_data / "junk.txt").write_bytes(b"junk")

    sm.reset_case_to_seed(case_id)

    files = sorted(p.name for p in personal_data.iterdir() if p.is_file())
    assert files == sorted([
        "Aufenthalstitel.png",
        "Geburtsurkunde.jpg",
        "Personalausweis.png",
    ]), f"Unexpected personal-data contents after reset: {files}"

    # Defensive: ensure no render-suffix file remains anywhere under the case.
    case_root = docs / case_id
    leftover_renders = [
        p.name for p in case_root.rglob("*")
        if p.is_file() and ("__anonymized" in p.name or "_translated_" in p.name)
    ]
    assert leftover_renders == [], (
        f"Reset should remove all render artifacts; found: {leftover_renders}"
    )
