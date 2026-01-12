"""
Test Case: TC-S5-010-04
Requirement: S5-010 - Optional Persistent Chat History
Description: Switch case, verify conversation history switches to new case
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_04():
    """Switch case, verify conversation history switches to new case"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id_1 = "ACTE-2024-001"
    case_id_2 = "ACTE-2024-002"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id_1)
    conv_manager.clear_conversation(case_id_2)

    # 3. Add messages to first case
    conv_manager.add_message(case_id_1, "user", "Tell me about case 001")
    conv_manager.add_message(case_id_1, "assistant", "This is information about case 001")

    # 4. Verify first case has 2 messages
    history_1 = conv_manager.get_conversation_history(case_id_1)
    assert len(history_1) == 2, f"Expected 2 messages for case 1, got {len(history_1)}"

    # 5. Switch to second case and add messages
    conv_manager.add_message(case_id_2, "user", "Tell me about case 002")
    conv_manager.add_message(case_id_2, "assistant", "This is information about case 002")

    # 6. Verify second case has 2 messages
    history_2 = conv_manager.get_conversation_history(case_id_2)
    assert len(history_2) == 2, f"Expected 2 messages for case 2, got {len(history_2)}"

    # 7. Verify first case still has its original 2 messages
    history_1_again = conv_manager.get_conversation_history(case_id_1)
    assert len(history_1_again) == 2, f"Case 1 should still have 2 messages, got {len(history_1_again)}"

    # 8. Verify content is case-specific
    assert "case 001" in history_1_again[0]["content"], "Case 1 should contain its own content"
    assert "case 002" in history_2[0]["content"], "Case 2 should contain its own content"

    # 9. Verify histories are completely independent
    assert history_1_again[0]["content"] != history_2[0]["content"], "Histories should be different"

    # 10. Clean up
    conv_manager.clear_conversation(case_id_1)
    conv_manager.clear_conversation(case_id_2)

    print("TC-S5-010-04: Case switching verified - histories remain separate and independent")

if __name__ == "__main__":
    try:
        test_TC_S5_010_04()
        print("TC-S5-010-04: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-04: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-04: ERROR - {e}")
