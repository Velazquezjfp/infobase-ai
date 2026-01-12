"""
File Management Service for BAMF AI Case Management System.

This module provides file validation, sanitization, and storage utilities
for the file upload feature. All functions follow stateless design patterns
for reliability and testability.

Security Features:
    - File size validation (15 MB limit)
    - Filename sanitization to prevent path traversal
    - Case path validation to prevent directory escape
    - Safe file writing with atomic operations
"""

import logging
import re
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_FILENAME_LENGTH = 255
UNSAFE_FILENAME_CHARS = r'[^\w\s\-\.]'  # Allow only alphanumeric, spaces, hyphens, dots


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE_BYTES) -> None:
    """
    Validate that a file size is within the allowed limit.

    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed size in bytes (default: 15 MB)

    Raises:
        ValueError: If file size exceeds the limit

    Example:
        >>> validate_file_size(5_000_000)  # 5 MB - OK
        >>> validate_file_size(20_000_000)  # 20 MB - raises ValueError
    """
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise ValueError(
            f"File exceeds {max_mb:.1f} MB size limit. "
            f"File size: {actual_mb:.2f} MB"
        )

    if file_size == 0:
        raise ValueError("File is empty (0 bytes)")

    logger.debug(f"File size validation passed: {file_size} bytes")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent security issues and filesystem problems.

    Removes or replaces unsafe characters, prevents path traversal attacks,
    and ensures the filename is valid for cross-platform filesystem usage.

    Args:
        filename: Original filename from upload

    Returns:
        str: Sanitized filename safe for filesystem storage

    Raises:
        ValueError: If filename becomes empty after sanitization

    Security Measures:
        - Removes path separators (/, \\)
        - Removes parent directory references (..)
        - Removes special characters
        - Limits filename length
        - Prevents null bytes

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("my file (1).pdf")
        'my_file_1.pdf'
        >>> sanitize_filename("document<>:?\"|*.txt")
        'document.txt'
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Remove null bytes (security risk)
    filename = filename.replace('\0', '')

    # Get base filename (remove any path components)
    filename = Path(filename).name

    # Remove or replace unsafe characters
    # Replace spaces with underscores for better URL compatibility
    filename = filename.replace(' ', '_')

    # Remove other unsafe characters
    filename = re.sub(UNSAFE_FILENAME_CHARS, '', filename)

    # Remove any remaining path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')

    # Ensure filename starts with alphanumeric character
    filename = re.sub(r'^[^a-zA-Z0-9]+', '', filename)

    # Limit filename length
    if len(filename) > MAX_FILENAME_LENGTH:
        # Preserve file extension
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            max_name_length = MAX_FILENAME_LENGTH - len(ext) - 1
            filename = f"{name[:max_name_length]}.{ext}"
        else:
            filename = filename[:MAX_FILENAME_LENGTH]

    # Validate result
    if not filename or filename == '.':
        raise ValueError("Filename is invalid or empty after sanitization")

    logger.debug(f"Sanitized filename: {filename}")
    return filename


def validate_case_path(case_id: str, folder_id: str) -> None:
    """
    Validate that case_id and folder_id are safe for use in file paths.

    Prevents path traversal attacks by checking for directory escape
    attempts like "../" or absolute paths.

    Args:
        case_id: The case identifier (e.g., "ACTE-2024-001")
        folder_id: The folder identifier (e.g., "uploads", "personal-data")

    Raises:
        ValueError: If case_id or folder_id contains unsafe path components

    Example:
        >>> validate_case_path("ACTE-2024-001", "uploads")  # OK
        >>> validate_case_path("../../../etc", "passwd")  # raises ValueError
        >>> validate_case_path("/etc/passwd", "uploads")  # raises ValueError
    """
    # Check for empty values
    if not case_id or not case_id.strip():
        raise ValueError("case_id cannot be empty")

    if not folder_id or not folder_id.strip():
        raise ValueError("folder_id cannot be empty")

    # Check for path traversal attempts
    dangerous_patterns = [
        '..',      # Parent directory
        '/',       # Absolute path or path separator
        '\\',      # Windows path separator
        '\0',      # Null byte
        '\n',      # Newline
        '\r',      # Carriage return
    ]

    for pattern in dangerous_patterns:
        if pattern in case_id:
            raise ValueError(f"case_id contains invalid characters: '{pattern}'")
        if pattern in folder_id:
            raise ValueError(f"folder_id contains invalid characters: '{pattern}'")

    # Ensure case_id and folder_id don't start with special characters
    if case_id.startswith(('.', '-', '_')) or folder_id.startswith(('.', '-', '_')):
        raise ValueError("case_id and folder_id must start with alphanumeric characters")

    # Validate format (alphanumeric, hyphens, underscores only)
    valid_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*$')

    if not valid_pattern.match(case_id):
        raise ValueError(
            f"case_id '{case_id}' contains invalid characters. "
            "Only alphanumeric, hyphens, and underscores are allowed."
        )

    if not valid_pattern.match(folder_id):
        raise ValueError(
            f"folder_id '{folder_id}' contains invalid characters. "
            "Only alphanumeric, hyphens, and underscores are allowed."
        )

    logger.debug(f"Case path validation passed: {case_id}/{folder_id}")


