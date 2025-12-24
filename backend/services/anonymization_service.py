"""
Anonymization Service for BAMF AI Case Management System.

This module provides integration with an external PII anonymization service
that detects and masks personally identifiable information in identity documents
such as passports, birth certificates, and driving licenses.

The service uses black box masking over sensitive fields and returns
the anonymized image as base64.
"""

import logging
import aiohttp
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AnonymizationResult:
    """
    Result of an anonymization operation.

    Attributes:
        success: Whether the anonymization was successful.
        anonymized_image: Base64-encoded anonymized image with data URI prefix.
        detections_count: Number of PII detections found and masked.
        error: Error message if anonymization failed.
    """
    success: bool
    anonymized_image: Optional[str] = None
    detections_count: int = 0
    error: Optional[str] = None


class AnonymizationService:
    """
    Service class for interacting with the external PII anonymization API.

    This service handles:
    - Sending document images to the anonymization service
    - Receiving anonymized images with PII masked
    - Error handling for service unavailability

    The external service runs a self-contained trained model for privacy.
    """

    API_URL = "http://localhost:5000/ai-analysis"
    SECRET_KEY = "2b5e151428aed2a6aff7158846cf4f2c"
    TIMEOUT_SECONDS = 30

    _instance: Optional['AnonymizationService'] = None

    def __new__(cls) -> 'AnonymizationService':
        """
        Implement singleton pattern for AnonymizationService.

        Returns:
            AnonymizationService: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def anonymize_image(self, base64_image: str) -> AnonymizationResult:
        """
        Send an image to the anonymization service and receive the masked result.

        The service detects PII in identity documents and applies black box
        masking over sensitive fields like names, dates, photos, and ID numbers.

        Args:
            base64_image: Base64-encoded image with data URI prefix
                         (e.g., "data:image/png;base64,iVBORw0KGgo...")

        Returns:
            AnonymizationResult: Result containing the anonymized image or error.

        Example:
            >>> service = AnonymizationService()
            >>> result = await service.anonymize_image("data:image/png;base64,...")
            >>> if result.success:
            ...     print(f"Masked {result.detections_count} PII fields")
        """
        # Validate input format
        if not base64_image:
            return AnonymizationResult(
                success=False,
                error="No image data provided"
            )

        # Ensure base64 has data URI prefix
        if not base64_image.startswith("data:image"):
            logger.warning("Image missing data URI prefix, adding default PNG prefix")
            base64_image = f"data:image/png;base64,{base64_image}"

        logger.info(f"Sending image to anonymization service (size: {len(base64_image)} chars)")

        try:
            # Prepare request payload
            payload = {
                "image": base64_image,
                "mode": "default"
            }

            headers = {
                "Content-Type": "application/json",
                "Secret-Key": self.SECRET_KEY
            }

            # Create timeout for the request
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT_SECONDS)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.API_URL,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        anonymized_image = data.get("anonymized_image")
                        detections_count = data.get("detections_count", 0)

                        if anonymized_image:
                            logger.info(
                                f"Anonymization successful - "
                                f"detections: {detections_count}"
                            )
                            return AnonymizationResult(
                                success=True,
                                anonymized_image=anonymized_image,
                                detections_count=detections_count
                            )
                        else:
                            logger.error("Anonymization response missing anonymized_image")
                            return AnonymizationResult(
                                success=False,
                                error="Invalid response from anonymization service"
                            )

                    elif response.status == 401:
                        logger.error("Anonymization service authentication failed")
                        return AnonymizationResult(
                            success=False,
                            error="Authentication failed - invalid API key"
                        )

                    elif response.status == 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", "Bad request")
                        logger.error(f"Anonymization bad request: {error_msg}")
                        return AnonymizationResult(
                            success=False,
                            error=f"Invalid request: {error_msg}"
                        )

                    else:
                        logger.error(
                            f"Anonymization service returned status {response.status}"
                        )
                        return AnonymizationResult(
                            success=False,
                            error=f"Service error (status {response.status})"
                        )

        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to anonymization service")
            return AnonymizationResult(
                success=False,
                error="Anonymization service unavailable. Please ensure the service is running at localhost:5000"
            )

        except aiohttp.ServerTimeoutError:
            logger.error(f"Anonymization service timeout after {self.TIMEOUT_SECONDS}s")
            return AnonymizationResult(
                success=False,
                error="Anonymization service timed out. The image may be too large."
            )

        except Exception as e:
            logger.error(f"Unexpected error during anonymization: {str(e)}")
            return AnonymizationResult(
                success=False,
                error=f"Anonymization failed: {str(e)}"
            )

    async def check_service_health(self) -> bool:
        """
        Check if the anonymization service is available.

        Returns:
            bool: True if service is reachable, False otherwise.
        """
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.API_URL.replace("/ai-analysis", "/")) as response:
                    return response.status in [200, 404]  # 404 is ok, means server is running
        except Exception:
            return False
