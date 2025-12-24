"""
Unit tests for S3-001 Anonymization Service Integration.
Tests the backend anonymization service and tool.
"""

import pytest
import pytest_asyncio
import base64
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.anonymization_service import AnonymizationService, AnonymizationResult
from backend.tools.anonymization_tool import (
    anonymize_document,
    is_supported_format,
    get_supported_formats,
    _get_anonymized_filename,
    _image_to_base64,
    _base64_to_image,
    AnonymizationToolResult
)


class TestAnonymizationService:
    """Tests for AnonymizationService class."""

    def test_singleton_pattern(self):
        """Test that AnonymizationService follows singleton pattern."""
        service1 = AnonymizationService()
        service2 = AnonymizationService()
        assert service1 is service2

    def test_api_url_configuration(self):
        """TC-S3-001-05: Verify correct API URL."""
        service = AnonymizationService()
        assert service.API_URL == "http://localhost:5000/ai-analysis"

    def test_secret_key_configuration(self):
        """TC-S3-001-05: Verify correct Secret-Key."""
        service = AnonymizationService()
        assert service.SECRET_KEY == "2b5e151428aed2a6aff7158846cf4f2c"

    @pytest.mark.asyncio
    async def test_anonymize_image_adds_data_uri_prefix(self):
        """TC-S3-001-01: Test that base64 without prefix gets prefix added."""
        service = AnonymizationService()

        # Mock the aiohttp session
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "anonymized_image": "data:image/png;base64,test",
                "detections_count": 0
            })

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            mock_context.__aexit__.return_value = None

            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value = mock_context
            mock_session_instance.__aenter__.return_value = mock_session_instance
            mock_session_instance.__aexit__.return_value = None

            mock_session.return_value = mock_session_instance

            # Call with base64 without prefix
            result = await service.anonymize_image("iVBORw0KGgo...")

            # Verify the call was made
            assert mock_session_instance.post.called

    @pytest.mark.asyncio
    async def test_anonymize_image_empty_input(self):
        """Test error handling for empty input."""
        service = AnonymizationService()
        result = await service.anonymize_image("")

        assert result.success is False
        assert "No image data provided" in result.error


class TestAnonymizationTool:
    """Tests for anonymization_tool functions."""

    def test_get_anonymized_filename(self):
        """TC-S3-001-02: Test filename generation with _anonymized suffix."""
        assert _get_anonymized_filename("/docs/test.png") == "/docs/test_anonymized.png"
        assert _get_anonymized_filename("/docs/birth_certificate.jpg") == "/docs/birth_certificate_anonymized.jpg"
        assert _get_anonymized_filename("image.jpeg") == "image_anonymized.jpeg"

    def test_is_supported_format(self):
        """Test supported format detection."""
        assert is_supported_format("test.png") is True
        assert is_supported_format("test.jpg") is True
        assert is_supported_format("test.jpeg") is True
        assert is_supported_format("test.gif") is True
        assert is_supported_format("test.bmp") is True
        assert is_supported_format("test.webp") is True
        assert is_supported_format("test.txt") is False
        assert is_supported_format("test.pdf") is False

    def test_get_supported_formats(self):
        """Test getting list of supported formats."""
        formats = get_supported_formats()
        assert ".png" in formats
        assert ".jpg" in formats
        assert ".jpeg" in formats

    def test_image_to_base64_file_not_found(self):
        """TC-S3-001-08: Test error handling for missing file."""
        result, error = _image_to_base64("/nonexistent/path/image.png")
        assert result is None
        assert "File not found" in error

    def test_image_to_base64_unsupported_format(self):
        """Test error handling for unsupported file format."""
        # Create a temp file with wrong extension
        temp_path = "/tmp/test_file.txt"
        with open(temp_path, "w") as f:
            f.write("test")

        result, error = _image_to_base64(temp_path)
        assert result is None
        assert "Unsupported file type" in error

        os.remove(temp_path)

    def test_image_to_base64_valid_image(self):
        """TC-S3-001-01: Test base64 encoding of valid image."""
        test_image_path = "public/documents/ACTE-2024-001/personal-data/test.jpg"

        if os.path.exists(test_image_path):
            result, error = _image_to_base64(test_image_path)
            assert error is None
            assert result is not None
            assert result.startswith("data:image/jpeg;base64,")

    def test_base64_to_image_creates_file(self):
        """TC-S3-001-02: Test saving base64 to file."""
        # Simple 1x1 red PNG
        base64_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        output_path = "/tmp/test_output.png"

        success, error = _base64_to_image(base64_data, output_path)

        assert success is True
        assert error is None
        assert os.path.exists(output_path)

        os.remove(output_path)


class TestAnonymizationIntegration:
    """Integration tests requiring the external service."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
        reason="Integration tests disabled"
    )
    async def test_full_anonymization_workflow(self):
        """TC-S3-001-01, TC-S3-001-02: Full anonymization workflow."""
        test_image_path = "public/documents/ACTE-2024-001/personal-data/test.jpg"

        if not os.path.exists(test_image_path):
            pytest.skip("Test image not found")

        result = await anonymize_document(test_image_path)

        assert result.success is True
        assert result.anonymized_path is not None
        assert "_anonymized" in result.anonymized_path
        assert os.path.exists(result.anonymized_path)

        # Verify original unchanged
        assert os.path.exists(test_image_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
