"""
S5-004: Translation Service - Document Translation with Gemini AI.

This module provides translation services for documents including emails, text files,
and PDFs. Uses Google Gemini API for high-quality translation between any language pairs.

Features:
    - Email translation (.eml files) with header preservation
    - Text document translation
    - Multi-language support (Arabic, German, English, etc.)
    - Preserves email structure and metadata
    - Creates translated renders

Dependencies:
    - google-generativeai: For translation via Gemini API
    - email_service: For email parsing and reconstruction
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """
    Result of a translation operation.

    Attributes:
        success: Whether translation succeeded
        original_path: Path to original file
        translated_path: Path to translated file (if successful)
        source_language: Detected or specified source language
        target_language: Target language for translation
        error: Error message if translation failed
    """
    success: bool
    original_path: str
    translated_path: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    error: Optional[str] = None


class TranslationService:
    """
    Service for translating documents using Gemini AI.

    Supports multiple document types and creates translated renders.
    """

    def __init__(self):
        """Initialize the translation service."""
        logger.info("TranslationService initialized")

    async def translate_text(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "de"
    ) -> str:
        """
        Translate text using Gemini API.

        Args:
            text: Text to translate
            source_lang: Source language (ISO 639-1) or 'auto' for detection
            target_lang: Target language (ISO 639-1), default: German

        Returns:
            str: Translated text

        Raises:
            Exception: If translation fails
        """
        try:
            from backend.services.gemini_service import GeminiService

            gemini = GeminiService()

            # Build translation prompt
            if source_lang == "auto":
                prompt = f"""Translate the following text to {self._get_language_name(target_lang)}.
Maintain the original formatting and structure.

Text to translate:
{text}

Provide ONLY the translated text, no explanations."""
            else:
                prompt = f"""Translate the following text from {self._get_language_name(source_lang)} to {self._get_language_name(target_lang)}.
Maintain the original formatting and structure.

Text to translate:
{text}

Provide ONLY the translated text, no explanations."""

            # Call Gemini for translation
            translated = await gemini.generate_response(
                prompt=prompt,
                case_id=None,  # No case context needed for translation
                folder_id=None,
                document_content=None,
                stream=False,
                language='en'  # Respond in English for consistency
            )

            logger.info(f"Translated {len(text)} chars to {target_lang}")
            return translated.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise Exception(f"Translation failed: {str(e)}")

    async def translate_email(
        self,
        email_path: str,
        target_lang: str = "de",
        source_lang: str = "auto"
    ) -> TranslationResult:
        """
        Translate an email file and create a new .eml with translated content.

        Translates the subject and body while preserving original headers
        (From, To, Date, etc.). Creates a new .eml file with _translated_{lang} suffix.

        Args:
            email_path: Path to original .eml file
            target_lang: Target language (ISO 639-1), default: German
            source_lang: Source language or 'auto' for detection

        Returns:
            TranslationResult: Result with translated file path

        Raises:
            FileNotFoundError: If email file not found
            Exception: If translation fails

        Example:
            >>> service = TranslationService()
            >>> result = await service.translate_email(
            ...     "public/documents/ACTE-2024-001/emails/Email.eml",
            ...     target_lang="de"
            ... )
            >>> print(result.translated_path)
        """
        path = Path(email_path)

        if not path.exists():
            logger.error(f"Email file not found: {email_path}")
            return TranslationResult(
                success=False,
                original_path=email_path,
                error=f"Email file not found: {email_path}"
            )

        try:
            # Parse original email
            from backend.services.email_service import get_email_service

            email_service = get_email_service()
            email_data = email_service.parse_eml_file(email_path)

            # Translate subject and body
            logger.info(f"Translating email to {target_lang}")

            translated_subject = await self.translate_text(
                email_data.subject,
                source_lang,
                target_lang
            )

            translated_body = await self.translate_text(
                email_data.body_text,
                source_lang,
                target_lang
            )

            # Create new email with translated content
            new_email = EmailMessage()
            new_email['From'] = email_data.from_addr
            new_email['To'] = email_data.to_addr
            new_email['Subject'] = translated_subject
            new_email['Date'] = email_data.date

            # Set translated body
            new_email.set_content(translated_body)

            # Generate output path
            translated_path = str(path).replace('.eml', f'_translated_{target_lang}.eml')

            # Save translated email
            with open(translated_path, 'wb') as f:
                f.write(new_email.as_bytes())

            logger.info(f"Translated email saved to: {translated_path}")

            return TranslationResult(
                success=True,
                original_path=email_path,
                translated_path=translated_path,
                source_language=source_lang,
                target_language=target_lang
            )

        except Exception as e:
            logger.error(f"Email translation failed: {e}")
            return TranslationResult(
                success=False,
                original_path=email_path,
                error=str(e)
            )

    def _get_language_name(self, lang_code: str) -> str:
        """
        Get full language name from ISO 639-1 code.

        Args:
            lang_code: ISO 639-1 language code

        Returns:
            str: Full language name
        """
        language_map = {
            'de': 'German',
            'en': 'English',
            'ar': 'Arabic',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'tr': 'Turkish',
            'ru': 'Russian',
        }
        return language_map.get(lang_code.lower(), lang_code.upper())


# Singleton instance
_translation_service_instance: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """
    Get the singleton instance of TranslationService.

    Returns:
        TranslationService: The translation service instance
    """
    global _translation_service_instance
    if _translation_service_instance is None:
        _translation_service_instance = TranslationService()
    return _translation_service_instance
