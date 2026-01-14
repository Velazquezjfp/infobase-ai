"""
S5-008: Email Service - Email Parsing and Processing.

This module provides email parsing services for .eml files, extracting headers,
body content, and attachments. Supports multiple character encodings including
Arabic (ISO-8859-6) and RTL text.

Features:
    - Email header extraction (From, To, Subject, Date)
    - Email body extraction (plain text and HTML)
    - Character encoding detection and conversion
    - Arabic and RTL text support
    - Attachment metadata extraction

Dependencies:
    - email: Python standard library for email parsing
    - html2text: For HTML to plain text conversion
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from email import policy
from email.parser import BytesParser
from email.message import Message
from dataclasses import dataclass
import html2text

logger = logging.getLogger(__name__)


@dataclass
class EmailAttachment:
    """
    Represents an email attachment.

    Attributes:
        filename: Name of the attachment file
        content_type: MIME type of the attachment
        size: Size in bytes (if available)
    """
    filename: str
    content_type: str
    size: Optional[int] = None


@dataclass
class EmailData:
    """
    Parsed email data structure.

    Attributes:
        from_addr: Sender email address and name
        to_addr: Recipient email address(es)
        subject: Email subject line
        date: Email date string
        body_text: Plain text body content
        body_html: HTML body content (if available)
        attachments: List of attachment metadata
        headers: Raw headers dictionary
    """
    from_addr: str
    to_addr: str
    subject: str
    date: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = None
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.headers is None:
            self.headers = {}


class EmailService:
    """
    Service for parsing and processing email files (.eml format).

    This service provides methods for:
    - Parsing .eml files
    - Extracting email headers (From, To, Subject, Date)
    - Extracting email body (plain text and HTML)
    - Handling multiple character encodings (UTF-8, ISO-8859-6 for Arabic, etc.)
    - Extracting attachment metadata
    - Converting HTML to plain text
    """

    def __init__(self):
        """Initialize the email service."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.body_width = 0  # Don't wrap text
        logger.info("EmailService initialized")

    def parse_eml_file(self, file_path: str) -> EmailData:
        """
        Parse an .eml file and extract all email data.

        Handles multiple character encodings including Arabic (ISO-8859-6).
        Extracts headers, body content, and attachment metadata.

        Args:
            file_path: Path to the .eml file (absolute or relative)

        Returns:
            EmailData: Parsed email data structure

        Raises:
            FileNotFoundError: If the email file doesn't exist
            ValueError: If the file is not a valid email
            Exception: For other email parsing errors

        Example:
            >>> service = EmailService()
            >>> email_data = service.parse_eml_file("Email.eml")
            >>> print(email_data.subject)
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"Email file not found: {file_path}")
            raise FileNotFoundError(f"Email file not found: {file_path}")

        if not path.suffix.lower() == '.eml':
            logger.error(f"File is not an email: {file_path}")
            raise ValueError(f"File must be .eml, got: {path.suffix}")

        try:
            # Parse email using BytesParser for proper encoding handling
            with open(path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)

            # Extract headers
            from_addr = self._decode_header(msg.get('From', 'Unknown'))
            to_addr = self._decode_header(msg.get('To', 'Unknown'))
            subject = self._decode_header(msg.get('Subject', 'No Subject'))
            date = msg.get('Date', 'Unknown')

            # Extract all headers for reference
            headers = {
                key: self._decode_header(str(value))
                for key, value in msg.items()
            }

            # Extract body content
            body_text, body_html = self._extract_body(msg)

            # Extract attachments
            attachments = self._extract_attachments(msg)

            logger.info(
                f"Parsed email: {subject} "
                f"({len(body_text)} chars, {len(attachments)} attachments)"
            )

            return EmailData(
                from_addr=from_addr,
                to_addr=to_addr,
                subject=subject,
                date=date,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments,
                headers=headers
            )

        except Exception as e:
            logger.error(f"Error parsing email {path.name}: {str(e)}")
            raise Exception(f"Failed to parse email: {str(e)}")

    def _decode_header(self, header_value: str) -> str:
        """
        Decode email header handling various encodings.

        Args:
            header_value: Raw header value

        Returns:
            str: Decoded header string
        """
        if not header_value:
            return ""

        try:
            from email.header import decode_header
            decoded_parts = decode_header(header_value)
            result = []

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    # Decode bytes using specified encoding or default to UTF-8
                    charset = encoding or 'utf-8'
                    try:
                        result.append(part.decode(charset))
                    except (UnicodeDecodeError, LookupError):
                        # Fallback to ISO-8859-6 for Arabic if UTF-8 fails
                        try:
                            result.append(part.decode('iso-8859-6'))
                        except:
                            result.append(part.decode('utf-8', errors='replace'))
                else:
                    result.append(str(part))

            return ' '.join(result)
        except Exception as e:
            logger.warning(f"Header decode error: {e}")
            return str(header_value)

    def _extract_body(self, msg: Message) -> tuple[str, Optional[str]]:
        """
        Extract email body content (plain text and HTML).

        Args:
            msg: Parsed email message

        Returns:
            tuple: (plain_text, html_text) - HTML may be None
        """
        plain_text = ""
        html_text = None

        try:
            if msg.is_multipart():
                # Walk through email parts
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue

                    # Extract plain text
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            try:
                                plain_text = payload.decode(charset)
                            except (UnicodeDecodeError, LookupError):
                                # Try ISO-8859-6 for Arabic
                                try:
                                    plain_text = payload.decode('iso-8859-6')
                                except:
                                    plain_text = payload.decode('utf-8', errors='replace')
                        break  # Use first plain text part

                    # Extract HTML (as fallback)
                    elif content_type == "text/html" and not plain_text:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            try:
                                html_text = payload.decode(charset)
                            except (UnicodeDecodeError, LookupError):
                                try:
                                    html_text = payload.decode('iso-8859-6')
                                except:
                                    html_text = payload.decode('utf-8', errors='replace')
            else:
                # Single part message
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    try:
                        plain_text = payload.decode(charset)
                    except (UnicodeDecodeError, LookupError):
                        try:
                            plain_text = payload.decode('iso-8859-6')
                        except:
                            plain_text = payload.decode('utf-8', errors='replace')

            # If we only have HTML, convert it to plain text
            if not plain_text and html_text:
                plain_text = self.html_converter.handle(html_text)

        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            plain_text = "Error: Could not extract email body"

        return plain_text, html_text

    def _extract_attachments(self, msg: Message) -> List[EmailAttachment]:
        """
        Extract attachment metadata from email.

        Args:
            msg: Parsed email message

        Returns:
            List[EmailAttachment]: List of attachments
        """
        attachments = []

        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            # Decode filename if needed
                            filename = self._decode_header(filename)

                            content_type = part.get_content_type()
                            payload = part.get_payload(decode=True)
                            size = len(payload) if payload else None

                            attachments.append(EmailAttachment(
                                filename=filename,
                                content_type=content_type,
                                size=size
                            ))
        except Exception as e:
            logger.warning(f"Error extracting attachments: {e}")

        return attachments


# Singleton instance
_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get the singleton instance of EmailService.

    Returns:
        EmailService: The email service instance
    """
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
