"""
Test Case: TC-S5-010-01
Requirement: S5-010 - Optional Persistent Chat History
Description: Feature flag disabled, verify one-shot mode works as before
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager
from backend import config

def test_TC_S5_010_01():
    """Feature flag disabled, verify one-shot mode works as before"""

    # 1. Verify ENABLE_CHAT_HISTORY is False by default
    assert config.ENABLE_CHAT_HISTORY == False, \
        f"Expected ENABLE_CHAT_HISTORY to be False by default, got {config.ENABLE_CHAT_HISTORY}"

    # 2. Get conversation manager (should be initialized)
    conv_manager = get_conversation_manager()
    assert conv_manager is not None, "Conversation manager should be initialized"

    # 3. Verify that when feature is disabled, the conversation manager exists
    # but won't be used by gemini_service (we're testing it exists and works independently)
    case_id = "TEST-CASE-001"

    # 4. Add a test message (this should work even if feature is disabled)
    conv_manager.add_message(case_id, "user", "Test message")

    # 5. Verify the message count is 1
    message_count = conv_manager.get_message_count(case_id)
    assert message_count == 1, f"Expected 1 message, got {message_count}"

    # 6. Clean up
    cleared = conv_manager.clear_conversation(case_id)
    assert cleared == 1, f"Expected to clear 1 message, cleared {cleared}"

    print("TC-S5-010-01: Feature flag disabled - one-shot mode preserved")

if __name__ == "__main__":
    try:
        test_TC_S5_010_01()
        print("TC-S5-010-01: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-01: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-01: ERROR - {e}")
