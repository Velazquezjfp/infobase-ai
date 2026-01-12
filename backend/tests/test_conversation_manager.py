"""
Unit tests for ConversationManager service.

Tests conversation history management, token estimation, context window limiting,
and case isolation for S5-010: Optional Persistent Chat History.
"""

import pytest
from backend.services.conversation_manager import ConversationManager, get_conversation_manager
from backend.config import MAX_CONVERSATION_HISTORY, TOKEN_ESTIMATE_PER_CHAR


class TestConversationManager:
    """Test suite for ConversationManager class."""

    def setup_method(self):
        """Create a fresh ConversationManager instance for each test."""
        self.manager = ConversationManager()

    def test_add_message(self):
        """Test adding messages to conversation history."""
        case_id = "ACTE-2024-001"

        # Add user message
        self.manager.add_message(case_id, "user", "Hello, AI!")
        assert self.manager.get_message_count(case_id) == 1

        # Add assistant message
        self.manager.add_message(case_id, "assistant", "Hello! How can I help?")
        assert self.manager.get_message_count(case_id) == 2

        # Verify messages
        history = self.manager.get_conversation_history(case_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello, AI!"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hello! How can I help?"

    def test_add_message_with_timestamp(self):
        """Test adding messages with timestamps."""
        case_id = "ACTE-2024-001"
        timestamp = "2026-01-12T10:00:00Z"

        self.manager.add_message(case_id, "user", "Test message", timestamp=timestamp)

        history = self.manager.get_conversation_history(case_id)
        assert len(history) == 1
        assert history[0]["timestamp"] == timestamp

    def test_add_message_invalid_role(self):
        """Test that invalid roles raise ValueError."""
        case_id = "ACTE-2024-001"

        with pytest.raises(ValueError, match="Invalid role"):
            self.manager.add_message(case_id, "invalid_role", "Test")

    def test_get_conversation_history_empty(self):
        """Test getting history for case with no messages."""
        case_id = "ACTE-2024-001"
        history = self.manager.get_conversation_history(case_id)
        assert history == []

    def test_context_window_limiting(self):
        """Test that conversation history is limited to max N messages."""
        case_id = "ACTE-2024-001"

        # Add 15 messages
        for i in range(15):
            role = "user" if i % 2 == 0 else "assistant"
            self.manager.add_message(case_id, role, f"Message {i}")

        # Default max is 10, so only last 10 should be returned
        history = self.manager.get_conversation_history(case_id)
        assert len(history) <= MAX_CONVERSATION_HISTORY

        # Verify we got the last 10 messages (messages 5-14)
        if MAX_CONVERSATION_HISTORY == 10:
            assert len(history) == 10
            assert history[0]["content"] == "Message 5"
            assert history[-1]["content"] == "Message 14"

    def test_context_window_custom_limit(self):
        """Test getting history with custom message limit."""
        case_id = "ACTE-2024-001"

        # Add 10 messages
        for i in range(10):
            role = "user" if i % 2 == 0 else "assistant"
            self.manager.add_message(case_id, role, f"Message {i}")

        # Get only last 5 messages
        history = self.manager.get_conversation_history(case_id, max_messages=5)
        assert len(history) == 5
        assert history[0]["content"] == "Message 5"
        assert history[-1]["content"] == "Message 9"

    def test_clear_conversation(self):
        """Test clearing conversation history."""
        case_id = "ACTE-2024-001"

        # Add messages
        self.manager.add_message(case_id, "user", "Message 1")
        self.manager.add_message(case_id, "assistant", "Response 1")
        assert self.manager.get_message_count(case_id) == 2

        # Clear conversation
        cleared_count = self.manager.clear_conversation(case_id)
        assert cleared_count == 2
        assert self.manager.get_message_count(case_id) == 0

        # Verify history is empty
        history = self.manager.get_conversation_history(case_id)
        assert history == []

    def test_case_isolation(self):
        """Test that conversations are isolated per case."""
        case1 = "ACTE-2024-001"
        case2 = "ACTE-2024-002"

        # Add messages to case 1
        self.manager.add_message(case1, "user", "Case 1 message")
        self.manager.add_message(case1, "assistant", "Case 1 response")

        # Add messages to case 2
        self.manager.add_message(case2, "user", "Case 2 message")
        self.manager.add_message(case2, "assistant", "Case 2 response")

        # Verify isolation
        history1 = self.manager.get_conversation_history(case1)
        history2 = self.manager.get_conversation_history(case2)

        assert len(history1) == 2
        assert len(history2) == 2
        assert history1[0]["content"] == "Case 1 message"
        assert history2[0]["content"] == "Case 2 message"

        # Clear case 1, verify case 2 unaffected
        self.manager.clear_conversation(case1)
        assert self.manager.get_message_count(case1) == 0
        assert self.manager.get_message_count(case2) == 2

    def test_estimate_tokens(self):
        """Test token estimation for messages."""
        messages = [
            {"role": "user", "content": "Hello"},  # 5 chars
            {"role": "assistant", "content": "Hi there!"},  # 9 chars
        ]
        # Total: 14 chars * 0.25 tokens/char = 3.5 tokens (rounded to 3)

        estimated = self.manager.estimate_tokens(messages)
        expected = int(14 * TOKEN_ESTIMATE_PER_CHAR)
        assert estimated == expected

    def test_estimate_tokens_empty(self):
        """Test token estimation for empty message list."""
        estimated = self.manager.estimate_tokens([])
        assert estimated == 0

    def test_truncate_to_token_limit(self):
        """Test truncating messages to fit token budget."""
        # Create messages with known character counts
        messages = [
            {"role": "user", "content": "A" * 1000},      # ~250 tokens
            {"role": "assistant", "content": "B" * 1000}, # ~250 tokens
            {"role": "user", "content": "C" * 1000},      # ~250 tokens
            {"role": "assistant", "content": "D" * 1000}, # ~250 tokens
        ]
        # Total: ~1000 tokens

        # Truncate to 600 tokens (should keep last 2-3 messages)
        truncated = self.manager.truncate_to_token_limit(messages, max_tokens=600)

        # Should have removed oldest messages
        assert len(truncated) < len(messages)
        assert truncated[-1]["content"] == "D" * 1000  # Most recent kept

        # Verify token budget is respected
        estimated_tokens = self.manager.estimate_tokens(truncated)
        assert estimated_tokens <= 600

    def test_truncate_keeps_at_least_one_message(self):
        """Test that truncation always keeps at least the most recent message."""
        # Single very long message that exceeds token limit
        messages = [
            {"role": "user", "content": "A" * 200000},  # ~50,000 tokens
        ]

        # Even with low token limit, should keep the message
        truncated = self.manager.truncate_to_token_limit(messages, max_tokens=100)
        assert len(truncated) == 1

    def test_prepare_history_for_prompt(self):
        """Test preparing history for AI prompt."""
        case_id = "ACTE-2024-001"

        # Add messages with timestamps
        self.manager.add_message(case_id, "user", "Hello", "2026-01-12T10:00:00Z")
        self.manager.add_message(case_id, "assistant", "Hi!", "2026-01-12T10:00:01Z")

        # Get prepared history
        prepared = self.manager.prepare_history_for_prompt(case_id)

        assert len(prepared) == 2
        # Verify timestamps are removed
        assert "timestamp" not in prepared[0]
        assert "timestamp" not in prepared[1]
        # Verify role and content are preserved
        assert prepared[0] == {"role": "user", "content": "Hello"}
        assert prepared[1] == {"role": "assistant", "content": "Hi!"}

    def test_get_all_case_ids(self):
        """Test getting list of all cases with history."""
        # Add messages to multiple cases
        self.manager.add_message("ACTE-2024-001", "user", "Test 1")
        self.manager.add_message("ACTE-2024-002", "user", "Test 2")
        self.manager.add_message("ACTE-2024-003", "user", "Test 3")

        case_ids = self.manager.get_all_case_ids()
        assert len(case_ids) == 3
        assert "ACTE-2024-001" in case_ids
        assert "ACTE-2024-002" in case_ids
        assert "ACTE-2024-003" in case_ids

    def test_get_statistics(self):
        """Test getting conversation statistics."""
        # Add messages to multiple cases
        self.manager.add_message("ACTE-2024-001", "user", "Test 1")
        self.manager.add_message("ACTE-2024-001", "assistant", "Response 1")
        self.manager.add_message("ACTE-2024-002", "user", "Test 2")

        stats = self.manager.get_statistics()

        assert stats["total_cases"] == 2
        assert stats["total_messages"] == 3
        assert stats["average_messages_per_case"] == 1.5
        assert stats["messages_per_case"]["ACTE-2024-001"] == 2
        assert stats["messages_per_case"]["ACTE-2024-002"] == 1

    def test_singleton_instance(self):
        """Test that get_conversation_manager returns singleton."""
        manager1 = get_conversation_manager()
        manager2 = get_conversation_manager()

        assert manager1 is manager2

        # Add message via manager1
        manager1.add_message("ACTE-2024-001", "user", "Test")

        # Verify accessible via manager2
        assert manager2.get_message_count("ACTE-2024-001") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
