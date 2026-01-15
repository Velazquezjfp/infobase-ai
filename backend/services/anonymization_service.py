"""
Anonymization Service for BAMF AI Case Management System.

This module provides integration with an external PII detection service
that identifies personally identifiable information in identity documents
such as passports, birth certificates, and driving licenses.

The service receives detection coordinates from the external API and
applies black box masking over sensitive fields locally using PIL.
"""

import base64
import io
import logging
import aiohttp
from dataclasses import dataclass
from typing import Optional
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


@dataclass
class AnonymizationResult:
    """
    Result of an anonymization operation.

    Attributes:
        success: Whether the anonymization was successful.
        anonymized_image: Base64-encoded anonymized image with data URI prefix.
        detections_count: Number of PII detections found and masked.
        detection_labels: List of field names (labels) that were detected and masked.
        detections: Full detection data with field names and coordinates for overlay display.
        error: Error message if anonymization failed.
    """
    success: bool
    anonymized_image: Optional[str] = None
    detections_count: int = 0
    detection_labels: Optional[list] = None
    detections: Optional[dict] = None
    error: Optional[str] = None


class AnonymizationService:
    """
    Service class for interacting with the external PII detection API.

    This service handles:
    - Sending document images to the detection service
    - Receiving PII coordinates from the detection service
    - Drawing black boxes over detected areas using PIL
    - Returning the masked image as base64

    The external service runs a self-contained trained model for privacy.
    """

    API_URL = "http://localhost:5000/ai-analysis"
    SECRET_KEY = "2b5e151428aed2a6aff7158846cf4f2c"
    TIMEOUT_SECONDS = 60

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

    def _extract_base64_data(self, base64_image: str) -> tuple[str, str]:
        """
        Extract raw base64 data and mime type from data URI.

        Args:
            base64_image: Base64 string with or without data URI prefix.

        Returns:
            tuple: (raw_base64_data, mime_type)
        """
        if ';base64,' in base64_image:
            header, data = base64_image.split(';base64,', 1)
            mime_type = header.replace('data:', '')
            return data, mime_type
        return base64_image, 'image/png'

    def _apply_black_boxes(
        self,
        base64_image: str,
        detections: dict
    ) -> tuple[Optional[str], int, list, dict]:
        """
        Apply black boxes over detected PII areas in the image.

        Args:
            base64_image: Base64-encoded image with data URI prefix.
            detections: Dictionary of field_name -> list of detections,
                       each detection has 'coordinate': [x, y, width, height].

        Returns:
            tuple: (masked_image_base64, detections_count, detection_labels, detections_with_coords)
        """
        try:
            # Extract base64 data
            raw_base64, mime_type = self._extract_base64_data(base64_image)

            # Decode image
            image_data = base64.b64decode(raw_base64)
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary (for drawing)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')

            draw = ImageDraw.Draw(image)
            detections_count = 0
            detection_labels = []
            detections_with_coords = {}

            # Draw black boxes over each detection
            for field_name, field_detections in detections.items():
                if field_name not in detection_labels:
                    detection_labels.append(field_name)
                detections_with_coords[field_name] = []

                for detection in field_detections:
                    coord = detection.get('coordinate', [])
                    if len(coord) >= 4:
                        x, y, width, height = coord[:4]
                        # Draw filled black rectangle
                        draw.rectangle(
                            [x, y, x + width, y + height],
                            fill='black'
                        )
                        detections_count += 1
                        # Store detection info for frontend overlay
                        detections_with_coords[field_name].append({
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height,
                            'confidence': detection.get('confidence', 0)
                        })
                        logger.debug(
                            f"Masked {field_name} at ({x}, {y}, {width}, {height})"
                        )

            # Convert back to base64
            output_buffer = io.BytesIO()
            image_format = 'PNG' if 'png' in mime_type else 'JPEG'
            image.save(output_buffer, format=image_format)
            output_buffer.seek(0)

            masked_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            masked_with_prefix = f"data:{mime_type};base64,{masked_base64}"

            logger.info(f"Applied {detections_count} black boxes to image, labels: {detection_labels}")
            return masked_with_prefix, detections_count, detection_labels, detections_with_coords

        except Exception as e:
            logger.error(f"Error applying black boxes: {str(e)}")
            return None, 0, [], {}

    async def anonymize_image(self, base64_image: str) -> AnonymizationResult:
        """
        Send an image to the detection service and mask detected PII.

        The service detects PII in identity documents and returns coordinates.
        This method then applies black box masking over those areas.

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

        logger.info(f"Sending image to detection service (size: {len(base64_image)} chars)")

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

                        # Extract detections from response
                        # Response format: {"data": {"field_name": [{"confidence": X, "coordinate": [x, y, w, h]}]}}
                        detections = data.get("data", {})

                        if not detections:
                            logger.info("No PII detections found in image")
                            return AnonymizationResult(
                                success=True,
                                anonymized_image=base64_image,
                                detections_count=0,
                                detection_labels=[],
                                detections={}
                            )

                        # Apply black boxes to the original image
                        masked_image, detections_count, detection_labels, detections_with_coords = self._apply_black_boxes(
                            base64_image,
                            detections
                        )

                        if masked_image:
                            logger.info(
                                f"Anonymization successful - "
                                f"detections: {detections_count}, labels: {detection_labels}"
                            )
                            return AnonymizationResult(
                                success=True,
                                anonymized_image=masked_image,
                                detections_count=detections_count,
                                detection_labels=detection_labels,
                                detections=detections_with_coords
                            )
                        else:
                            logger.error("Failed to apply masking to image")
                            return AnonymizationResult(
                                success=False,
                                error="Failed to apply masking to image"
                            )

                    elif response.status == 401:
                        logger.error("Detection service authentication failed")
                        return AnonymizationResult(
                            success=False,
                            error="Authentication failed - invalid API key"
                        )

                    elif response.status == 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", "Bad request")
                        logger.error(f"Detection bad request: {error_msg}")
                        return AnonymizationResult(
                            success=False,
                            error=f"Invalid request: {error_msg}"
                        )

                    else:
                        logger.error(
                            f"Detection service returned status {response.status}"
                        )
                        return AnonymizationResult(
                            success=False,
                            error=f"Service error (status {response.status})"
                        )

        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to detection service")
            return AnonymizationResult(
                success=False,
                error="Anonymization service unavailable. Please ensure the service is running at localhost:5000"
            )

        except aiohttp.ServerTimeoutError:
            logger.error(f"Detection service timeout after {self.TIMEOUT_SECONDS}s")
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
        Check if the detection service is available.

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
