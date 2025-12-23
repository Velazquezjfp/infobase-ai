"""
S2-004: Multi-Format Contextual Extraction - Document Processor Base Class.

This module provides an abstract base class for document processors that handle
different file formats. It enables extracting text content and metadata from
various document types (TXT, PDF, etc.) with a unified interface.

Architecture:
    DocumentProcessor (ABC)
        ├── TextProcessor  - Handles .txt files
        └── PDFProcessor   - Handles .pdf files (stub for Phase 3)

Usage:
    ```python
    from backend.tools.document_processor import get_processor

    # Get appropriate processor for file type
    processor = get_processor("document.txt")
    text = processor.extract_text("path/to/document.txt")
    metadata = processor.get_metadata("path/to/document.txt")
    ```
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Type

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """
    Standardized metadata structure for all document types.

    Attributes:
        file_name: Original file name
        file_path: Full path to the file
        file_size: Size in bytes
        file_extension: File extension (e.g., '.txt', '.pdf')
        created_at: File creation timestamp (if available)
        modified_at: File modification timestamp
        content_type: MIME type of the document
        page_count: Number of pages (for paginated documents)
        encoding: Character encoding (for text documents)
        source: How the document was obtained ('upload', 'import', etc.)
        extra: Additional format-specific metadata
    """
    file_name: str
    file_path: str
    file_size: int
    file_extension: str
    modified_at: datetime
    content_type: str
    created_at: Optional[datetime] = None
    page_count: int = 1
    encoding: Optional[str] = None
    source: str = "upload"
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "fileName": self.file_name,
            "filePath": self.file_path,
            "fileSize": self.file_size,
            "fileExtension": self.file_extension,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "modifiedAt": self.modified_at.isoformat(),
            "contentType": self.content_type,
            "pageCount": self.page_count,
            "encoding": self.encoding,
            "source": self.source,
            **self.extra,
        }


@dataclass
class ExtractionResult:
    """
    Result of document text extraction.

    Attributes:
        text: Extracted text content
        metadata: Document metadata
        success: Whether extraction succeeded
        error: Error message if extraction failed
        source_label: Human-readable source label for context tracking
    """
    text: str
    metadata: DocumentMetadata
    success: bool = True
    error: Optional[str] = None
    source_label: str = "Document"

    @property
    def context_source(self) -> str:
        """Get formatted source for context tracking (S2-004)."""
        return f"[{self.source_label}: {self.metadata.file_name}]"


class DocumentProcessor(ABC):
    """
    Abstract base class for document processors.

    This class defines the interface that all document format processors
    must implement. It provides a unified way to extract text and metadata
    from different document types.

    Subclasses must implement:
        - extract_text(): Extract text content from a document
        - get_metadata(): Extract metadata from a document
        - supports_format(): Check if processor handles a file extension
    """

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a document.

        Args:
            file_path: Path to the document file.

        Returns:
            str: Extracted text content.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file format is not supported.
            IOError: If file cannot be read.
        """
        pass

    @abstractmethod
    def get_metadata(self, file_path: str) -> DocumentMetadata:
        """
        Extract metadata from a document.

        Args:
            file_path: Path to the document file.

        Returns:
            DocumentMetadata: Standardized metadata object.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        pass

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports a given file extension.

        Args:
            file_extension: File extension including dot (e.g., '.txt', '.pdf').

        Returns:
            bool: True if format is supported.
        """
        pass

    def process(self, file_path: str) -> ExtractionResult:
        """
        Full processing: extract text and metadata with error handling.

        This is a template method that combines extract_text and get_metadata
        with proper error handling and logging.

        Args:
            file_path: Path to the document file.

        Returns:
            ExtractionResult: Contains text, metadata, and success status.
        """
        path = Path(file_path)

        # Validate file exists
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return ExtractionResult(
                text="",
                metadata=self._empty_metadata(file_path),
                success=False,
                error=f"File not found: {file_path}",
            )

        # Validate format is supported
        if not self.supports_format(path.suffix.lower()):
            logger.error(f"Unsupported format: {path.suffix}")
            return ExtractionResult(
                text="",
                metadata=self._empty_metadata(file_path),
                success=False,
                error=f"Unsupported format: {path.suffix}",
            )

        try:
            # Extract metadata first (lighter operation)
            metadata = self.get_metadata(file_path)

            # Extract text content
            text = self.extract_text(file_path)

            logger.info(
                f"Successfully processed {path.name}: "
                f"{len(text)} chars, {metadata.page_count} page(s)"
            )

            return ExtractionResult(
                text=text,
                metadata=metadata,
                success=True,
                source_label=self._get_source_label(),
            )

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return ExtractionResult(
                text="",
                metadata=self._empty_metadata(file_path),
                success=False,
                error=str(e),
            )

    def _empty_metadata(self, file_path: str) -> DocumentMetadata:
        """Create empty metadata for error cases."""
        path = Path(file_path)
        return DocumentMetadata(
            file_name=path.name,
            file_path=str(path),
            file_size=0,
            file_extension=path.suffix.lower(),
            modified_at=datetime.now(),
            content_type="application/octet-stream",
        )

    def _get_source_label(self) -> str:
        """Get human-readable source label for this processor type."""
        return "Document"


# Registry of available processors
_processor_registry: Dict[str, Type[DocumentProcessor]] = {}


def register_processor(extensions: List[str], processor_class: Type[DocumentProcessor]):
    """
    Register a processor class for specific file extensions.

    Args:
        extensions: List of extensions this processor handles (e.g., ['.txt', '.text'])
        processor_class: The processor class to register.
    """
    for ext in extensions:
        ext_lower = ext.lower() if ext.startswith('.') else f".{ext.lower()}"
        _processor_registry[ext_lower] = processor_class
        logger.debug(f"Registered {processor_class.__name__} for {ext_lower}")


def get_processor(file_path: str) -> Optional[DocumentProcessor]:
    """
    Get the appropriate processor for a file based on its extension.

    Args:
        file_path: Path to the file or just filename with extension.

    Returns:
        Optional[DocumentProcessor]: Instantiated processor or None if unsupported.

    Example:
        >>> processor = get_processor("document.txt")
        >>> if processor:
        ...     text = processor.extract_text("path/to/document.txt")
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    processor_class = _processor_registry.get(ext)
    if processor_class:
        return processor_class()

    logger.warning(f"No processor registered for extension: {ext}")
    return None


def get_supported_extensions() -> List[str]:
    """
    Get list of all supported file extensions.

    Returns:
        List[str]: Supported extensions (e.g., ['.txt', '.pdf']).
    """
    return list(_processor_registry.keys())


def is_supported(file_path: str) -> bool:
    """
    Check if a file type is supported.

    Args:
        file_path: Path to file or filename.

    Returns:
        bool: True if file type is supported.
    """
    ext = Path(file_path).suffix.lower()
    return ext in _processor_registry
