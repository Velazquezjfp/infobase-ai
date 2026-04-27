"""
Test Case: TC-S5-010-02
Requirement: S5-010 - Optional Persistent Chat History
Description: Feature flag enabled, send message, verify history stored in conversation_manager
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_02():
    """Feature flag enabled, send message, verify history stored in conversation_manager"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Clear any existing history first
    conv_manager.clear_conversation(case_id)

    # 3. Add a user message
    user_message = "What documents are required for integration course application?"
    conv_manager.add_message(case_id, "user", user_message)

    # 4. Verify message is stored
    history = conv_manager.get_conversation_history(case_id)
    assert len(history) == 1, f"Expected 1 message in history, got {len(history)}"
    assert history[0]["role"] == "user", f"Expected role 'user', got {history[0]['role']}"
    assert history[0]["content"] == user_message, "Message content mismatch"

    # 5. Add an assistant response
    assistant_message = "For an integration course application, you typically need: passport, residence permit, and proof of registration."
    conv_manager.add_message(case_id, "assistant", assistant_message)

    # 6. Verify both messages are stored
    history = conv_manager.get_conversation_history(case_id)
    assert len(history) == 2, f"Expected 2 messages in history, got {len(history)}"
    assert history[0]["role"] == "user", "First message should be user"
    assert history[1]["role"] == "assistant", "Second message should be assistant"
    assert history[1]["content"] == assistant_message, "Assistant message content mismatch"

    # 7. Clean up
    cleared = conv_manager.clear_conversation(case_id)
    assert cleared == 2, f"Expected to clear 2 messages, cleared {cleared}"

    print("TC-S5-010-02: Messages successfully stored in conversation manager")

if __name__ == "__main__":
    try:
        test_TC_S5_010_02()
        print("TC-S5-010-02: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-02: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-02: ERROR - {e}")
