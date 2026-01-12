"""
Test Case: TC-S5-010-03
Requirement: S5-010 - Optional Persistent Chat History
Description: Send follow-up question 'What was the name again?', verify AI uses previous context
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_03():
    """Send follow-up question 'What was the name again?', verify AI uses previous context"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id)

    # 3. Simulate initial conversation with a name
    conv_manager.add_message(case_id, "user", "The applicant's name is Maria Schmidt")
    conv_manager.add_message(case_id, "assistant", "Thank you. I've noted that the applicant is Maria Schmidt. How can I help you with her case?")

    # 4. Add follow-up question that requires context
    conv_manager.add_message(case_id, "user", "What was the name again?")

    # 5. Prepare history for prompt (this is what would be sent to AI)
    history = conv_manager.prepare_history_for_prompt(case_id)

    # 6. Verify all messages are included in history
    assert len(history) == 3, f"Expected 3 messages in prepared history, got {len(history)}"

    # 7. Verify the history contains the original name context
    user_messages = [msg["content"] for msg in history if msg["role"] == "user"]
    assert "Maria Schmidt" in user_messages[0], "Original context with name should be in history"
    assert "What was the name again?" in user_messages[1], "Follow-up question should be in history"

    # 8. Verify history is in correct chronological order
    assert history[0]["role"] == "user", "First message should be user"
    assert history[1]["role"] == "assistant", "Second message should be assistant"
    assert history[2]["role"] == "user", "Third message should be user"

    # 9. Clean up
    conv_manager.clear_conversation(case_id)

    print("TC-S5-010-03: Follow-up question context verified - history includes previous messages")

if __name__ == "__main__":
    try:
        test_TC_S5_010_03()
        print("TC-S5-010-03: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-03: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-03: ERROR - {e}")
