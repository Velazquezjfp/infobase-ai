"""
Context Manager Service for Case-Instance Document Context Management.

This module provides hierarchical context inheritance for AI agents, ensuring
complete case isolation. Each case (ACTE) has its own context directory with
case-level and folder-level configuration files.

Architecture:
- Case-level context: cases/{caseId}/case.json
- Folder-level context: cases/{caseId}/folders/{folderId}.json
- Template contexts: templates/{caseType}/

When switching cases, ALL context switches - no cross-case data access.

S2-004 Enhancement:
- Context source tracking for AI transparency
- resolve_conflict() helper for precedence rules
- Enhanced merge_contexts() with source labels
"""

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextSource(Enum):
    """
    S2-004: Enumeration of context source types for tracking.

    Used to identify where information came from in merged context,
    enabling AI transparency about data sources.
    """
    CASE = "case"
    FOLDER = "folder"
    DOCUMENT = "document"
    USER = "user"
    SYSTEM = "system"


@dataclass
class ContextEntry:
    """
    S2-004: A single context entry with source tracking.

    Attributes:
        key: The context key (e.g., 'applicant_name', 'case_type')
        value: The context value
        source: Where this context came from
        source_name: Human-readable source name (e.g., filename)
        confidence: Confidence score 0.0-1.0 (optional)
        timestamp: When this entry was created/updated
    """
    key: str
    value: Any
    source: ContextSource
    source_name: str
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source.value,
            "sourceName": self.source_name,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MergedContext:
    """
    S2-004: Result of merging multiple context sources.

    Provides both the merged context string for AI prompts and
    tracking information about where each piece came from.

    Attributes:
        prompt_text: Formatted context string for AI prompt
        sources: List of context sources used
        entries: Individual context entries with source tracking
        conflicts: Any conflicts that were resolved during merge
    """
    prompt_text: str
    sources: List[str]
    entries: List[ContextEntry] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def get_source_summary(self) -> str:
        """Get human-readable summary of sources used."""
        if not self.sources:
            return "No context sources"
        return f"Sources: {', '.join(self.sources)}"


def resolve_conflict(
    entries: List[ContextEntry],
    precedence: List[ContextSource] = None
) -> Tuple[ContextEntry, List[Dict[str, Any]]]:
    """
    S2-004: Resolve conflicts between context entries with same key.

    When multiple sources provide the same key, this function determines
    which value to use based on precedence rules.

    Default precedence: Document > Folder > Case > User > System

    Args:
        entries: List of conflicting ContextEntry objects
        precedence: Optional custom precedence order (highest priority first)

    Returns:
        Tuple of (winning_entry, conflict_info_list)

    Example:
        >>> entries = [
        ...     ContextEntry("name", "John", ContextSource.CASE, "case.json"),
        ...     ContextEntry("name", "Johan", ContextSource.DOCUMENT, "passport.txt"),
        ... ]
        >>> winner, conflicts = resolve_conflict(entries)
        >>> print(winner.value)  # "Johan" (document has higher precedence)
        'Johan'
    """
    if not entries:
        raise ValueError("No entries to resolve")

    if len(entries) == 1:
        return entries[0], []

    # Default precedence order (highest to lowest priority)
    default_precedence = [
        ContextSource.DOCUMENT,
        ContextSource.FOLDER,
        ContextSource.CASE,
        ContextSource.USER,
        ContextSource.SYSTEM,
    ]

    precedence = precedence or default_precedence

    # Sort entries by precedence (lower index = higher priority)
    def get_priority(entry: ContextEntry) -> int:
        try:
            return precedence.index(entry.source)
        except ValueError:
            return len(precedence)  # Unknown sources get lowest priority

    sorted_entries = sorted(entries, key=get_priority)
    winner = sorted_entries[0]

    # Build conflict information
    conflicts = []
    for entry in sorted_entries[1:]:
        if entry.value != winner.value:
            conflicts.append({
                "key": entry.key,
                "resolvedValue": winner.value,
                "resolvedSource": winner.source.value,
                "conflictingValue": entry.value,
                "conflictingSource": entry.source.value,
                "reason": f"{winner.source.value} takes precedence over {entry.source.value}",
            })

    if conflicts:
        logger.info(
            f"Resolved {len(conflicts)} conflict(s) for key '{winner.key}', "
            f"using value from {winner.source.value}"
        )

    return winner, conflicts


