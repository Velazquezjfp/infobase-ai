"""
BAMF AI Case Management System - FastAPI Backend Entry Point.

This module initializes the FastAPI application with CORS middleware,
health check endpoints, and event handlers for startup/shutdown.

The backend follows clean architecture with separation of concerns:
- API layer (api/): HTTP/WebSocket protocol handling
- Service layer (services/): Business logic
- Tools layer (tools/): Reusable stateless functions
- Data layer (data/): Configuration files and context data
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

from backend.api.chat import router as chat_router
from backend.api.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifespan events.

    Handles startup and shutdown events for the FastAPI application.
    Use this for initializing and cleaning up resources like database
    connections, AI service clients, etc.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is yielded to the application during its lifetime.
    """
    # Startup
    logger.info("Starting BAMF AI Case Management Backend...")
    logger.info("Backend initialization complete.")

    yield

    # Shutdown
    logger.info("Shutting down BAMF AI Case Management Backend...")
    logger.info("Backend shutdown complete.")


# Initialize FastAPI application
app = FastAPI(
    title="BAMF AI Case Management API",
    description="Backend API for AI-powered case management system",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS middleware
# Allow frontend development server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Vite dev server (configured port)
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Vite alternate port
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat_router, tags=["chat"])
app.include_router(admin_router, tags=["admin"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns the current status of the backend service.
    Used for monitoring and load balancer health checks.

    Returns:
        dict[str, str]: A dictionary containing the service status.
    """
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Provides basic API information.

    Returns:
        dict[str, str]: A dictionary with API name and version.
    """
    return {
        "name": "BAMF AI Case Management API",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