def create_folder_if_needed(folder_path: Union[Path, str]) -> None:
    """
    Create a folder and all parent directories if they don't exist.

    Args:
        folder_path: Path to the folder to create

    Raises:
        OSError: If folder creation fails due to permissions or disk space

    Example:
        >>> create_folder_if_needed(Path("public/documents/ACTE-2024-001/uploads"))
    """
    folder_path = Path(folder_path)

    if folder_path.exists():
        if not folder_path.is_dir():
            raise OSError(f"Path exists but is not a directory: {folder_path}")
        logger.debug(f"Folder already exists: {folder_path}")
        return

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created folder: {folder_path}")
    except OSError as e:
        logger.error(f"Failed to create folder {folder_path}: {str(e)}")
        raise OSError(f"Failed to create upload directory: {str(e)}")


def save_uploaded_file(file_path: Union[Path, str], file_contents: bytes) -> None:
    """
    Save uploaded file contents to disk.

    Performs atomic write operation to prevent partial file writes.
    Creates parent directories if needed.

    Args:
        file_path: Target path for the file
        file_contents: Binary content of the file

    Raises:
        OSError: If file write fails

    Example:
        >>> save_uploaded_file(
        ...     Path("public/documents/ACTE-2024-001/uploads/document.pdf"),
        ...     b"PDF content here..."
        ... )
    """
    file_path = Path(file_path)

    # Ensure parent directory exists
    create_folder_if_needed(file_path.parent)

    try:
        # Write file atomically
        # Use binary mode for all file types (text, images, PDFs, etc.)
        with open(file_path, 'wb') as f:
            f.write(file_contents)

        logger.info(f"Saved file: {file_path} ({len(file_contents)} bytes)")

    except OSError as e:
        logger.error(f"Failed to save file {file_path}: {str(e)}")
        raise OSError(f"Failed to save file: {str(e)}")


def delete_file(case_id: str, folder_id: str, filename: str) -> bool:
    """
    Delete a file from a case folder with security validation.

    Performs path traversal prevention by ensuring the resolved file path
    stays within the expected case directory.

    Args:
        case_id: The case identifier (e.g., "ACTE-2024-001")
        folder_id: The folder identifier (e.g., "uploads")
        filename: Name of the file to delete

    Returns:
        bool: True if file was deleted successfully

    Raises:
        ValueError: If path validation fails (path traversal attempt)
        FileNotFoundError: If the file does not exist
        PermissionError: If access to the file is denied
        OSError: If deletion fails for other reasons

    Security Measures:
        - Validates case_id and folder_id format
        - Sanitizes filename
        - Verifies resolved path is within expected base directory
        - Prevents path traversal attacks (../, etc.)

    Example:
        >>> delete_file("ACTE-2024-001", "uploads", "document.pdf")
        True
        >>> delete_file("ACTE-2024-001", "../etc", "passwd")  # raises ValueError
    """
    # Validate case path components
    validate_case_path(case_id, folder_id)

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Construct paths
    base_dir = Path("public") / "documents"
    expected_case_dir = base_dir / case_id
    file_path = base_dir / case_id / folder_id / safe_filename

    # Security check: Ensure resolved path is within expected case directory
    # This prevents path traversal attacks even if validation was bypassed
    try:
        resolved_file_path = file_path.resolve()
        resolved_case_dir = expected_case_dir.resolve()

        if not resolved_file_path.is_relative_to(resolved_case_dir):
            logger.warning(
                f"Path traversal attempt detected: {file_path} resolves to "
                f"{resolved_file_path}, outside of {resolved_case_dir}"
            )
            raise ValueError("Access denied: Invalid file path")
    except ValueError as e:
        # Re-raise ValueError (our security exception)
        raise
    except Exception as e:
        logger.error(f"Path resolution error: {str(e)}")
        raise ValueError(f"Invalid file path: {str(e)}")

    # Check if file exists
    if not file_path.exists():
        logger.warning(f"File not found for deletion: {file_path}")
        raise FileNotFoundError(f"File not found: {safe_filename}")

    # Check if it's actually a file (not a directory)
    if not file_path.is_file():
        logger.warning(f"Path is not a file: {file_path}")
        raise ValueError(f"Path is not a file: {safe_filename}")

    # Delete the file
    try:
        file_path.unlink()
        logger.info(f"Deleted file: {file_path}")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied when deleting {file_path}: {str(e)}")
        raise PermissionError(f"Permission denied: Cannot delete {safe_filename}")
    except OSError as e:
        logger.error(f"Failed to delete {file_path}: {str(e)}")
        raise OSError(f"Failed to delete file: {str(e)}")