class ContextManager:
    """
    Manages case-instance scoped context for AI document processing.

    Provides methods to load case-level context, folder-level context,
    create new cases from templates, and merge contexts for AI prompts.
    Ensures complete isolation between cases.

    Attributes:
        base_path (Path): Base directory for context files
        contexts_path (Path): Path to contexts directory
        cases_path (Path): Path to cases directory
        templates_path (Path): Path to templates directory
    """

    def __init__(self, base_path: str = "backend/data/contexts"):
        """
        Initialize the ContextManager with base path for context files.

        Args:
            base_path (str): Base directory containing contexts. Defaults to
                           "backend/data/contexts"

        Raises:
            ValueError: If base_path does not exist
        """
        self.base_path = Path(base_path)

        if not self.base_path.exists():
            logger.error(f"Context base path does not exist: {base_path}")
            raise ValueError(f"Context base path does not exist: {base_path}")

        self.contexts_path = self.base_path
        self.cases_path = self.contexts_path / "cases"
        self.templates_path = self.contexts_path / "templates"

        logger.info(f"ContextManager initialized with base path: {base_path}")

    def load_case_context(self, case_id: str) -> Dict[str, Any]:
        """
        Load case-level context from case-specific directory.

        Loads context configuration from cases/{case_id}/case.json including
        case type, regulations, required documents, and validation rules.

        Args:
            case_id (str): Unique case identifier (e.g., "ACTE-2024-001")

        Returns:
            Dict[str, Any]: Case context dictionary containing:
                - caseId: Case identifier
                - caseType: Type of case (e.g., "integration_course")
                - name: Human-readable case name
                - regulations: List of applicable regulations
                - requiredDocuments: List of required document types
                - validationRules: List of validation rules
                - commonIssues: List of common issues and suggestions

        Raises:
            FileNotFoundError: If case context file does not exist
            json.JSONDecodeError: If case context file contains invalid JSON

        Example:
            >>> context_manager = ContextManager()
            >>> context = context_manager.load_case_context("ACTE-2024-001")
            >>> print(context["caseType"])
            'integration_course'
        """
        case_context_path = self.cases_path / case_id / "case.json"

        if not case_context_path.exists():
            logger.error(f"Case context not found for case: {case_id}")
            raise FileNotFoundError(
                f"Case context not found: {case_context_path}"
            )

        try:
            with open(case_context_path, 'r', encoding='utf-8') as f:
                context = json.load(f)

            logger.info(f"Successfully loaded case context for: {case_id}")
            return context

        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in case context file {case_context_path}: {e}"
            )
            raise

    def load_folder_context(
        self,
        case_id: str,
        folder_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load folder-level context for specific folder within a case.

        Loads folder-specific validation rules and expected documents from
        cases/{case_id}/folders/{folder_id}.json.

        Args:
            case_id (str): Unique case identifier
            folder_id (str): Folder identifier (e.g., "personal-data")

        Returns:
            Optional[Dict[str, Any]]: Folder context dictionary containing:
                - folderId: Folder identifier
                - folderName: Human-readable folder name
                - purpose: Description of folder's purpose
                - expectedDocuments: List of expected document types
                - validationCriteria: List of validation criteria
                - commonMistakes: Common mistakes in this folder
                Returns None if folder context file doesn't exist (graceful fallback)

        Example:
            >>> context = context_manager.load_folder_context(
            ...     "ACTE-2024-001",
            ...     "personal-data"
            ... )
            >>> print(context["folderName"])
            'Personal Data'
        """
        folder_context_path = (
            self.cases_path / case_id / "folders" / f"{folder_id}.json"
        )

        if not folder_context_path.exists():
            logger.warning(
                f"Folder context not found for case {case_id}, "
                f"folder {folder_id}. Returning None."
            )
            return None

        try:
            with open(folder_context_path, 'r', encoding='utf-8') as f:
                context = json.load(f)

            logger.info(
                f"Successfully loaded folder context for case {case_id}, "
                f"folder {folder_id}"
            )
            return context

        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in folder context file "
                f"{folder_context_path}: {e}"
            )
            return None

    def create_case_from_template(
        self,
        case_id: str,
        case_type: str
    ) -> bool:
        """
        Create new case directory from template.

        Copies template context structure from templates/{case_type}/ to
        cases/{case_id}/. Updates caseId in the copied case.json file.
        Enables dynamic case creation with pre-configured contexts.

        Args:
            case_id (str): New case identifier (e.g., "ACTE-2024-004")
            case_type (str): Type of case template to use
                           (e.g., "integration_course")

        Returns:
            bool: True if case created successfully, False otherwise

        Raises:
            FileNotFoundError: If template does not exist
            FileExistsError: If case directory already exists
            OSError: If file system operations fail

        Example:
            >>> success = context_manager.create_case_from_template(
            ...     "ACTE-2024-004",
            ...     "integration_course"
            ... )
            >>> print(success)
            True
        """
        template_path = self.templates_path / case_type
        new_case_path = self.cases_path / case_id

        # Validate template exists
        if not template_path.exists():
            logger.error(f"Template not found: {case_type}")
            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        # Check if case already exists
        if new_case_path.exists():
            logger.error(f"Case directory already exists: {case_id}")
            raise FileExistsError(
                f"Case directory already exists: {new_case_path}"
            )

        try:
            # Copy template directory to new case directory
            shutil.copytree(template_path, new_case_path)
            logger.info(
                f"Copied template {case_type} to new case {case_id}"
            )

            # Update caseId in the copied case.json
            case_json_path = new_case_path / "case.json"
            if case_json_path.exists():
                with open(case_json_path, 'r', encoding='utf-8') as f:
                    case_data = json.load(f)

                # Update caseId
                case_data['caseId'] = case_id

                with open(case_json_path, 'w', encoding='utf-8') as f:
                    json.dump(case_data, f, indent=2, ensure_ascii=False)

                logger.info(
                    f"Updated caseId in case.json for new case {case_id}"
                )

            return True

        except (OSError, json.JSONDecodeError) as e:
            logger.error(
                f"Failed to create case {case_id} from template "
                f"{case_type}: {e}"
            )
            # Clean up partial copy if creation failed
            if new_case_path.exists():
                shutil.rmtree(new_case_path)
            return False

    def merge_contexts(
        self,
        case_ctx: Optional[Dict[str, Any]],
        folder_ctx: Optional[Dict[str, Any]],
        doc_ctx: Optional[str]
    ) -> str:
        """
        Merge case, folder, and document contexts into AI prompt string.

        Combines three levels of context hierarchy for AI agent:
        1. Case-level: Regulations, required documents, validation rules
        2. Folder-level: Expected documents, validation criteria
        3. Document-level: Actual document content

        Precedence: Document > Folder > Case

        Args:
            case_ctx (Optional[Dict[str, Any]]): Case context dictionary
            folder_ctx (Optional[Dict[str, Any]]): Folder context dictionary
            doc_ctx (Optional[str]): Document content string

        Returns:
            str: Formatted context string for AI prompt with clear sections
                for case information, folder validation, and document content

        Example:
            >>> merged = context_manager.merge_contexts(
            ...     case_ctx={"caseType": "integration_course", ...},
            ...     folder_ctx={"folderId": "personal-data", ...},
            ...     doc_ctx="Birth Certificate: Ahmad Ali..."
            ... )
            >>> print(merged)
            # Returns formatted multi-line context string
        """
        context_parts = []

        # Case-level context
        if case_ctx:
            case_section = [
                "=== CASE CONTEXT ===",
                f"Case ID: {case_ctx.get('caseId', 'Unknown')}",
                f"Case Type: {case_ctx.get('caseType', 'Unknown')}",
                f"Case Name: {case_ctx.get('name', 'Unknown')}",
                ""
            ]

            # Add regulations summary
            if 'regulations' in case_ctx and case_ctx['regulations']:
                case_section.append("Applicable Regulations:")
                for reg in case_ctx['regulations'][:5]:  # Top 5 regulations
                    case_section.append(
                        f"  - {reg.get('id', 'N/A')}: "
                        f"{reg.get('title', 'N/A')}"
                    )
                case_section.append("")

            # Add required documents summary
            if 'requiredDocuments' in case_ctx:
                mandatory_docs = [
                    doc for doc in case_ctx['requiredDocuments']
                    if doc.get('mandatory', False)
                ]
                if mandatory_docs:
                    case_section.append(
                        f"Required Documents: "
                        f"{len(mandatory_docs)} mandatory types"
                    )
                    case_section.append("")

            # Add validation rules summary
            if 'validationRules' in case_ctx and case_ctx['validationRules']:
                case_section.append("Key Validation Rules:")
                for rule in case_ctx['validationRules'][:3]:  # Top 3 rules
                    case_section.append(
                        f"  - {rule.get('rule_id', 'N/A')}: "
                        f"{rule.get('condition', 'N/A')}"
                    )
                case_section.append("")

            context_parts.append("\n".join(case_section))

        # Folder-level context
        if folder_ctx:
            folder_section = [
                "=== FOLDER CONTEXT ===",
                f"Folder: {folder_ctx.get('folderName', 'Unknown')}",
                f"Purpose: {folder_ctx.get('purpose', 'N/A')}",
                ""
            ]

            # Add expected documents
            if 'expectedDocuments' in folder_ctx:
                folder_section.append("Expected Documents:")
                for doc_type in folder_ctx['expectedDocuments']:
                    folder_section.append(f"  - {doc_type}")
                folder_section.append("")

            # Add validation criteria
            if 'validationCriteria' in folder_ctx:
                folder_section.append("Validation Criteria:")
                for criterion in folder_ctx['validationCriteria']:
                    folder_section.append(
                        f"  - {criterion.get('criterionId', 'N/A')}: "
                        f"{criterion.get('description', 'N/A')}"
                    )
                folder_section.append("")

            context_parts.append("\n".join(folder_section))

        # Document-level context
        if doc_ctx:
            doc_section = [
                "=== DOCUMENT CONTENT ===",
                doc_ctx,
                ""
            ]
            context_parts.append("\n".join(doc_section))

        # Combine all context parts
        merged_context = "\n".join(context_parts)

        logger.info(
            f"Merged context: "
            f"case={'present' if case_ctx else 'absent'}, "
            f"folder={'present' if folder_ctx else 'absent'}, "
            f"document={'present' if doc_ctx else 'absent'}"
        )

        return merged_context

    def merge_contexts_with_tracking(
        self,
        case_ctx: Optional[Dict[str, Any]],
        folder_ctx: Optional[Dict[str, Any]],
        doc_ctx: Optional[str],
        doc_name: Optional[str] = None
    ) -> MergedContext:
        """
        S2-004: Merge contexts with full source tracking for AI transparency.

        Enhanced version of merge_contexts that returns a MergedContext object
        with source tracking information. This enables the AI to cite sources
        and the UI to show where information came from.

        Args:
            case_ctx: Case context dictionary
            folder_ctx: Folder context dictionary
            doc_ctx: Document content string
            doc_name: Name of the document (for source tracking)

        Returns:
            MergedContext: Contains prompt text, sources used, and tracking info

        Example:
            >>> result = context_manager.merge_contexts_with_tracking(
            ...     case_ctx={"caseType": "integration_course", ...},
            ...     folder_ctx={"folderId": "personal-data", ...},
            ...     doc_ctx="Birth Certificate: Ahmad Ali...",
            ...     doc_name="birth_certificate.txt"
            ... )
            >>> print(result.get_source_summary())
            'Sources: Case: ACTE-2024-001, Folder: personal-data, Document: birth_certificate.txt'
        """
        context_parts = []
        sources = []
        entries = []
        all_conflicts = []

        # S2-004: Case-level context with source tracking
        if case_ctx:
            case_id = case_ctx.get('caseId', 'Unknown')
            case_name = case_ctx.get('name', 'Unknown')
            sources.append(f"Case: {case_id}")

            # Track key case entries
            entries.append(ContextEntry(
                key="case_type",
                value=case_ctx.get('caseType'),
                source=ContextSource.CASE,
                source_name=f"case.json ({case_id})"
            ))

            case_section = [
                f"=== CASE CONTEXT [Source: {case_id}] ===",
                f"Case ID: {case_id}",
                f"Case Type: {case_ctx.get('caseType', 'Unknown')}",
                f"Case Name: {case_name}",
                ""
            ]

            # Add regulations summary
            if 'regulations' in case_ctx and case_ctx['regulations']:
                case_section.append("Applicable Regulations:")
                for reg in case_ctx['regulations'][:5]:
                    case_section.append(
                        f"  - {reg.get('id', 'N/A')}: "
                        f"{reg.get('title', 'N/A')}"
                    )
                case_section.append("")

            # Add required documents summary
            if 'requiredDocuments' in case_ctx:
                mandatory_docs = [
                    doc for doc in case_ctx['requiredDocuments']
                    if doc.get('mandatory', False)
                ]
                if mandatory_docs:
                    case_section.append(
                        f"Required Documents: "
                        f"{len(mandatory_docs)} mandatory types"
                    )
                    case_section.append("")

            # Add validation rules summary
            if 'validationRules' in case_ctx and case_ctx['validationRules']:
                case_section.append("Key Validation Rules:")
                for rule in case_ctx['validationRules'][:3]:
                    case_section.append(
                        f"  - {rule.get('rule_id', 'N/A')}: "
                        f"{rule.get('condition', 'N/A')}"
                    )
                case_section.append("")

            context_parts.append("\n".join(case_section))

        # S2-004: Folder-level context with source tracking
        if folder_ctx:
            folder_id = folder_ctx.get('folderId', 'Unknown')
            folder_name = folder_ctx.get('folderName', 'Unknown')
            sources.append(f"Folder: {folder_name}")

            # Track folder context entry
            entries.append(ContextEntry(
                key="folder_purpose",
                value=folder_ctx.get('purpose'),
                source=ContextSource.FOLDER,
                source_name=f"{folder_id}.json"
            ))

            folder_section = [
                f"=== FOLDER CONTEXT [Source: {folder_name}] ===",
                f"Folder: {folder_name}",
                f"Purpose: {folder_ctx.get('purpose', 'N/A')}",
                ""
            ]

            # Add expected documents
            if 'expectedDocuments' in folder_ctx:
                folder_section.append("Expected Documents:")
                for doc_type in folder_ctx['expectedDocuments']:
                    folder_section.append(f"  - {doc_type}")
                folder_section.append("")

            # Add validation criteria
            if 'validationCriteria' in folder_ctx:
                folder_section.append("Validation Criteria:")
                for criterion in folder_ctx['validationCriteria']:
                    folder_section.append(
                        f"  - {criterion.get('criterionId', 'N/A')}: "
                        f"{criterion.get('description', 'N/A')}"
                    )
                folder_section.append("")

            context_parts.append("\n".join(folder_section))

        # S2-004: Document-level context with source tracking
        if doc_ctx:
            source_label = doc_name or "Uploaded Document"
            sources.append(f"Document: {source_label}")

            # Track document context entry
            entries.append(ContextEntry(
                key="document_content",
                value=f"[{len(doc_ctx)} characters]",
                source=ContextSource.DOCUMENT,
                source_name=source_label
            ))

            doc_section = [
                f"=== DOCUMENT CONTENT [Source: {source_label}] ===",
                doc_ctx,
                ""
            ]
            context_parts.append("\n".join(doc_section))

        # Combine all context parts
        merged_context = "\n".join(context_parts)

        # Add source summary at the end
        if sources:
            merged_context += f"\n--- Context Sources: {', '.join(sources)} ---"

        logger.info(
            f"Merged context with tracking: {len(sources)} sources, "
            f"{len(entries)} tracked entries"
        )

        return MergedContext(
            prompt_text=merged_context,
            sources=sources,
            entries=entries,
            conflicts=all_conflicts
        )
