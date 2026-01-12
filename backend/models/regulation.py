"""
Regulation Model for BAMF Case Context.

This module provides structured access to regulation data from case contexts.
Regulations reference German immigration law sections that apply to specific
case types (integration courses, asylum applications, family reunification).

S5-013: Enhanced Acte Context Research
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class Regulation:
    """
    Represents a legal regulation referenced in a case context.

    Attributes:
        id: Regulation identifier (e.g., "§43_AufenthG", "IntV_§4")
        title: Official regulation title
        summary: Summary of regulation content and relevance
        url: Direct URL to official regulation text
        relevance: Optional explanation of regulation's relevance to case type
    """
    id: str
    title: str
    summary: str
    url: str
    relevance: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Regulation':
        """
        Create Regulation instance from dictionary (e.g., from JSON).

        Args:
            data: Dictionary containing regulation fields

        Returns:
            Regulation instance

        Raises:
            ValueError: If required fields are missing

        Example:
            >>> reg_data = {
            ...     "id": "§43_AufenthG",
            ...     "title": "Integrationskurs - Berechtigung",
            ...     "summary": "Defines entitlement to participate...",
            ...     "url": "https://www.gesetze-im-internet.de/..."
            ... }
            >>> regulation = Regulation.from_dict(reg_data)
        """
        required_fields = ['id', 'title', 'summary', 'url']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(
                f"Missing required fields for Regulation: {', '.join(missing_fields)}"
            )

        return cls(
            id=data['id'],
            title=data['title'],
            summary=data['summary'],
            url=data['url'],
            relevance=data.get('relevance')
        )

    def validate(self) -> List[str]:
        """
        Validate regulation data and return list of validation errors.

        Returns:
            List of error messages (empty list if valid)

        Example:
            >>> regulation = Regulation(id="", title="Test", summary="", url="")
            >>> errors = regulation.validate()
            >>> print(errors)
            ['Regulation id cannot be empty', 'Regulation summary cannot be empty']
        """
        errors = []

        if not self.id or not self.id.strip():
            errors.append("Regulation id cannot be empty")

        if not self.title or not self.title.strip():
            errors.append("Regulation title cannot be empty")

        if not self.summary or not self.summary.strip():
            errors.append("Regulation summary cannot be empty")

        if not self.url or not self.url.strip():
            errors.append("Regulation url cannot be empty")

        # Validate URL format (basic check)
        if self.url and not self.url.startswith(('http://', 'https://')):
            errors.append(f"Regulation url must start with http:// or https://: {self.url}")

        # Validate minimum content length
        if self.summary and len(self.summary) < 20:
            errors.append(
                f"Regulation summary too short (minimum 20 characters): {len(self.summary)} characters"
            )

        if self.title and len(self.title) < 5:
            errors.append(
                f"Regulation title too short (minimum 5 characters): {len(self.title)} characters"
            )

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Regulation to dictionary for JSON serialization.

        Returns:
            Dictionary representation of regulation
        """
        result = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'url': self.url
        }

        if self.relevance:
            result['relevance'] = self.relevance

        return result


def get_regulation_details(
    regulations: List[Dict[str, Any]],
    reference: str
) -> Optional[Regulation]:
    """
    Find and return regulation details by reference ID.

    Searches through a list of regulation dictionaries (typically from
    case context JSON) and returns a Regulation object for the matching ID.

    Args:
        regulations: List of regulation dictionaries from case context
        reference: Regulation ID to search for (e.g., "§43_AufenthG")

    Returns:
        Regulation object if found, None otherwise

    Example:
        >>> case_context = load_case_context("ACTE-2024-001")
        >>> regulation = get_regulation_details(
        ...     case_context['regulations'],
        ...     "§43_AufenthG"
        ... )
        >>> if regulation:
        ...     print(regulation.title)
        'Integrationskurs - Berechtigung'
    """
    if not regulations:
        logger.warning(f"No regulations provided for lookup of '{reference}'")
        return None

    for reg_data in regulations:
        if reg_data.get('id') == reference:
            try:
                return Regulation.from_dict(reg_data)
            except ValueError as e:
                logger.error(
                    f"Invalid regulation data for '{reference}': {e}"
                )
                return None

    logger.debug(f"Regulation '{reference}' not found in provided list")
    return None


def validate_regulations_list(
    regulations: List[Dict[str, Any]]
) -> tuple[bool, List[str], Dict[str, Any]]:
    """
    Validate a list of regulations from case context.

    Checks that all regulations in the list have required fields and
    valid data. Returns validation status, errors, and statistics.

    Args:
        regulations: List of regulation dictionaries from case context

    Returns:
        Tuple of (is_valid, errors, stats)
        - is_valid: True if all regulations valid
        - errors: List of error messages
        - stats: Dictionary with regulation statistics

    Example:
        >>> regulations = case_context['regulations']
        >>> valid, errors, stats = validate_regulations_list(regulations)
        >>> print(f"Valid: {valid}, Count: {stats['count']}")
        Valid: True, Count: 11
    """
    errors = []
    stats = {
        'count': len(regulations),
        'valid': 0,
        'invalid': 0,
        'unique_ids': set()
    }

    if not regulations:
        errors.append("Regulations list is empty")
        return False, errors, stats

    for idx, reg_data in enumerate(regulations):
        try:
            regulation = Regulation.from_dict(reg_data)
            reg_errors = regulation.validate()

            if reg_errors:
                stats['invalid'] += 1
                for error in reg_errors:
                    errors.append(f"Regulation {idx} ({regulation.id}): {error}")
            else:
                stats['valid'] += 1
                stats['unique_ids'].add(regulation.id)

        except ValueError as e:
            stats['invalid'] += 1
            errors.append(f"Regulation {idx}: {e}")
        except Exception as e:
            stats['invalid'] += 1
            errors.append(f"Regulation {idx}: Unexpected error - {e}")

    # Check for duplicate IDs
    if len(stats['unique_ids']) < len(regulations):
        errors.append(
            f"Duplicate regulation IDs found: "
            f"{len(regulations)} regulations but only {len(stats['unique_ids'])} unique IDs"
        )

    stats['unique_ids'] = len(stats['unique_ids'])  # Convert set to count
    is_valid = len(errors) == 0

    return is_valid, errors, stats
