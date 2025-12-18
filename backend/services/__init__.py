"""
Services Layer - Business Logic.

This package contains service classes that implement the core business logic
of the application. Services are designed with dependency injection to
enable testing and flexibility.

Modules:
    - gemini_service: Google Gemini API integration for AI responses (F-001)
    - context_manager: Case-instance scoped context loading and merging (F-002)
    - field_generator: AI-powered form field generation (F-004)

Service Design Principles:
    - Single Responsibility: Each service handles one domain concern
    - Dependency Injection: Services accept dependencies via __init__
    - Case Isolation: Context operations are scoped to case IDs
    - Stateless Operations: Services don't maintain conversation state
    - Type Safety: All methods have type hints
    - Documentation: All methods have docstrings with Args, Returns, Raises

Example usage:
    ```python
    from services.gemini_service import GeminiService
    from services.context_manager import ContextManager

    # Inject dependencies
    gemini = GeminiService(api_key="...")
    context_mgr = ContextManager()

    # Load case-scoped context
    case_ctx = context_mgr.load_case_context("ACTE-2024-001")
    folder_ctx = context_mgr.load_folder_context("ACTE-2024-001", "personal-data")

    # Use service methods with case context
    response = await gemini.generate_response(prompt, case_ctx, folder_ctx)
    ```
"""

__all__: list[str] = []
