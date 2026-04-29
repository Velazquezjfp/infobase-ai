"""TC-S001-F-007-02 — Browser-close-equivalent reset clears custom_rules.json.

Acceptance criterion: after the reset (mirroring the navigator.sendBeacon path
fired on tab close), the case's `custom_rules.json` is back to the template
state. The integration_course template provides no `custom_rules.json`, so the
file must be absent after the reset.
"""

from __future__ import annotations

import json


def test_reset_removes_custom_rules_modifications(session_sandbox):
    sm = session_sandbox["session_manager"]
    case_id = session_sandbox["case_id"]
    cases_dir = session_sandbox["cases_dir"]

    # Stage the case dir as if the user had used the chat to add a custom rule.
    case_dir = cases_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    custom_rules = case_dir / "custom_rules.json"
    custom_rules.write_text(json.dumps({
        "caseId": case_id,
        "lastModified": "2026-04-29T00:00:00+00:00",
        "rules": [{
            "id": "custom-rule-test",
            "type": "validation_rule",
            "createdAt": "2026-04-29T00:00:00+00:00",
            "targetFolder": "evidence",
            "rule": "test rule",
            "ruleType": "folder_rule",
        }],
    }), encoding="utf-8")
    assert custom_rules.exists(), "Test setup failed: custom_rules.json not staged"

    sm.reset_case_to_seed(case_id)

    # The integration_course template has no custom_rules.json, so the reset
    # must restore that absent state.
    assert not custom_rules.exists(), (
        "custom_rules.json should be absent after reset because the "
        "integration_course template does not provide one"
    )

    # case.json must still exist and carry the right caseId.
    case_json = case_dir / "case.json"
    assert case_json.exists(), "case.json must be restored from the template"
    data = json.loads(case_json.read_text(encoding="utf-8"))
    assert data["caseId"] == case_id
