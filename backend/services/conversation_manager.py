"""
Conversation Manager Service for BAMF AI Case Management System.

This module manages in-memory conversation history for multi-turn AI chat sessions.
Conversations are case-scoped, with automatic context window management and
token budget calculation.

S5-010: Optional Persistent Chat History
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from threading import Lock

from backend.config import (
    MAX_CONVERSATION_HISTORY,
    MAX_TOKENS_PER_REQUEST,
    TOKEN_ESTIMATE_PER_CHAR,
    RESERVE_TOKENS
)

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages in-memory conversation history for case-scoped AI chat sessions.

    Features:
    - Per-case conversation isolation
    - Automatic context window management (max N messages)
    - Token budget calculation and truncation
    - Thread-safe operations

    Note: Conversation history is stored in-memory only and will be cleared
    on application restart. This is by design for the POC phase.
    """

    def __init__(self):
        """
        Initialize the conversation manager with empty in-memory storage.
        """
        # In-memory storage: case_id -> list of message dicts
        self._conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Thread lock for safe concurrent access
        self._lock = Lock()

        logger.info("ConversationManager initialized")

    def add_message(
        self,
        case_id: str,
        role: str,
        content: str,
        timestamp: Optional[str] = None
    ) -> None:
        """
        Add a message to the conversation history for a specific case.

        Args:
            case_id: The case ID (e.g., "ACTE-2024-001").
            role: Message role ("user" or "assistant").
            content: Message content.
            timestamp: Optional ISO timestamp (for logging/debugging).

        Raises:
            ValueError: If role is not "user" or "assistant".
        """
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'.")

        message = {
            "role": role,
            "content": content,
        }
        if timestamp:
            message["timestamp"] = timestamp

        with self._lock:
            self._conversations[case_id].append(message)
            logger.debug(
                f"Added {role} message to case {case_id} "
                f"(total: {len(self._conversations[case_id])} messages)"
            )

    def get_conversation_history(
        self,
        case_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific case.

        Returns the last N messages, where N is determined by max_messages
        or MAX_CONVERSATION_HISTORY config setting.

        Args:
            case_id: The case ID.
            max_messages: Optional maximum number of messages to return.
                         Defaults to MAX_CONVERSATION_HISTORY from config.

        Returns:
            List of message dictionaries in chronological order.
            Each dict contains: {"role": str, "content": str, "timestamp": str (optional)}
        """
        if max_messages is None:
            max_messages = MAX_CONVERSATION_HISTORY

        with self._lock:
            messages = self._conversations.get(case_id, [])
            # Return last N messages
            return messages[-max_messages:] if messages else []

    def clear_conversation(self, case_id: str) -> int:
        """
        Clear all conversation history for a specific case.

        Args:
            case_id: The case ID to clear.

        Returns:
            int: Number of messages cleared.
        """
        with self._lock:
            messages_count = len(self._conversations.get(case_id, []))
            if case_id in self._conversations:
                del self._conversations[case_id]
                logger.info(f"Cleared conversation history for case {case_id} ({messages_count} messages)")
            return messages_count

    def get_all_case_ids(self) -> List[str]:
        """
        Get list of all case IDs with conversation history.

        Returns:
            List of case IDs.
        """
        with self._lock:
            return list(self._conversations.keys())

    def get_message_count(self, case_id: str) -> int:
        """
        Get the number of messages in a case's conversation history.

        Args:
            case_id: The case ID.

        Returns:
            int: Number of messages.
        """
        with self._lock:
            return len(self._conversations.get(case_id, []))

    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate the number of tokens in a list of messages.

        Uses a simple character-based estimation (TOKEN_ESTIMATE_PER_CHAR).
        This is approximate but sufficient for budget management.

        Args:
            messages: List of message dictionaries.

        Returns:
            int: Estimated token count.
        """
        if not messages:
            return 0

        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_tokens = int(total_chars * TOKEN_ESTIMATE_PER_CHAR)

        logger.debug(
            f"Token estimation: {total_chars} chars ≈ {estimated_tokens} tokens "
            f"({TOKEN_ESTIMATE_PER_CHAR} tokens/char)"
        )

        return estimated_tokens

    def truncate_to_token_limit(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Truncate messages to fit within token budget.

        Removes oldest messages until the total estimated tokens is below
        the specified limit. Always keeps at least the most recent message.

        Args:
            messages: List of message dictionaries.
            max_tokens: Maximum token budget. Defaults to MAX_TOKENS_PER_REQUEST - RESERVE_TOKENS.

        Returns:
            List of messages that fit within token budget.
        """
        if not messages:
            return []

        if max_tokens is None:
            max_tokens = MAX_TOKENS_PER_REQUEST - RESERVE_TOKENS

        # Start with all messages
        truncated = messages[:]
        estimated_tokens = self.estimate_tokens(truncated)

        # Remove oldest messages until we fit the budget
        while estimated_tokens > max_tokens and len(truncated) > 1:
            # Remove the oldest message
            truncated.pop(0)
            estimated_tokens = self.estimate_tokens(truncated)

        if len(truncated) < len(messages):
            logger.info(
                f"Truncated conversation history: {len(messages)} -> {len(truncated)} messages "
                f"(estimated tokens: {estimated_tokens}/{max_tokens})"
            )

        return truncated

    def prepare_history_for_prompt(
        self,
        case_id: str,
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare conversation history for inclusion in AI prompt.

        Gets the conversation history, applies context window limiting,
        and truncates to fit token budget.

        Args:
            case_id: The case ID.
            max_tokens: Optional token budget limit.

        Returns:
            List of message dicts with "role" and "content" keys only
            (timestamps removed for cleaner prompts).
        """
        # Get conversation history with context window limit
        messages = self.get_conversation_history(case_id)

        # Truncate to token budget
        messages = self.truncate_to_token_limit(messages, max_tokens)

        # Return clean format for prompt (remove timestamps)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about conversation manager state.

        Returns:
            dict: Statistics including total cases, messages per case, etc.
        """
        with self._lock:
            total_cases = len(self._conversations)
            total_messages = sum(len(msgs) for msgs in self._conversations.values())
            messages_per_case = {
                case_id: len(msgs)
                for case_id, msgs in self._conversations.items()
            }

            return {
                "total_cases": total_cases,
                "total_messages": total_messages,
                "average_messages_per_case": total_messages / total_cases if total_cases > 0 else 0,
                "messages_per_case": messages_per_case,
            }


# Singleton instance
_conversation_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """
    Get the singleton ConversationManager instance.

    Returns:
        ConversationManager: The singleton instance.
    """
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
