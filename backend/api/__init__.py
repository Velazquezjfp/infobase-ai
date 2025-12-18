"""
API Layer - HTTP/WebSocket Protocol Handling.

This package contains FastAPI route handlers for the application.
Routes handle protocol-level concerns (request parsing, response formatting,
WebSocket connections) and delegate business logic to the services layer.

Modules:
    - chat: WebSocket endpoint for AI chat interactions (F-001)
    - admin: REST endpoints for admin operations (F-004)

The API layer should:
    - Parse and validate incoming requests using Pydantic models
    - Call appropriate service methods
    - Format and return responses
    - Handle protocol-specific errors (HTTP status codes, WebSocket close codes)

The API layer should NOT:
    - Contain business logic
    - Directly access data files
    - Make AI API calls directly
"""

__all__: list[str] = []