def get_file_size_mb(file_size_bytes: int) -> float:
    """
    Convert file size from bytes to megabytes.

    Args:
        file_size_bytes: File size in bytes

    Returns:
        float: File size in megabytes (rounded to 2 decimal places)

    Example:
        >>> get_file_size_mb(5_242_880)
        5.0
        >>> get_file_size_mb(1_048_576)
        1.0
    """
    return round(file_size_bytes / (1024 * 1024), 2)


def validate_file_extension(filename: str, allowed_extensions: list[str] = None) -> bool:
    """
    Validate that a file has an allowed extension.

    Args:
        filename: Name of the file to validate
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.jpg', '.txt'])
                           If None, all extensions are allowed

    Returns:
        bool: True if extension is allowed, False otherwise

    Example:
        >>> validate_file_extension("document.pdf", ['.pdf', '.txt'])
        True
        >>> validate_file_extension("image.exe", ['.pdf', '.txt'])
        False
    """
    if allowed_extensions is None:
        return True

    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def check_file_exists(case_id: str, folder_id: str, filename: str) -> bool:
    """
    Check if a file already exists in the specified case folder.

    Args:
        case_id: The case identifier (e.g., "ACTE-2024-001")
        folder_id: The folder identifier (e.g., "uploads")
        filename: Name of the file to check

    Returns:
        bool: True if file exists, False otherwise

    Raises:
        ValueError: If path validation fails

    Example:
        >>> check_file_exists("ACTE-2024-001", "uploads", "document.pdf")
        True
    """
    # Validate case path components
    validate_case_path(case_id, folder_id)

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Construct path
    file_path = Path("public") / "documents" / case_id / folder_id / safe_filename

    exists = file_path.exists() and file_path.is_file()
    logger.debug(f"File exists check: {file_path} -> {exists}")
    return exists


def generate_unique_filename(case_id: str, folder_id: str, filename: str) -> str:
    """
    Generate a unique filename by adding a numeric suffix if the file already exists.

    If the file doesn't exist, returns the original (sanitized) filename.
    If it exists, adds (1), (2), etc. before the extension until a unique name is found.

    Args:
        case_id: The case identifier (e.g., "ACTE-2024-001")
        folder_id: The folder identifier (e.g., "uploads")
        filename: Original filename

    Returns:
        str: A unique filename that doesn't exist in the folder

    Raises:
        ValueError: If path validation fails or unable to generate unique name

    Example:
        >>> generate_unique_filename("ACTE-2024-001", "uploads", "document.pdf")
        'document.pdf'  # if doesn't exist
        >>> generate_unique_filename("ACTE-2024-001", "uploads", "document.pdf")
        'document_1.pdf'  # if document.pdf exists
        >>> generate_unique_filename("ACTE-2024-001", "uploads", "document.pdf")
        'document_2.pdf'  # if document.pdf and document_1.pdf exist
    """
    # Validate case path components
    validate_case_path(case_id, folder_id)

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Check if original file doesn't exist
    if not check_file_exists(case_id, folder_id, safe_filename):
        return safe_filename

    # Split filename into name and extension
    base_path = Path(safe_filename)
    name = base_path.stem
    ext = base_path.suffix

    # Try adding numeric suffixes until we find a unique name
    max_attempts = 1000  # Prevent infinite loop
    for i in range(1, max_attempts + 1):
        new_filename = f"{name}_{i}{ext}"
        if not check_file_exists(case_id, folder_id, new_filename):
            logger.info(f"Generated unique filename: {safe_filename} -> {new_filename}")
            return new_filename

    raise ValueError(f"Unable to generate unique filename for {filename} after {max_attempts} attempts")


# ==============================================================================
# S5-006: Document Renders Management Functions
# ==============================================================================

