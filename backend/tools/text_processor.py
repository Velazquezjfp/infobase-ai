"""
S2-004: TextProcessor - Plain Text Document Handler.

This module implements the DocumentProcessor interface for plain text files (.txt).
It handles text extraction with proper encoding detection and metadata extraction.

Supported formats:
    - .txt (plain text)
    - .text (alternative extension)

Features:
    - Auto-detect encoding (UTF-8, Latin-1, ASCII, etc.)
    - Extract file metadata (size, timestamps, etc.)
    - Normalize line endings
    - Handle BOM markers
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from backend.tools.document_processor import (
    DocumentProcessor,
    DocumentMetadata,
    register_processor,
)

logger = logging.getLogger(__name__)


class TextProcessor(DocumentProcessor):
    """
    Processor for plain text documents (.txt files).

    Handles text extraction with encoding detection and proper
    metadata extraction from the file system.
    """

    SUPPORTED_EXTENSIONS: List[str] = [".txt", ".text"]
    CONTENT_TYPE = "text/plain"

    # Common encodings to try in order of preference
    ENCODINGS_TO_TRY: List[str] = [
        "utf-8",
        "utf-8-sig",  # UTF-8 with BOM
        "latin-1",    # ISO-8859-1 (Western European)
        "cp1252",     # Windows Western European
        "ascii",
    ]

    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a plain text file.

        Attempts multiple encodings to handle various text file formats.
        Normalizes line endings to Unix style (\\n).

        Args:
            file_path: Path to the text file.

        Returns:
            str: Extracted and normalized text content.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file cannot be decoded with any supported encoding.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(path.suffix):
            raise ValueError(f"Unsupported format: {path.suffix}")

        # Try each encoding until one works
        content = None
        used_encoding = None

        for encoding in self.ENCODINGS_TO_TRY:
            try:
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                logger.debug(f"Successfully read {path.name} with {encoding} encoding")
                break
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode {path.name} with {encoding}")
                continue
            except Exception as e:
                logger.warning(f"Error reading {path.name} with {encoding}: {e}")
                continue

        if content is None:
            raise ValueError(
                f"Could not decode {path.name} with any supported encoding. "
                f"Tried: {', '.join(self.ENCODINGS_TO_TRY)}"
            )

        # Normalize line endings
        content = self._normalize_line_endings(content)

        # Remove BOM if present (already handled by utf-8-sig, but just in case)
        content = self._remove_bom(content)

        logger.info(
            f"Extracted {len(content)} chars from {path.name} "
            f"(encoding: {used_encoding})"
        )

        return content

    def get_metadata(self, file_path: str) -> DocumentMetadata:
        """
        Extract metadata from a text file.

        Args:
            file_path: Path to the text file.

        Returns:
            DocumentMetadata: File metadata including size, timestamps, encoding.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = path.stat()

        # Detect encoding
        detected_encoding = self._detect_encoding(path)

        # Get file timestamps
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        created_at = None
        if hasattr(stat, "st_birthtime"):  # macOS
            created_at = datetime.fromtimestamp(stat.st_birthtime)
        elif hasattr(stat, "st_ctime"):  # Linux (inode change time, close to creation)
            created_at = datetime.fromtimestamp(stat.st_ctime)

        return DocumentMetadata(
            file_name=path.name,
            file_path=str(path.absolute()),
            file_size=stat.st_size,
            file_extension=path.suffix.lower(),
            created_at=created_at,
            modified_at=modified_at,
            content_type=self.CONTENT_TYPE,
            page_count=1,  # Text files are single-page
            encoding=detected_encoding,
            source="upload",
            extra={
                "lineCount": self._count_lines(path, detected_encoding),
            },
        )

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports the given file extension.

        Args:
            file_extension: File extension (with or without dot).

        Returns:
            bool: True if .txt or .text extension.
        """
        ext = file_extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        return ext in self.SUPPORTED_EXTENSIONS

    def _get_source_label(self) -> str:
        """Get human-readable source label for context tracking."""
        return "Text File"

    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize line endings to Unix style (\\n).

        Handles Windows (\\r\\n), old Mac (\\r), and Unix (\\n).

        Args:
            text: Text with potentially mixed line endings.

        Returns:
            str: Text with normalized Unix line endings.
        """
        # First convert CRLF to LF
        text = text.replace("\r\n", "\n")
        # Then convert remaining CR to LF (old Mac style)
        text = text.replace("\r", "\n")
        return text

    def _remove_bom(self, text: str) -> str:
        """
        Remove Byte Order Mark (BOM) if present at start of text.

        Args:
            text: Text that may start with BOM.

        Returns:
            str: Text without BOM.
        """
        # UTF-8 BOM
        if text.startswith("\ufeff"):
            return text[1:]
        return text

    def _detect_encoding(self, path: Path) -> Optional[str]:
        """
        Detect the encoding of a text file by trying to read it.

        Args:
            path: Path to the text file.

        Returns:
            Optional[str]: Detected encoding name or None.
        """
        for encoding in self.ENCODINGS_TO_TRY:
            try:
                with open(path, "r", encoding=encoding) as f:
                    f.read(1024)  # Read just first 1KB for detection
                return encoding
            except (UnicodeDecodeError, Exception):
                continue
        return None

    def _count_lines(self, path: Path, encoding: Optional[str]) -> int:
        """
        Count the number of lines in a text file.

        Args:
            path: Path to the text file.
            encoding: Detected encoding to use.

        Returns:
            int: Number of lines (0 if error).
        """
        try:
            enc = encoding or "utf-8"
            with open(path, "r", encoding=enc) as f:
                return sum(1 for _ in f)
        except Exception:
            return 0


# Register TextProcessor for its supported extensions
register_processor(TextProcessor.SUPPORTED_EXTENSIONS, TextProcessor)
