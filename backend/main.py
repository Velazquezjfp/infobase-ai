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
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
load_dotenv()

from backend.api.chat import router as chat_router
from backend.api.admin import router as admin_router
from backend.api.files import router as files_router
from backend.api.documents import router as documents_router
from backend.api.context import router as context_router  # S5-011
from backend.api.search import router as search_router  # S5-003
from backend.api.validation import router as validation_router  # Case validation
from backend.api.custom_context import router as custom_context_router  # S5-017
from backend.api.folders import router as folders_router  # Folder management
from backend.api.idirs import router as idirs_router  # IDIRS hybrid search & RAG

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

    # S5-015: Initialize test documents for ACTE-2024-001
    # DISABLED: Auto-initialization is disabled to allow starting with empty folders
    # Set INIT_TEST_DOCS=true to re-enable auto-initialization of test documents
    import os
    if os.getenv("INIT_TEST_DOCS", "false").lower() == "true":
        try:
            from backend.scripts.initialize_test_documents import (
                initialize_test_documents,
                cleanup_old_test_documents
            )

            logger.info("Running test document initialization...")

            # Clean up old .txt test files first
            deleted_count = cleanup_old_test_documents()
            if deleted_count > 0:
                logger.info(f"Removed {deleted_count} old test documents")

            # Copy new sample documents from root_docs
            stats = initialize_test_documents()
            if stats["copied"] > 0:
                logger.info(
                    f"Initialized {stats['copied']} test documents "
                    f"(skipped {stats['skipped']}, failed {stats['failed']})"
                )
            elif stats["skipped"] > 0:
                logger.debug(f"Test documents already initialized ({stats['skipped']} files exist)")

        except Exception as e:
            logger.warning(f"Test document initialization failed: {e}", exc_info=True)
            logger.info("Application will continue normally")
    else:
        logger.info("Test document auto-initialization is disabled (set INIT_TEST_DOCS=true to enable)")

    # S5-007: Document registry reconciliation on startup
    try:
        from backend.config import DOCUMENTS_BASE_PATH
        from backend.services.document_registry import (
            load_manifest,
            scan_filesystem,
            reconcile
        )

        logger.info("Starting document registry reconciliation...")

        # Load manifest
        manifest = load_manifest()
        logger.info(f"Loaded manifest with {len(manifest.documents)} documents")

        # Scan filesystem
        filesystem_files = scan_filesystem(DOCUMENTS_BASE_PATH)
        logger.info(f"Filesystem scan found {len(filesystem_files)} files")

        # Reconcile
        report = reconcile(manifest, filesystem_files)
        logger.info(
            f"Reconciliation complete: "
            f"{len(report.added)} added, "
            f"{len(report.missing)} missing, "
            f"{len(report.integrity_failed)} integrity failed"
        )

        # Log details if there were issues
        if report.missing:
            logger.warning(f"Missing files (in manifest but not on disk): {report.missing}")
        if report.integrity_failed:
            logger.warning(f"Files with integrity issues: {report.integrity_failed}")

    except Exception as e:
        logger.error(f"Document registry reconciliation failed: {e}", exc_info=True)
        logger.warning("Application will continue, but document persistence may be affected")

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

# S5-003: Mount static files for PDF viewing
# This allows the frontend PDFViewer to access PDFs at http://localhost:8000/root_docs/
app.mount("/root_docs", StaticFiles(directory="root_docs"), name="root_docs")

# S5-003: Mount documents directory for case PDFs
# This allows access to PDFs in case folders at http://localhost:8000/documents/
from pathlib import Path
from backend.config import DOCUMENTS_BASE_PATH
if Path(DOCUMENTS_BASE_PATH).exists():
    app.mount("/documents", StaticFiles(directory=DOCUMENTS_BASE_PATH), name="documents")

# Register API routers
app.include_router(chat_router, tags=["chat"])
app.include_router(admin_router, tags=["admin"])
app.include_router(files_router, tags=["files"])
app.include_router(documents_router, tags=["documents"])
app.include_router(context_router, tags=["context"])  # S5-011
app.include_router(search_router, prefix="/api/search", tags=["search"])  # S5-003
app.include_router(validation_router, prefix="/api/validation", tags=["validation"])  # Case validation
app.include_router(custom_context_router, tags=["custom-context"])  # S5-017
app.include_router(folders_router, tags=["folders"])  # Folder management
app.include_router(idirs_router, tags=["idirs"])  # IDIRS hybrid search & RAG


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
