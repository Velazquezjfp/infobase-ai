"""
Anonymization Tool for BAMF AI Case Management System.

This module provides a tool function for anonymizing document images.
It handles file I/O, base64 conversion, and coordinates with the
AnonymizationService to mask PII in identity documents.

The tool is designed to be used both directly and as an AI agent tool.
"""

import base64
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from backend.services.anonymization_service import AnonymizationService, AnonymizationResult

logger = logging.getLogger(__name__)

# Supported image formats for anonymization
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

# MIME types for data URI prefix
MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
}


@dataclass
class AnonymizationToolResult:
    """
    Result of the anonymization tool operation.

    Attributes:
        success: Whether the operation was successful.
        original_path: Path to the original document.
        anonymized_path: Path to the saved anonymized document.
        detections_count: Number of PII fields detected and masked.
        detection_labels: List of field names (labels) that were detected and masked.
        detections: Full detection data with field names and coordinates for overlay display.
        error: Error message if operation failed.
        render_metadata: S5-006: Render metadata for document registry (optional)
    """
    success: bool
    original_path: str
    anonymized_path: Optional[str] = None
    detections_count: int = 0
    detection_labels: Optional[list] = None
    detections: Optional[dict] = None
    error: Optional[str] = None
    render_metadata: Optional[dict] = None


def _get_anonymized_filename(original_path: str) -> str:
    """
    Generate the filename for the anonymized document.

    Adds '_anonymized' suffix before the file extension.

    Args:
        original_path: Path to the original file.

    Returns:
        str: Path for the anonymized file.

    Example:
        >>> _get_anonymized_filename("/docs/birth_certificate.png")
        '/docs/birth_certificate_anonymized.png'
    """
    path = Path(original_path)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    anonymized_name = f"{stem}_anonymized{suffix}"
    return str(parent / anonymized_name)


def _image_to_base64(file_path: str) -> tuple[Optional[str], Optional[str]]:
    """
    Convert an image file to base64 string with data URI prefix.

    Args:
        file_path: Path to the image file.

    Returns:
        tuple: (base64_string, error_message)
               base64_string is None if conversion failed.
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return None, f"File not found: {file_path}"

        extension = path.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            return None, f"Unsupported file type: {extension}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"

        # Read file and encode to base64
        with open(file_path, 'rb') as f:
            image_data = f.read()

        base64_data = base64.b64encode(image_data).decode('utf-8')

        # Add data URI prefix
        mime_type = MIME_TYPES.get(extension, 'image/png')
        base64_with_prefix = f"data:{mime_type};base64,{base64_data}"

        logger.info(f"Converted image to base64: {len(base64_data)} chars")
        return base64_with_prefix, None

    except PermissionError:
        return None, f"Permission denied reading file: {file_path}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def _base64_to_image(base64_string: str, output_path: str) -> tuple[bool, Optional[str]]:
    """
    Save a base64-encoded image to a file.

    Args:
        base64_string: Base64 string with or without data URI prefix.
        output_path: Path where the image should be saved.

    Returns:
        tuple: (success, error_message)
    """
    try:
        # Remove data URI prefix if present
        if ';base64,' in base64_string:
            base64_data = base64_string.split(';base64,')[1]
        else:
            base64_data = base64_string

        # Decode and write
        image_data = base64.b64decode(base64_data)

        # Ensure parent directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"Saved anonymized image to: {output_path}")
        return True, None

    except PermissionError:
        return False, f"Permission denied writing to: {output_path}"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


async def anonymize_document(
    file_path: str,
    document_id: str = None,
    register_render: bool = False
) -> AnonymizationToolResult:
    """
    Anonymize a document image by masking PII with black boxes.

    This function:
    1. Reads the image file and converts it to base64
    2. Sends it to the anonymization service
    3. Saves the anonymized result with '_anonymized' suffix
    4. Optionally registers the result as a render in document registry (S5-006)
    5. Returns the path to the anonymized file

    The original file remains unchanged.

    Args:
        file_path: Absolute or relative path to the image file.
                  Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP
        document_id: Optional document ID for render registration (S5-006)
        register_render: If True, register anonymized file as a render (requires document_id)

    Returns:
        AnonymizationToolResult: Result containing paths, detection count, and render metadata.

    Example:
        >>> result = await anonymize_document("/documents/ACTE-2024-001/personal-data/passport.png")
        >>> if result.success:
        ...     print(f"Anonymized file saved to: {result.anonymized_path}")
        ...     print(f"Masked {result.detections_count} PII fields")
        >>>
        >>> # S5-006: With render registration
        >>> result = await anonymize_document(
        ...     "/documents/ACTE-2024-001/personal-data/passport.png",
        ...     document_id="doc_001",
        ...     register_render=True
        ... )
        >>> print(result.render_metadata)
    """
    logger.info(f"Starting anonymization for: {file_path}")

    # Validate and convert image to base64
    base64_image, error = _image_to_base64(file_path)
    if error:
        logger.error(f"Failed to read image: {error}")
        return AnonymizationToolResult(
            success=False,
            original_path=file_path,
            error=error
        )

    # Call anonymization service
    service = AnonymizationService()
    result = await service.anonymize_image(base64_image)

    if not result.success:
        logger.error(f"Anonymization service failed: {result.error}")
        return AnonymizationToolResult(
            success=False,
            original_path=file_path,
            error=result.error
        )

    # Generate output path and save anonymized image
    anonymized_path = _get_anonymized_filename(file_path)

    save_success, save_error = _base64_to_image(
        result.anonymized_image,
        anonymized_path
    )

    if not save_success:
        logger.error(f"Failed to save anonymized image: {save_error}")
        return AnonymizationToolResult(
            success=False,
            original_path=file_path,
            error=save_error
        )

    logger.info(
        f"Anonymization complete - "
        f"detections: {result.detections_count}, "
        f"labels: {result.detection_labels}, "
        f"output: {anonymized_path}"
    )

    # S5-006: Optionally register as a render
    render_metadata = None
    if register_render and document_id:
        try:
            from backend.services.file_service import add_document_render
            # Include detection data in render metadata for label overlay display
            render_extra_metadata = {
                'detections': result.detections or {},
                'detectionLabels': result.detection_labels or [],
            }
            render_metadata = add_document_render(
                document_id=document_id,
                render_type='anonymized',
                file_path=anonymized_path,
                metadata=render_extra_metadata
            )
            logger.info(f"Registered anonymized render: {render_metadata['id']}")
        except Exception as e:
            logger.warning(f"Failed to register render (continuing anyway): {e}")
            # Don't fail the anonymization if render registration fails

    return AnonymizationToolResult(
        success=True,
        original_path=file_path,
        anonymized_path=anonymized_path,
        detections_count=result.detections_count,
        detection_labels=result.detection_labels or [],
        detections=result.detections or {},
        render_metadata=render_metadata
    )


def is_supported_format(file_path: str) -> bool:
    """
    Check if a file format is supported for anonymization.

    Args:
        file_path: Path to the file.

    Returns:
        bool: True if the file format is supported.
    """
    extension = Path(file_path).suffix.lower()
    return extension in SUPPORTED_EXTENSIONS


def get_supported_formats() -> list[str]:
    """
    Get list of supported file formats for anonymization.

    Returns:
        list[str]: List of supported file extensions.
    """
    return list(SUPPORTED_EXTENSIONS)
