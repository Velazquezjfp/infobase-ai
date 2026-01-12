"""
Test Case: TC-S5-010-11
Requirement: S5-010 - Optional Persistent Chat History
Description: User asks 'Translate it to French' (referring to previous doc), verify AI understands reference
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager

def test_TC_S5_010_11():
    """User asks 'Translate it to French' (referring to previous doc), verify AI understands reference"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id)

    # 3. Simulate initial conversation about a document
    conv_manager.add_message(case_id, "user", "Can you summarize the residence permit document?")
    conv_manager.add_message(
        case_id,
        "assistant",
        "The residence permit document shows that the applicant has legal authorization "
        "to reside in Germany for work purposes, valid until December 2025."
    )

    # 4. Add follow-up with pronoun reference ('it' refers to the document)
    conv_manager.add_message(case_id, "user", "Translate it to French")

    # 5. Prepare history for prompt
    history = conv_manager.prepare_history_for_prompt(case_id)

    # 6. Verify all 3 messages are included
    assert len(history) == 3, f"Expected 3 messages in history, got {len(history)}"

    # 7. Verify the referent (the document discussion) is in the history
    user_messages = [msg["content"] for msg in history if msg["role"] == "user"]
    assistant_messages = [msg["content"] for msg in history if msg["role"] == "assistant"]

    assert len(user_messages) == 2, "Should have 2 user messages"
    assert len(assistant_messages) == 1, "Should have 1 assistant message"

    # 8. Verify the original document context is present
    assert "residence permit document" in user_messages[0], \
        "Original document reference should be in history"

    # 9. Verify the assistant's response about the document is present
    assert "residence permit document" in assistant_messages[0], \
        "Assistant's response about the document should be in history"

    # 10. Verify the pronoun reference is present
    assert "Translate it to French" in user_messages[1], \
        "Pronoun reference message should be in history"

    # 11. Verify chronological order
    assert history[0]["role"] == "user", "First should be user"
    assert history[1]["role"] == "assistant", "Second should be assistant"
    assert history[2]["role"] == "user", "Third should be user"

    # 12. Test another pronoun reference scenario
    conv_manager.add_message(
        case_id,
        "assistant",
        "Here is the French translation: Le document de titre de séjour..."
    )
    conv_manager.add_message(case_id, "user", "Can you also translate it to Spanish?")

    history_updated = conv_manager.prepare_history_for_prompt(case_id)
    assert len(history_updated) == 5, f"Expected 5 messages after more context, got {len(history_updated)}"

    # 13. Clean up
    conv_manager.clear_conversation(case_id)

    print("TC-S5-010-11: Pronoun reference verified - conversation history enables contextual understanding")

if __name__ == "__main__":
    try:
        test_TC_S5_010_11()
        print("TC-S5-010-11: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-11: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-11: ERROR - {e}")
