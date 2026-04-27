"""
Test Case: TC-S5-010-08
Requirement: S5-010 - Optional Persistent Chat History
Description: Restart backend, verify all conversation history cleared (no persistence)
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import ConversationManager

def test_TC_S5_010_08():
    """Restart backend, verify all conversation history cleared (no persistence)"""

    # Note: This test simulates backend restart by creating a new ConversationManager instance
    # In reality, on backend restart, the singleton instance is recreated and all in-memory data is lost

    # 1. Create first instance (simulates initial backend start)
    conv_manager_1 = ConversationManager()
    case_id = "ACTE-2024-001"

    # 2. Add conversation history
    conv_manager_1.add_message(case_id, "user", "This is a test message")
    conv_manager_1.add_message(case_id, "assistant", "This is a response")

    # 3. Verify messages exist
    history_1 = conv_manager_1.get_conversation_history(case_id)
    assert len(history_1) == 2, f"Expected 2 messages in first instance, got {len(history_1)}"

    # 4. Get statistics from first instance
    stats_1 = conv_manager_1.get_statistics()
    assert stats_1["total_cases"] == 1, "Expected 1 case in first instance"
    assert stats_1["total_messages"] == 2, "Expected 2 messages in first instance"

    # 5. Simulate backend restart by creating a new instance
    conv_manager_2 = ConversationManager()

    # 6. Verify new instance has no conversation history (in-memory only, no persistence)
    history_2 = conv_manager_2.get_conversation_history(case_id)
    assert len(history_2) == 0, f"Expected 0 messages after restart, got {len(history_2)}"

    # 7. Verify statistics show empty state
    stats_2 = conv_manager_2.get_statistics()
    assert stats_2["total_cases"] == 0, f"Expected 0 cases after restart, got {stats_2['total_cases']}"
    assert stats_2["total_messages"] == 0, f"Expected 0 messages after restart, got {stats_2['total_messages']}"

    # 8. Verify all case IDs are empty
    case_ids = conv_manager_2.get_all_case_ids()
    assert len(case_ids) == 0, f"Expected 0 case IDs after restart, got {len(case_ids)}"

    print("TC-S5-010-08: Backend restart verified - all conversation history cleared (in-memory only, no persistence)")

if __name__ == "__main__":
    try:
        test_TC_S5_010_08()
        print("TC-S5-010-08: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-08: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-08: ERROR - {e}")
