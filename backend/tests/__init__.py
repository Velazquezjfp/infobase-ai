"""
Tests Package - Unit and Integration Tests.

This package contains tests for the backend application.
Tests are organized to mirror the source code structure.

Test Organization:
    tests/
    ├── test_api/           # API endpoint tests
    ├── test_services/      # Service unit tests
    ├── test_tools/         # Tool function tests
    └── conftest.py         # Shared pytest fixtures

Testing Principles:
    - Unit Tests: Test individual functions/methods in isolation
    - Integration Tests: Test service interactions
    - Mocking: Use dependency injection to mock external services
    - Type Checking: Run mypy as part of test suite
    - Style Checking: Run pylint as part of test suite

Running Tests:
    ```bash
    cd backend
    pytest
    pytest --cov=. --cov-report=html  # With coverage
    mypy .                             # Type checking
    pylint api services tools          # Style checking
    ```
"""

__all__: list[str] = []
