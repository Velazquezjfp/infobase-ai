"""
Test Case: TC-S5-010-09
Requirement: S5-010 - Optional Persistent Chat History
Description: Two different cases with separate conversations, verify history doesn't mix
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_09():
    """Two different cases with separate conversations, verify history doesn't mix"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id_1 = "ACTE-2024-001"
    case_id_2 = "ACTE-2024-002"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id_1)
    conv_manager.clear_conversation(case_id_2)

    # 3. Add specific messages to case 1
    conv_manager.add_message(case_id_1, "user", "Case 1: Applicant is Maria Schmidt")
    conv_manager.add_message(case_id_1, "assistant", "Case 1: Noted. Maria Schmidt's documents are...")
    conv_manager.add_message(case_id_1, "user", "Case 1: Does she need a birth certificate?")

    # 4. Add different messages to case 2
    conv_manager.add_message(case_id_2, "user", "Case 2: Applicant is Hans Mueller")
    conv_manager.add_message(case_id_2, "assistant", "Case 2: Noted. Hans Mueller's requirements are...")
    conv_manager.add_message(case_id_2, "user", "Case 2: What about his passport?")

    # 5. Verify case 1 has exactly 3 messages
    history_1 = conv_manager.get_conversation_history(case_id_1)
    assert len(history_1) == 3, f"Expected 3 messages for case 1, got {len(history_1)}"

    # 6. Verify case 2 has exactly 3 messages
    history_2 = conv_manager.get_conversation_history(case_id_2)
    assert len(history_2) == 3, f"Expected 3 messages for case 2, got {len(history_2)}"

    # 7. Verify case 1 contains only its own content
    case_1_content = " ".join([msg["content"] for msg in history_1])
    assert "Maria Schmidt" in case_1_content, "Case 1 should contain Maria Schmidt"
    assert "Hans Mueller" not in case_1_content, "Case 1 should NOT contain Hans Mueller"
    assert "Case 1:" in case_1_content, "Case 1 should contain its own marker"
    assert "Case 2:" not in case_1_content, "Case 1 should NOT contain case 2 marker"

    # 8. Verify case 2 contains only its own content
    case_2_content = " ".join([msg["content"] for msg in history_2])
    assert "Hans Mueller" in case_2_content, "Case 2 should contain Hans Mueller"
    assert "Maria Schmidt" not in case_2_content, "Case 2 should NOT contain Maria Schmidt"
    assert "Case 2:" in case_2_content, "Case 2 should contain its own marker"
    assert "Case 1:" not in case_2_content, "Case 2 should NOT contain case 1 marker"

    # 9. Verify statistics show 2 separate cases
    stats = conv_manager.get_statistics()
    assert stats["total_cases"] >= 2, f"Expected at least 2 cases, got {stats['total_cases']}"
    assert case_id_1 in stats["messages_per_case"], "Case 1 should be in statistics"
    assert case_id_2 in stats["messages_per_case"], "Case 2 should be in statistics"
    assert stats["messages_per_case"][case_id_1] == 3, "Case 1 should have 3 messages"
    assert stats["messages_per_case"][case_id_2] == 3, "Case 2 should have 3 messages"

    # 10. Clean up
    conv_manager.clear_conversation(case_id_1)
    conv_manager.clear_conversation(case_id_2)

    print("TC-S5-010-09: Multiple cases verified - conversations remain completely isolated")

if __name__ == "__main__":
    try:
        test_TC_S5_010_09()
        print("TC-S5-010-09: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-09: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-09: ERROR - {e}")