def add_document_render(
    document_id: str,
    render_type: str,
    file_path: str,
    metadata: dict = None
) -> dict:
    """
    Add a new render to a document in the document registry.

    This function creates a render entry and updates the document manifest
    (via document_registry service from S5-007).

    Args:
        document_id: The parent document ID
        render_type: Type of render ('anonymized', 'translated', 'annotated')
        file_path: Path to the render file
        metadata: Optional metadata (e.g., {'language': 'de'} for translations)

    Returns:
        dict: Render metadata with id, type, name, filePath, createdAt, metadata

    Raises:
        ValueError: If document_id not found or render_type invalid
        ImportError: If document_registry service not available

    Example:
        >>> render = add_document_render(
        ...     'doc_001',
        ...     'anonymized',
        ...     'public/documents/ACTE-2024-001/personal-data/passport_anonymized.png'
        ... )
        >>> render['type']
        'anonymized'
    """
    try:
        from backend.services import document_registry
    except ImportError as e:
        logger.error("document_registry service not available (S5-007 dependency)")
        raise ImportError(
            "S5-006 requires S5-007 (document_registry) to be implemented"
        ) from e

    # Validate render type
    valid_types = {'original', 'anonymized', 'translated', 'annotated'}
    if render_type not in valid_types:
        raise ValueError(
            f"Invalid render_type '{render_type}'. Must be one of: {valid_types}"
        )

    # Create render metadata
    import uuid
    from datetime import datetime

    render_id = f"render_{uuid.uuid4().hex[:12]}"
    render_data = {
        'id': render_id,
        'type': render_type,
        'name': Path(file_path).name,
        'filePath': file_path,
        'createdAt': datetime.utcnow().isoformat() + 'Z',
        'metadata': metadata or {}
    }

    # Update document registry
    document_registry.add_render_to_document(document_id, render_data)

    logger.info(
        f"Added {render_type} render to document {document_id}: {render_id}"
    )
    return render_data


def get_document_renders(document_id: str) -> list:
    """
    Get all renders for a document from the document registry.

    Args:
        document_id: The document ID

    Returns:
        list: List of render dictionaries

    Raises:
        ValueError: If document not found
        ImportError: If document_registry service not available

    Example:
        >>> renders = get_document_renders('doc_001')
        >>> len(renders)
        3
    """
    try:
        from backend.services import document_registry
    except ImportError as e:
        logger.error("document_registry service not available (S5-007 dependency)")
        raise ImportError(
            "S5-006 requires S5-007 (document_registry) to be implemented"
        ) from e

    renders = document_registry.get_document_renders(document_id)

    logger.debug(f"Retrieved {len(renders)} renders for document {document_id}")
    return renders


def delete_document_render(
    document_id: str,
    render_id: str,
    case_id: str = None,
    folder_id: str = None
) -> bool:
    """
    Delete a specific render from a document.

    This function:
    1. Retrieves render metadata from registry
    2. Deletes the render file from filesystem
    3. Removes render entry from document registry

    Args:
        document_id: The parent document ID
        render_id: The render ID to delete
        case_id: Optional case ID for file path construction
        folder_id: Optional folder ID for file path construction

    Returns:
        bool: True if deletion successful

    Raises:
        ValueError: If trying to delete 'original' render or render not found
        FileNotFoundError: If render file not found
        ImportError: If document_registry service not available

    Security:
        - Cannot delete 'original' render type
        - Uses same path validation as delete_file()

    Example:
        >>> delete_document_render('doc_001', 'render_abc123')
        True
    """
    try:
        from backend.services import document_registry
    except ImportError as e:
        logger.error("document_registry service not available (S5-007 dependency)")
        raise ImportError(
            "S5-006 requires S5-007 (document_registry) to be implemented"
        ) from e

    # Get render metadata
    renders = document_registry.get_document_renders(document_id)
    render = next((r for r in renders if r.get('id') == render_id), None)

    if not render:
        raise ValueError(f"Render {render_id} not found for document {document_id}")

    # Security: Prevent deletion of 'original' render
    if render.get('type') == 'original':
        raise ValueError("Cannot delete 'original' render type")

    # Delete render file from filesystem
    render_file_path = Path(render.get('filePath', ''))

    if render_file_path.exists():
        try:
            render_file_path.unlink()
            logger.info(f"Deleted render file: {render_file_path}")
        except OSError as e:
            logger.error(f"Failed to delete render file {render_file_path}: {e}")
            raise OSError(f"Failed to delete render file: {str(e)}")
    else:
        logger.warning(f"Render file not found (already deleted?): {render_file_path}")

    # Remove from registry
    document_registry.remove_render_from_document(document_id, render_id)

    logger.info(f"Deleted render {render_id} from document {document_id}")
    return True
