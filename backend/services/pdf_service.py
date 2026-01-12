"""
S5-003: PDF Service - PDF Text Extraction for Semantic Search.

This module provides PDF text extraction services for the semantic search feature.
It extracts text content from PDF documents with position information for highlighting.

Features:
    - Full text extraction from PDF documents
    - Page-by-page text extraction with position data
    - Multi-page document support
    - Handles both searchable and text-based PDFs

Dependencies:
    - pdfplumber: For PDF text extraction and layout analysis
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import pdfplumber

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """
    Represents a block of text extracted from a PDF with position information.

    Attributes:
        text: The extracted text content
        page: Page number (1-indexed)
        position: Dictionary with x, y, width, height coordinates
        char_start: Starting character index in the full document text
        char_end: Ending character index in the full document text
    """
    text: str
    page: int
    position: Dict[str, float]
    char_start: int
    char_end: int


class PDFService:
    """
    Service for extracting text from PDF documents.

    This service provides methods for:
    - Extracting full text from PDFs
    - Extracting text with position information for highlighting
    - Handling multi-page documents
    - Processing PDF layout and structure
    """

    def __init__(self):
        """Initialize the PDF service."""
        logger.info("PDFService initialized")

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text content from a PDF document.

        This is a simplified method that extracts all text from all pages
        and concatenates them into a single string. Used for basic text
        processing and semantic search.

        Args:
            pdf_path: Path to the PDF file (absolute or relative)

        Returns:
            str: Extracted text content from all pages

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
            Exception: For other PDF processing errors

        Example:
            >>> service = PDFService()
            >>> text = service.extract_text("/path/to/document.pdf")
            >>> print(text[:100])
        """
        path = Path(pdf_path)

        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {pdf_path}")
            raise ValueError(f"File must be a PDF, got: {path.suffix}")

        try:
            text_parts = []

            with pdfplumber.open(path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing PDF: {path.name} ({total_pages} pages)")

                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from the page
                    page_text = page.extract_text()

                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                    else:
                        logger.warning(f"No text found on page {page_num}")

                full_text = "\n\n".join(text_parts)
                logger.info(
                    f"Successfully extracted {len(full_text)} characters "
                    f"from {total_pages} pages"
                )

                return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF {path.name}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_with_positions(self, pdf_path: str) -> List[TextBlock]:
        """
        Extract text from PDF with position information for each text block.

        This method extracts text along with bounding box coordinates for
        each text block. Useful for precise highlighting and text positioning
        in the UI.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List[TextBlock]: List of text blocks with position information

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
            Exception: For other PDF processing errors

        Example:
            >>> service = PDFService()
            >>> blocks = service.extract_text_with_positions("/path/to/doc.pdf")
            >>> for block in blocks[:3]:
            ...     print(f"Page {block.page}: {block.text[:50]}")
        """
        path = Path(pdf_path)

        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {pdf_path}")
            raise ValueError(f"File must be a PDF, got: {path.suffix}")

        try:
            text_blocks = []
            current_char_index = 0

            with pdfplumber.open(path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(
                    f"Processing PDF with positions: {path.name} ({total_pages} pages)"
                )

                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text with layout information
                    page_text = page.extract_text()

                    if page_text:
                        # Calculate character positions for this page
                        page_length = len(page_text)

                        # Get page dimensions for position information
                        page_width = page.width
                        page_height = page.height

                        # Create a text block for the entire page
                        # In a more advanced implementation, we could extract
                        # individual words or lines with their exact positions
                        text_block = TextBlock(
                            text=page_text,
                            page=page_num,
                            position={
                                'x': 0,
                                'y': 0,
                                'width': page_width,
                                'height': page_height
                            },
                            char_start=current_char_index,
                            char_end=current_char_index + page_length
                        )

                        text_blocks.append(text_block)
                        current_char_index += page_length + 2  # +2 for "\n\n" separator

                        logger.debug(
                            f"Page {page_num}: {page_length} chars "
                            f"(pos {text_block.char_start}-{text_block.char_end})"
                        )
                    else:
                        logger.warning(f"No text found on page {page_num}")

                logger.info(
                    f"Successfully extracted {len(text_blocks)} text blocks "
                    f"from {total_pages} pages"
                )

                return text_blocks

        except Exception as e:
            logger.error(
                f"Error extracting text with positions from PDF {path.name}: {str(e)}"
            )
            raise Exception(
                f"Failed to extract text with positions from PDF: {str(e)}"
            )

    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the number of pages in a PDF document.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            int: Number of pages in the PDF

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF, got: {path.suffix}")

        try:
            with pdfplumber.open(path) as pdf:
                page_count = len(pdf.pages)
                logger.info(f"PDF {path.name} has {page_count} pages")
                return page_count

        except Exception as e:
            logger.error(f"Error getting page count for PDF {path.name}: {str(e)}")
            raise Exception(f"Failed to get page count: {str(e)}")

    def extract_page_text(self, pdf_path: str, page_number: int) -> str:
        """
        Extract text from a specific page of a PDF.

        Args:
            pdf_path: Path to the PDF file
            page_number: Page number to extract (1-indexed)

        Returns:
            str: Extracted text from the specified page

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If page number is invalid
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with pdfplumber.open(path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise ValueError(
                        f"Invalid page number {page_number}. "
                        f"PDF has {len(pdf.pages)} pages."
                    )

                page = pdf.pages[page_number - 1]  # Convert to 0-indexed
                page_text = page.extract_text()

                if page_text:
                    logger.info(
                        f"Extracted {len(page_text)} chars from page {page_number}"
                    )
                    return page_text
                else:
                    logger.warning(f"No text found on page {page_number}")
                    return ""

        except Exception as e:
            logger.error(
                f"Error extracting text from page {page_number} of {path.name}: {str(e)}"
            )
            raise Exception(f"Failed to extract page text: {str(e)}")


# Create a singleton instance for convenience
_pdf_service_instance: Optional[PDFService] = None


def get_pdf_service() -> PDFService:
    """
    Get the singleton instance of PDFService.

    Returns:
        PDFService: The singleton PDF service instance
    """
    global _pdf_service_instance

    if _pdf_service_instance is None:
        _pdf_service_instance = PDFService()

    return _pdf_service_instance
