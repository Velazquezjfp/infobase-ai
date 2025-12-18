"""
Tools Layer - Reusable Stateless Functions.

This package contains pure utility functions that can be used across
services. Tools are stateless, have no external dependencies (except
standard library), and are designed for reusability.

Modules:
    - form_parser: Document-to-form field extraction (F-003)
    - document_processor: Document text processing utilities

Tool Design Principles:
    - Pure Functions: Same input always produces same output
    - No Side Effects: Don't modify external state
    - No External Dependencies: Only use standard library and passed arguments
    - Type Safety: All functions have complete type hints
    - Testability: Easy to unit test in isolation

Example usage:
    ```python
    from tools.form_parser import extract_form_data

    # Pure function call
    result = extract_form_data(document_text, form_schema)
    ```
"""

__all__: list[str] = []
