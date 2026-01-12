"""
Test Case: TC-S5-010-05
Requirement: S5-010 - Optional Persistent Chat History
Description: Send 15 messages, verify only last 10 included in context window
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager
from backend.config import MAX_CONVERSATION_HISTORY

def test_TC_S5_010_05():
    """Send 15 messages, verify only last 10 included in context window"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id)

    # 3. Add 15 messages (alternating user/assistant)
    num_messages = 15
    for i in range(num_messages):
        role = "user" if i % 2 == 0 else "assistant"
        content = f"Message {i + 1}"
        conv_manager.add_message(case_id, role, content)

    # 4. Verify all 15 messages are stored internally
    # (get_message_count returns total stored, not just what's in context window)
    # Actually, based on implementation, all messages are stored, but only last N are retrieved
    stored_count = conv_manager.get_message_count(case_id)
    assert stored_count == num_messages, f"Expected {num_messages} messages stored, got {stored_count}"

    # 5. Get conversation history (should apply MAX_CONVERSATION_HISTORY limit)
    history = conv_manager.get_conversation_history(case_id)

    # 6. Verify only last 10 messages are returned (default MAX_CONVERSATION_HISTORY)
    expected_limit = MAX_CONVERSATION_HISTORY
    assert len(history) == expected_limit, \
        f"Expected {expected_limit} messages in history (MAX_CONVERSATION_HISTORY), got {len(history)}"

    # 7. Verify the messages are the LAST 10 (messages 6-15)
    # First message in returned history should be "Message 6" (index 5 in 0-indexed)
    first_message = history[0]
    assert first_message["content"] == f"Message {num_messages - expected_limit + 1}", \
        f"Expected first message to be 'Message {num_messages - expected_limit + 1}', got '{first_message['content']}'"

    # Last message should be "Message 15"
    last_message = history[-1]
    assert last_message["content"] == f"Message {num_messages}", \
        f"Expected last message to be 'Message {num_messages}', got '{last_message['content']}'"

    # 8. Clean up
    conv_manager.clear_conversation(case_id)

    print(f"TC-S5-010-05: Context window limit verified - only last {expected_limit} of {num_messages} messages included")

if __name__ == "__main__":
    try:
        test_TC_S5_010_05()
        print("TC-S5-010-05: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-05: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-05: ERROR - {e}")
