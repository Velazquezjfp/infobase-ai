"""
Configuration settings for BAMF AI Case Management System.

This module contains application-wide configuration constants and feature flags.
Settings can be overridden via environment variables.
"""

import os
from typing import Optional


# ============================================================================
# Chat History Configuration (S5-010)
# ============================================================================

def get_bool_env(key: str, default: bool) -> bool:
    """
    Get boolean value from environment variable.

    Args:
        key: Environment variable name.
        default: Default value if not set.

    Returns:
        bool: The boolean value.
    """
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def get_int_env(key: str, default: int) -> int:
    """
    Get integer value from environment variable.

    Args:
        key: Environment variable name.
        default: Default value if not set.

    Returns:
        int: The integer value.
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_float_env(key: str, default: float) -> float:
    """
    Get float value from environment variable.

    Args:
        key: Environment variable name.
        default: Default value if not set.

    Returns:
        float: The float value.
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


# Feature flag: Enable/disable persistent chat history
# Default: False (disabled for POC, can be enabled via environment variable)
ENABLE_CHAT_HISTORY: bool = get_bool_env('ENABLE_CHAT_HISTORY', False)

# Maximum number of messages to keep in conversation history per case
# Older messages are dropped when this limit is exceeded
MAX_CONVERSATION_HISTORY: int = get_int_env('MAX_CONVERSATION_HISTORY', 10)

# Maximum tokens per API request to Gemini
# Used for token budget calculation to avoid exceeding API limits
MAX_TOKENS_PER_REQUEST: int = get_int_env('MAX_TOKENS_PER_REQUEST', 30000)

# Token estimation: approximate tokens per character
# Rule of thumb: 1 token ≈ 4 characters, so 0.25 tokens/char
TOKEN_ESTIMATE_PER_CHAR: float = get_float_env('TOKEN_ESTIMATE_PER_CHAR', 0.25)

# Reserve tokens for the current prompt and response
# This ensures we leave room for the user's message and AI response
RESERVE_TOKENS: int = get_int_env('RESERVE_TOKENS', 5000)


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================================
# Configuration Summary (for debugging)
# ============================================================================

def get_config_summary() -> dict:
    """
    Get a summary of current configuration settings.

    Returns:
        dict: Configuration settings.
    """
    return {
        'chat_history': {
            'enabled': ENABLE_CHAT_HISTORY,
            'max_history': MAX_CONVERSATION_HISTORY,
            'max_tokens': MAX_TOKENS_PER_REQUEST,
            'token_estimate_per_char': TOKEN_ESTIMATE_PER_CHAR,
            'reserve_tokens': RESERVE_TOKENS,
        },
        'logging': {
            'level': LOG_LEVEL,
        }
    }
