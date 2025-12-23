"""
Tools Layer - Reusable Stateless Functions.

This package contains pure utility functions that can be used across
services. Tools are stateless, have no external dependencies (except
standard library), and are designed for reusability.

Modules:
    - form_parser: Document-to-form field extraction (F-003)
    - document_processor: Abstract base class for document processors (S2-004)
    - text_processor: Plain text file processor (S2-004)
    - pdf_processor: PDF file processor stub (S2-004, Phase 3)

Tool Design Principles:
    - Pure Functions: Same input always produces same output
    - No Side Effects: Don't modify external state
    - No External Dependencies: Only use standard library and passed arguments
    - Type Safety: All functions have complete type hints
    - Testability: Easy to unit test in isolation

Example usage:
    ```python
    from tools.form_parser import extract_form_data
    from tools.document_processor import get_processor

    # Pure function call
    result = extract_form_data(document_text, form_schema)

    # S2-004: Document processing
    processor = get_processor("document.txt")
    if processor:
        text = processor.extract_text("path/to/document.txt")
    ```
"""

# S2-004: Import document processors to register them
from backend.tools.document_processor import (
    DocumentProcessor,
    DocumentMetadata,
    ExtractionResult,
    get_processor,
    get_supported_extensions,
    is_supported,
    register_processor,
)
from backend.tools.text_processor import TextProcessor
from backend.tools.pdf_processor import PDFProcessor

__all__: list[str] = [
    # Document processor base
    "DocumentProcessor",
    "DocumentMetadata",
    "ExtractionResult",
    "get_processor",
    "get_supported_extensions",
    "is_supported",
    "register_processor",
    # Concrete processors
    "TextProcessor",
    "PDFProcessor",
]
