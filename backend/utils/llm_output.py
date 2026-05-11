"""
LLM output parsing utilities (S001-NFR-007).

Centralizes the cleaning and parsing of structured (JSON) LLM responses so
all tools using the LLM backend share one robust implementation. Handles:

- Code-fence stripping: ```json ... ``` and ``` ... ```
- Preamble recovery: extracts {...} or [...] when models add prose before/after
- Optional truncation repair: balances unclosed braces/quotes for long outputs
- Graceful failure: returns None instead of raising, so callers can fall back

Used by form_parser, semantic_search (gemini_service), validation_service,
shacl_generator, and field_generator.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)


JSON_ONLY_HEADER = (
    "CRITICAL INSTRUCTION: Your ENTIRE response must be a single valid JSON "
    "value. Start with `{` (for an object) or `[` (for an array) and end with "
    "the matching closing brace/bracket. Do NOT write any preamble, "
    "explanation, greeting, or commentary — only the JSON itself."
)


def _strip_code_fence(text: str) -> str:
    """Remove ``` or ```json wrappers around JSON content."""
    text = text.strip()
    if "```" not in text:
        return text
    match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', text)
    if match:
        return match.group(1).strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def _extract_json_block(text: str, expect: str) -> Optional[str]:
    """Recover the JSON block when the response has prose before/after."""
    if not text:
        return None
    if text.startswith("{") or text.startswith("["):
        return text

    patterns: list[tuple[str, str]] = []
    if expect == "array":
        patterns.append(("array", r'\[[\s\S]*\]'))
        patterns.append(("object", r'\{[\s\S]*\}'))
    else:
        patterns.append(("object", r'\{[\s\S]*\}'))
        patterns.append(("array", r'\[[\s\S]*\]'))

    for kind, pattern in patterns:
        match = re.search(pattern, text)
        if match:
            logger.debug(f"Extracted JSON {kind} from preamble-laden response")
            return match.group(0)
    return None


def _repair_truncation(text: str) -> str:
    """Best-effort repair for truncated JSON: balance quotes and brackets."""
    if not text:
        return text
    unescaped_quotes = len(re.findall(r'(?<!\\)"', text))
    if unescaped_quotes % 2 == 1:
        text += '"'
        logger.debug("Repaired unterminated string in truncated JSON")
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    if open_brackets > close_brackets:
        text += ']' * (open_brackets - close_brackets)
        logger.debug(f"Repaired {open_brackets - close_brackets} unclosed brackets")
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces > close_braces:
        text += '}' * (open_braces - close_braces)
        logger.debug(f"Repaired {open_braces - close_braces} unclosed braces")
    return text


def extract_json_from_llm_response(
    text: str,
    *,
    expect: Literal["object", "array", "any"] = "any",
    repair_truncation: bool = False,
) -> Optional[Any]:
    """Parse an LLM response into a Python object, robust to common defects.

    Args:
        text: Raw response from the LLM.
        expect: Preferred shape — "object" tries {...} first, "array" tries
            [...] first, "any" tries object then array. Affects both regex
            ordering and log messages.
        repair_truncation: When True, attempt to balance unclosed quotes,
            brackets, and braces before parsing. Use for long structured
            outputs that may hit max_tokens.

    Returns:
        Parsed dict or list on success; None on any failure (logged).
        Callers should handle None as "extraction failed" rather than crash.
    """
    if not text or not text.strip():
        logger.debug("Empty LLM response, cannot parse JSON")
        return None

    cleaned = _strip_code_fence(text)
    candidate = _extract_json_block(cleaned, expect)

    if candidate is None:
        logger.warning(
            "No JSON block found in LLM response (expected %s). "
            "First 200 chars: %s",
            expect, cleaned[:200],
        )
        return None

    if repair_truncation:
        candidate = _repair_truncation(candidate)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        logger.warning(
            "Failed to parse JSON from LLM response: %s. "
            "Candidate (first 200 chars): %s",
            str(e), candidate[:200],
        )
        return None
