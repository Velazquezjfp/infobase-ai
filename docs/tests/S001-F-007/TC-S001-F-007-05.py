"""TC-S001-F-007-05 — Evidence folder is seeded with Notenspiegel.pdf.

Per the sprint-1 root_docs mapping, Notenspiegel.pdf lives in the evidence
folder (replacing the deprecated "Additional information" folder concept).
"""

from __future__ import annotations


def test_evidence_folder_contains_notenspiegel_after_reset(session_sandbox):
    sm = session_sandbox["session_manager"]
    case_id = session_sandbox["case_id"]
    docs = session_sandbox["documents_path"]

    sm.reset_case_to_seed(case_id)

    evidence = docs / case_id / "evidence" / "Notenspiegel.pdf"
    assert evidence.exists(), (
        f"Notenspiegel.pdf must be seeded into evidence/ after reset; "
        f"path checked: {evidence}"
    )
    # The seed copy should be non-empty (at minimum a placeholder byte).
    assert evidence.stat().st_size > 0
