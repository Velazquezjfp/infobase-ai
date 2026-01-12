"""
Test Case: TC-S5-010-06
Requirement: S5-010 - Optional Persistent Chat History
Description: Long conversation approaches token limit, verify older messages truncated
Generated: 2026-01-09T15:29:16Z
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.conversation_manager import get_conversation_manager
from backend.config import MAX_TOKENS_PER_REQUEST, RESERVE_TOKENS

def test_TC_S5_010_06():
    """Long conversation approaches token limit, verify older messages truncated"""

    # 1. Get conversation manager
    conv_manager = get_conversation_manager()
    case_id = "ACTE-2024-001"

    # 2. Clear any existing history
    conv_manager.clear_conversation(case_id)

    # 3. Create messages with known character counts
    # At 0.25 tokens/char, we need 4 chars per token
    # Token budget: MAX_TOKENS_PER_REQUEST - RESERVE_TOKENS = 30000 - 5000 = 25000 tokens
    # So we need ~100,000 characters to exceed budget

    # Create 10 very long messages (each ~12,000 chars = ~3000 tokens)
    # Total: ~30,000 tokens, which exceeds budget of 25,000
    long_content = "X" * 12000  # Each message is 12,000 characters

    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        conv_manager.add_message(case_id, role, f"Message {i + 1}: {long_content}")

    # 4. Get all stored messages
    all_messages = conv_manager.get_conversation_history(case_id, max_messages=100)
    assert len(all_messages) == 10, f"Expected 10 messages stored, got {len(all_messages)}"

    # 5. Estimate tokens for all messages
    estimated_tokens = conv_manager.estimate_tokens(all_messages)
    expected_budget = MAX_TOKENS_PER_REQUEST - RESERVE_TOKENS

    # Should be around 30,000 tokens (exceeds budget)
    assert estimated_tokens > expected_budget, \
        f"Expected total tokens ({estimated_tokens}) to exceed budget ({expected_budget})"

    # 6. Truncate to token limit
    truncated = conv_manager.truncate_to_token_limit(all_messages)

    # 7. Verify truncated messages fit within budget
    truncated_tokens = conv_manager.estimate_tokens(truncated)
    assert truncated_tokens <= expected_budget, \
        f"Truncated messages ({truncated_tokens} tokens) should fit budget ({expected_budget} tokens)"

    # 8. Verify we kept fewer messages than original
    assert len(truncated) < len(all_messages), \
        f"Expected truncation to remove messages, got {len(truncated)} from {len(all_messages)}"

    # 9. Verify most recent message is always kept
    assert truncated[-1]["content"] == all_messages[-1]["content"], \
        "Most recent message should always be preserved"

    # 10. Clean up
    conv_manager.clear_conversation(case_id)

    print(f"TC-S5-010-06: Token truncation verified - {len(all_messages)} messages truncated to {len(truncated)} to fit {expected_budget} token budget")

if __name__ == "__main__":
    try:
        test_TC_S5_010_06()
        print("TC-S5-010-06: PASSED")
    except AssertionError as e:
        print(f"TC-S5-010-06: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-010-06: ERROR - {e}")
