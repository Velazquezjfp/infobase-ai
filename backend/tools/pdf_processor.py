"""
S2-004: PDFProcessor - PDF Document Handler (Stub for Phase 3).

This module provides a placeholder implementation for PDF processing.
Full PDF support (OCR, text extraction, metadata) will be implemented in Phase 3.

Current Status: STUB
    - Raises NotImplementedError for all operations
    - Registers .pdf extension for future support detection

Phase 3 Implementation Plan:
    - Use PyMuPDF (fitz) or pdfplumber for text extraction
    - Use pytesseract for OCR on image-based PDFs
    - Extract PDF metadata (author, title, creation date, etc.)
    - Handle multi-page documents with page tracking
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from backend.tools.document_processor import (
    DocumentProcessor,
    DocumentMetadata,
    register_processor,
)

logger = logging.getLogger(__name__)


class PDFProcessor(DocumentProcessor):
    """
    Processor for PDF documents (.pdf files).

    STUB IMPLEMENTATION - Full support planned for Phase 3.

    This processor is registered but will raise NotImplementedError
    for all operations until Phase 3 implementation.

    Phase 3 Features:
        - Text extraction from searchable PDFs
        - OCR for scanned/image PDFs
        - Multi-page document handling
        - PDF metadata extraction
        - Table extraction (optional)
    """

    SUPPORTED_EXTENSIONS: List[str] = [".pdf"]
    CONTENT_TYPE = "application/pdf"

    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.

        STUB: Raises NotImplementedError.
        Phase 3 will implement using PyMuPDF or similar library.

        Args:
            file_path: Path to the PDF file.

        Returns:
            str: Extracted text content.

        Raises:
            NotImplementedError: PDF support not yet implemented.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(path.suffix):
            raise ValueError(f"Unsupported format: {path.suffix}")

        logger.warning(
            f"PDF processing requested for {path.name}, "
            "but full PDF support is not yet implemented (Phase 3)"
        )

        raise NotImplementedError(
            "PDF text extraction is not yet implemented. "
            "Full PDF support (including OCR) is planned for Phase 3. "
            "For now, please upload text documents (.txt) or manually "
            "copy the relevant text content."
        )

    def get_metadata(self, file_path: str) -> DocumentMetadata:
        """
        Extract metadata from a PDF file.

        STUB: Returns basic file system metadata only.
        Phase 3 will extract PDF-specific metadata (author, title, etc.).

        Args:
            file_path: Path to the PDF file.

        Returns:
            DocumentMetadata: Basic file metadata (no PDF-specific data).

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = path.stat()

        # Get basic file timestamps
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        created_at = None
        if hasattr(stat, "st_birthtime"):
            created_at = datetime.fromtimestamp(stat.st_birthtime)
        elif hasattr(stat, "st_ctime"):
            created_at = datetime.fromtimestamp(stat.st_ctime)

        logger.info(
            f"Returning basic metadata for PDF {path.name}. "
            "Full PDF metadata extraction available in Phase 3."
        )

        return DocumentMetadata(
            file_name=path.name,
            file_path=str(path.absolute()),
            file_size=stat.st_size,
            file_extension=path.suffix.lower(),
            created_at=created_at,
            modified_at=modified_at,
            content_type=self.CONTENT_TYPE,
            page_count=0,  # Unknown until Phase 3
            encoding=None,
            source="upload",
            extra={
                "pdfSupport": "stub",
                "phase": "Phase 3 required for full support",
            },
        )

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports the given file extension.

        Args:
            file_extension: File extension (with or without dot).

        Returns:
            bool: True if .pdf extension.
        """
        ext = file_extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        return ext in self.SUPPORTED_EXTENSIONS

    def _get_source_label(self) -> str:
        """Get human-readable source label for context tracking."""
        return "PDF Document"


# Register PDFProcessor for its supported extensions
# Even as a stub, this allows the system to detect PDF files
# and provide appropriate user feedback
register_processor(PDFProcessor.SUPPORTED_EXTENSIONS, PDFProcessor)
