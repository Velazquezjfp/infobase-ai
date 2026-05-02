"""
Configuration settings for BAMF AI Case Management System.

This module contains application-wide configuration constants and feature flags.
Settings can be overridden via environment variables.
"""

import os
from pathlib import Path
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
# Document Storage Configuration (S5-007)
# ============================================================================

def get_documents_path() -> str:
    """
    Get the base path for document storage.

    For local development, defaults to 'public/documents'.
    For containers, set DOCUMENTS_PATH environment variable to '/var/app/documents'
    and mount as a volume for persistence.

    Returns:
        str: The base path for document storage.
    """
    return os.getenv('DOCUMENTS_PATH', 'public/documents')


# Base path for document storage
# In containers, this should be set to '/var/app/documents' and mounted as a volume
DOCUMENTS_BASE_PATH: str = get_documents_path()


# ----------------------------------------------------------------------------
# S001-NFR-006: legacy `public/documents/` path translation
# ----------------------------------------------------------------------------
# `document_manifest.json` and the SPA's DocumentViewer encode document paths
# with the project-root-relative prefix `public/documents/<rest>` (frozen from
# the host-dev era). Inside the container, cwd is `/app` and that prefix does
# not resolve — files actually live under DOCUMENTS_BASE_PATH (`/var/app/documents`
# in the containerised deployment, `public/documents` in host-dev — same string,
# no-op).
#
# This helper translates legacy paths transparently and passes everything else
# through. Used at the three service-layer entry points where Python opens
# the file (pdf_service / email_service). NEVER touched by the API layer or
# the prompt-building / chat path.

LEGACY_DOCUMENTS_PREFIX = "public/documents/"


def resolve_document_path(path: str) -> Path:
    """
    Resolve a document path to its on-disk location, translating the legacy
    project-root-relative prefix when needed.

    Translation rule:
      - If `path` starts with `public/documents/`, replace that prefix with
        `${DOCUMENTS_BASE_PATH}/`. In host-dev (DOCUMENTS_BASE_PATH ==
        'public/documents') this is a no-op; in container-run
        (DOCUMENTS_BASE_PATH == '/var/app/documents') it relocates the path
        under the volume mount.
      - Otherwise (absolute paths, other relative paths), return Path(path)
        unchanged.

    See `docs/requirements/sprint-001/S001-NFR-006.md` for full rationale.

    Args:
        path: Legacy or already-resolved path, as a string.

    Returns:
        A `pathlib.Path` pointing at the on-disk file.
    """
    if path.startswith(LEGACY_DOCUMENTS_PREFIX):
        relative = path[len(LEGACY_DOCUMENTS_PREFIX):]
        return Path(DOCUMENTS_BASE_PATH) / relative
    return Path(path)


# ============================================================================
# IDIRS API Configuration (Hybrid Search & RAG)
# ============================================================================

IDIRS_BASE_URL: str = os.getenv('IDIRS_BASE_URL', 'http://localhost:8010')
IDIRS_TIMEOUT: int = get_int_env('IDIRS_TIMEOUT', 30)
RAG_CONFIDENCE_THRESHOLD: float = get_float_env('RAG_CONFIDENCE_THRESHOLD', 0.80)


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================================
# LLM Provider Configuration (S001-F-001)
# ============================================================================
# LLM_BACKEND selects the provider implementation in
# backend.services.llm_provider:
#   - 'internal' (default): route through the LiteLLM proxy (closed-env path)
#   - 'external': use google.generativeai directly (developer opt-in)
# Any other value raises ValueError when llm_provider.get_provider() is first
# called.

LLM_BACKEND: str = os.getenv('LLM_BACKEND', 'internal')

# OpenAI-compatible base URL of the LiteLLM proxy. Required when LLM_BACKEND
# is 'internal'.
LITELLM_PROXY_URL: str = os.getenv('LITELLM_PROXY_URL', '')

# Bearer token / master key the proxy expects. Empty string is acceptable
# when the proxy is unauthenticated; LiteLLM still requires a non-None value.
LITELLM_TOKEN: str = os.getenv('LITELLM_TOKEN', '')

# Model identifier the proxy should route to (e.g. the host's Ollama model).
# Default matches the model preinstalled on the closed-environment host.
LITELLM_MODEL: str = os.getenv('LITELLM_MODEL', 'gemma3:12b')

# API key for the public Gemini API. Only consulted when LLM_BACKEND is
# 'external'; absence is fine on the 'internal' path.
GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')


# ============================================================================
# Feature Flags (S001-F-004 / S001-F-005 / S001-F-006)
# ============================================================================

# Feature flag: Enable/disable PII anonymization service
# Default: False (external service unreachable in closed environment)
ENABLE_ANONYMIZATION: bool = get_bool_env('ENABLE_ANONYMIZATION', False)

# Feature flag: Enable/disable IDIRS document search and RAG
# Default: False (IDIRS unreachable in closed environment)
ENABLE_DOCUMENT_SEARCH: bool = get_bool_env('ENABLE_DOCUMENT_SEARCH', False)

# Feature flag: Enable/disable file upload
# Default: False (upload stubbed out for sprint 1)
ENABLE_UPLOAD: bool = get_bool_env('ENABLE_UPLOAD', False)


# ============================================================================
# Session Lifecycle Configuration (S001-F-007)
# ============================================================================

# Idle threshold (in minutes) after which a sprint-1 demo session is reset
# back to its seed state. The frontend useIdleTimeout hook reads its
# Vite-prefixed counterpart (VITE_SESSION_IDLE_TIMEOUT_MINUTES); this value
# is the backend-side reference for any server-driven watchdog logic and is
# also exposed as part of the configuration summary.
SESSION_IDLE_TIMEOUT_MINUTES: int = get_int_env('SESSION_IDLE_TIMEOUT_MINUTES', 10)


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
        'document_storage': {
            'base_path': DOCUMENTS_BASE_PATH,
        },
        'logging': {
            'level': LOG_LEVEL,
        },
        'llm': {
            'backend': LLM_BACKEND,
            'litellm_proxy_url': LITELLM_PROXY_URL or '(unset)',
            'litellm_model': LITELLM_MODEL,
            'gemini_api_key_set': bool(GEMINI_API_KEY),
        },
    }
