"""
S5-003: Language Detector - Automatic Language Detection for Semantic Search.

This module provides language detection functionality for the semantic search feature.
It detects the language of text input (queries and documents) to enable cross-language
semantic search capabilities.

Features:
    - Automatic language detection from text
    - Returns ISO 639-1 language codes (en, de, fr, ar, etc.)
    - Handles short text and mixed-language content
    - Fallback to default language on detection failure

Dependencies:
    - langdetect: Python port of Google's language detection library
"""

import logging
from typing import Optional

from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


def detect_language(text: str, default: str = 'en') -> str:
    """
    Detect the language of the given text.

    Uses the langdetect library to identify the language of text input.
    Returns ISO 639-1 language codes (2-letter codes like 'en', 'de', 'fr').

    Args:
        text: The text to analyze for language detection
        default: Default language code to return if detection fails (default: 'en')

    Returns:
        str: ISO 639-1 language code (e.g., 'en', 'de', 'fr', 'ar')

    Examples:
        >>> detect_language("Hello, how are you?")
        'en'

        >>> detect_language("Guten Tag, wie geht es Ihnen?")
        'de'

        >>> detect_language("Bonjour, comment allez-vous?")
        'fr'

        >>> detect_language("مرحبا، كيف حالك؟")
        'ar'

    Note:
        - Short text (< 20 characters) may not be detected accurately
        - Mixed-language text will return the dominant language
        - Returns default language if detection fails
    """
    # Validate input
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection, using default")
        return default

    # Clean text for better detection
    text_cleaned = text.strip()

    # Very short text may not be detected accurately
    if len(text_cleaned) < 10:
        logger.warning(
            f"Text too short for reliable detection ({len(text_cleaned)} chars), "
            f"using default: {default}"
        )
        return default

    try:
        # Detect language
        detected_lang = detect(text_cleaned)

        logger.info(
            f"Detected language: {detected_lang} "
            f"(text length: {len(text_cleaned)} chars)"
        )

        return detected_lang

    except LangDetectException as e:
        # Detection failed - this can happen with very short or ambiguous text
        logger.warning(
            f"Language detection failed: {str(e)}. Using default: {default}"
        )
        return default

    except Exception as e:
        # Unexpected error
        logger.error(
            f"Unexpected error in language detection: {str(e)}. Using default: {default}"
        )
        return default


def detect_query_and_document_languages(
    query: str,
    document: str,
    query_default: str = 'en',
    doc_default: str = 'en'
) -> tuple[str, str]:
    """
    Detect languages for both query and document text.

    Convenience function that detects languages for both the search query
    and the document being searched. Useful for cross-language semantic search.

    Args:
        query: The search query text
        document: The document text
        query_default: Default language for query if detection fails
        doc_default: Default language for document if detection fails

    Returns:
        tuple[str, str]: Tuple of (query_language, document_language)

    Example:
        >>> query = "passport number"
        >>> document = "Reisepassnummer: 123456789"
        >>> q_lang, d_lang = detect_query_and_document_languages(query, document)
        >>> print(f"Query: {q_lang}, Document: {d_lang}")
        Query: en, Document: de
    """
    query_lang = detect_language(query, default=query_default)
    doc_lang = detect_language(document, default=doc_default)

    logger.info(
        f"Language detection: Query={query_lang}, Document={doc_lang}"
    )

    return query_lang, doc_lang


def is_cross_language_search(query_lang: str, doc_lang: str) -> bool:
    """
    Check if the search is cross-language (query and document in different languages).

    Args:
        query_lang: Language code of the query
        doc_lang: Language code of the document

    Returns:
        bool: True if languages differ, False if same

    Example:
        >>> is_cross_language_search('en', 'de')
        True

        >>> is_cross_language_search('en', 'en')
        False
    """
    is_cross = query_lang.lower() != doc_lang.lower()

    if is_cross:
        logger.info(
            f"Cross-language search detected: {query_lang} → {doc_lang}"
        )

    return is_cross


# Language name mapping for user-friendly display
LANGUAGE_NAMES = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'ru': 'Russian',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'fa': 'Persian',
    'ur': 'Urdu',
    'hi': 'Hindi',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ja': 'Japanese',
    'ko': 'Korean',
}


def get_language_name(lang_code: str) -> str:
    """
    Get the human-readable name for a language code.

    Args:
        lang_code: ISO 639-1 language code

    Returns:
        str: Human-readable language name

    Example:
        >>> get_language_name('de')
        'German'

        >>> get_language_name('unknown')
        'Unknown (unknown)'
    """
    return LANGUAGE_NAMES.get(lang_code.lower(), f"Unknown ({lang_code})")
