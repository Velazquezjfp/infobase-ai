"""
Test Case: TC-S5-010-07
Requirement: S5-010 - Optional Persistent Chat History
Description: Click 'Clear History', verify conversation cleared and next message has no context
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_07():
    """Click 'Clear History', verify conversation cleared and next message has no context"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Add some conversation history
    conv_manager.add_message(case_id, "user", "The applicant name is John Doe")
    conv_manager.add_message(case_id, "assistant", "I've noted that the applicant is John Doe")
    conv_manager.add_message(case_id, "user", "What documents does he need?")
    conv_manager.add_message(case_id, "assistant", "John Doe will need passport and residence permit")

    # 3. Verify history exists (4 messages)
    history_before = conv_manager.get_conversation_history(case_id)
    assert len(history_before) == 4, f"Expected 4 messages before clear, got {len(history_before)}"

    # 4. Clear conversation history (simulates clicking 'Clear History' button)
    cleared_count = conv_manager.clear_conversation(case_id)
    assert cleared_count == 4, f"Expected to clear 4 messages, cleared {cleared_count}"

    # 5. Verify history is now empty
    history_after = conv_manager.get_conversation_history(case_id)
    assert len(history_after) == 0, f"Expected 0 messages after clear, got {len(history_after)}"

    # 6. Verify prepared history for prompt is also empty
    prepared_history = conv_manager.prepare_history_for_prompt(case_id)
    assert len(prepared_history) == 0, f"Expected 0 messages in prepared history, got {len(prepared_history)}"

    # 7. Add a new message after clearing
    conv_manager.add_message(case_id, "user", "What was the applicant's name?")

    # 8. Verify new message exists but no context from before
    history_new = conv_manager.get_conversation_history(case_id)
    assert len(history_new) == 1, f"Expected 1 message after adding new, got {len(history_new)}"
    assert "What was the applicant's name?" in history_new[0]["content"], "New message should be present"

    # 9. Verify old context is NOT present
    all_content = " ".join([msg["content"] for msg in history_new])
    assert "John Doe" not in all_content, "Old context should not be present after clear"

    # 10. Clean up
    conv_manager.clear_conversation(case_id)

    print("TC-S5-010-07: Clear history verified - conversation cleared and no context retained")

if __name__ == "__main__":
    try:
        test_TC_S5_010_07()
        print("TC-S5-010-07: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-07: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-07: ERROR - {e}")
