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
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S5-011: In-memory cache for document tree views
# Maps case_id to tuple of (tree_string, timestamp)
_tree_view_cache: Dict[str, Tuple[str, datetime]] = {}


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


@dataclass
class ValidationResult:
    """
    S5-013: Result of case context validation.

    Provides validation status, error messages, warnings, and statistics
    about the validated case context.

    Attributes:
        valid: True if context passes all validation checks
        errors: List of validation error messages
        warnings: List of validation warning messages
        stats: Dictionary containing validation statistics
    """
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }

    def add_error(self, error: str) -> None:
        """Add an error message and mark validation as invalid."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def get_summary(self) -> str:
        """Get human-readable summary of validation result."""
        if self.valid:
            return f"✓ Valid - {self.stats.get('documents', 0)} docs, {self.stats.get('regulations', 0)} regs, {self.stats.get('issues', 0)} issues"
        else:
            return f"✗ Invalid - {len(self.errors)} error(s), {len(self.warnings)} warning(s)"


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

            # S5-011: Add document tree view to case context
            try:
                tree_view = generate_document_tree(case_id)
                context['documentTreeView'] = tree_view
                logger.debug(f"Added document tree view to case context for {case_id}")
            except Exception as e:
                logger.warning(f"Could not generate tree view for {case_id}: {e}")
                context['documentTreeView'] = f"Case: {case_id}\n└── (tree view unavailable)"

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

    def validate_case_context(
        self,
        context: Dict[str, Any],
        check_urls: bool = False
    ) -> ValidationResult:
        """
        S5-013: Validate case context against schema v2.0 requirements.

        Validates that a case context dictionary meets all schema requirements
        including required fields, minimum thresholds, and data quality checks.

        Args:
            context: Case context dictionary to validate
            check_urls: If True, verify regulation URLs are accessible (slow)

        Returns:
            ValidationResult with validation status, errors, warnings, and stats

        Example:
            >>> context_manager = ContextManager()
            >>> context = context_manager.load_case_context("ACTE-2024-001")
            >>> result = context_manager.validate_case_context(context)
            >>> if result.valid:
            ...     print("Context is valid!")
            >>> else:
            ...     for error in result.errors:
            ...         print(f"Error: {error}")
        """
        result = ValidationResult(valid=True)

        # Validate schema version
        schema_version = context.get('schemaVersion')
        if schema_version != '2.0':
            result.add_error(
                f"Invalid schema version: expected '2.0', got '{schema_version}'"
            )

        # Check required top-level fields
        required_fields = [
            'schemaVersion', 'caseId', 'caseType', 'name', 'description',
            'requiredDocuments', 'regulations', 'validationRules', 'commonIssues'
        ]

        for field in required_fields:
            if field not in context:
                result.add_error(f"Missing required field: {field}")

        # If critical fields missing, return early
        if not result.valid:
            return result

        # Validate and count required documents
        required_docs = context.get('requiredDocuments', [])
        result.stats['documents'] = len(required_docs)
        result.stats['critical_documents'] = 0
        result.stats['optional_documents'] = 0

        if len(required_docs) < 15:
            result.add_error(
                f"Insufficient required documents: expected ≥15, got {len(required_docs)}"
            )

        for idx, doc in enumerate(required_docs):
            # Check required document fields
            doc_required_fields = ['name', 'documentType', 'description', 'criticality', 'validationRules']
            for field in doc_required_fields:
                if field not in doc:
                    result.add_error(
                        f"Document {idx} missing required field: {field}"
                    )

            # Validate criticality value
            criticality = doc.get('criticality')
            if criticality == 'critical':
                result.stats['critical_documents'] += 1
            elif criticality == 'optional':
                result.stats['optional_documents'] += 1
            elif criticality:
                result.add_error(
                    f"Document {idx} has invalid criticality: '{criticality}' "
                    f"(must be 'critical' or 'optional')"
                )

        # Validate regulations using the regulation model
        from backend.models.regulation import validate_regulations_list

        regulations = context.get('regulations', [])
        result.stats['regulations'] = len(regulations)

        if len(regulations) < 10:
            result.add_error(
                f"Insufficient regulations: expected ≥10, got {len(regulations)}"
            )

        # Use regulation model validation
        regs_valid, reg_errors, reg_stats = validate_regulations_list(regulations)
        if not regs_valid:
            for error in reg_errors:
                result.add_error(f"Regulation validation: {error}")

        result.stats['regulations_valid'] = reg_stats.get('valid', 0)
        result.stats['regulations_invalid'] = reg_stats.get('invalid', 0)

        # Optional: Check URL accessibility
        if check_urls and regs_valid:
            try:
                import requests
                for reg in regulations:
                    url = reg.get('url')
                    if url:
                        try:
                            response = requests.head(url, timeout=5, allow_redirects=True)
                            if response.status_code >= 400:
                                result.add_warning(
                                    f"Regulation URL not accessible: {url} "
                                    f"(HTTP {response.status_code})"
                                )
                        except requests.RequestException as e:
                            result.add_warning(
                                f"Could not verify URL: {url} ({str(e)})"
                            )
            except ImportError:
                result.add_warning(
                    "URL checking requested but 'requests' library not available"
                )

        # Validate common issues
        common_issues = context.get('commonIssues', [])
        result.stats['issues'] = len(common_issues)

        if len(common_issues) < 20:
            result.add_error(
                f"Insufficient common issues: expected ≥20, got {len(common_issues)}"
            )

        result.stats['issues_by_severity'] = {'error': 0, 'warning': 0, 'info': 0}
        result.stats['issues_by_category'] = {}

        for idx, issue in enumerate(common_issues):
            # Check required issue fields
            issue_required_fields = ['issue', 'severity', 'suggestion']
            for field in issue_required_fields:
                if field not in issue:
                    result.add_error(
                        f"Common issue {idx} missing required field: {field}"
                    )

            # Validate severity
            severity = issue.get('severity')
            if severity in ['error', 'warning', 'info']:
                result.stats['issues_by_severity'][severity] += 1
            elif severity:
                result.add_error(
                    f"Common issue {idx} has invalid severity: '{severity}' "
                    f"(must be 'error', 'warning', or 'info')"
                )

            # Count by category
            category = issue.get('category')
            if category:
                result.stats['issues_by_category'][category] = \
                    result.stats['issues_by_category'].get(category, 0) + 1

        # Validate validation rules
        validation_rules = context.get('validationRules', [])
        result.stats['validation_rules'] = len(validation_rules)

        if len(validation_rules) == 0:
            result.add_warning("No validation rules defined")

        for idx, rule in enumerate(validation_rules):
            rule_required_fields = ['rule_id', 'condition', 'action']
            for field in rule_required_fields:
                if field not in rule:
                    result.add_error(
                        f"Validation rule {idx} missing required field: {field}"
                    )

        # Add summary info
        result.stats['case_id'] = context.get('caseId', 'Unknown')
        result.stats['case_type'] = context.get('caseType', 'Unknown')
        result.stats['case_name'] = context.get('name', 'Unknown')

        # Log validation result
        logger.info(
            f"Validated case context '{context.get('caseId')}': "
            f"{result.get_summary()}"
        )

        return result


# ============================================================================
# S5-011: Document Tree View Functions
# ============================================================================

def generate_document_tree(case_id: str) -> str:
    """
    S5-011: Generate a hierarchical text representation of the document tree.

    Creates a tree view showing all folders and documents in a case using
    ASCII tree characters (├── └──). This tree view is included in AI prompts
    to provide global document awareness.

    Args:
        case_id: The case ID to generate tree view for (e.g., "ACTE-2024-001")

    Returns:
        str: Hierarchical text representation of the document tree.

    Example Output:
        Case: ACTE-2024-001
        ├── Personal Data/
        │   ├── Birth_Certificate.jpg
        │   ├── Reisepass.png
        │   └── ID_Card.png
        ├── Certificates/
        │   └── Language_Certificate_A1.pdf
        └── Emails/ (empty)
    """
    # Check cache first
    if case_id in _tree_view_cache:
        cached_tree, cached_time = _tree_view_cache[case_id]
        logger.debug(f"Returning cached tree view for {case_id} (cached at {cached_time})")
        return cached_tree

    try:
        # Import document registry functions
        from backend.services.document_registry import (
            build_document_tree,
            get_documents_by_case
        )

        # Get the structured tree from document registry
        tree_data = build_document_tree(case_id)
        documents = get_documents_by_case(case_id)

        # Load folder metadata to get display names
        folder_names = {}
        context_base = Path("backend/data/contexts/cases") / case_id

        # First, load from folder_config.json (new format with localized names)
        folder_config_path = context_base / "folder_config.json"
        if folder_config_path.exists():
            try:
                with open(folder_config_path, 'r', encoding='utf-8') as f:
                    folder_config = json.load(f)
                    for folder in folder_config.get('folders', []):
                        folder_id = folder.get('id')
                        # Get name - prefer German, then English, then id
                        name_obj = folder.get('name', {})
                        if isinstance(name_obj, dict):
                            folder_name = name_obj.get('de') or name_obj.get('en') or folder_id
                        else:
                            folder_name = str(name_obj) or folder_id
                        if folder_id:
                            folder_names[folder_id] = folder_name
            except Exception as e:
                logger.warning(f"Could not load folder_config.json: {e}")

        # Also load from individual folder/*.json files (legacy format)
        folders_dir = context_base / "folders"
        if folders_dir.exists():
            for folder_file in folders_dir.glob("*.json"):
                try:
                    with open(folder_file, 'r', encoding='utf-8') as f:
                        folder_ctx = json.load(f)
                        folder_id = folder_ctx.get('folderId')
                        folder_name = folder_ctx.get('folderName', folder_id)
                        # Only add if not already in folder_names (folder_config takes precedence)
                        if folder_id and folder_id not in folder_names:
                            folder_names[folder_id] = folder_name
                except Exception as e:
                    logger.warning(f"Could not load folder name from {folder_file}: {e}")

        # Build tree text representation
        tree_lines = [f"Case: {case_id}"]

        folders = tree_data.get('folders', [])
        root_documents = tree_data.get('rootDocuments', [])

        # Count total items (folders + root documents)
        total_items = len(folders) + len(root_documents)
        current_item = 0

        # Add folders with their documents
        for folder in folders:
            current_item += 1
            is_last_item = (current_item == total_items)

            folder_id = folder.get('id')
            folder_display_name = folder_names.get(folder_id, folder_id)
            folder_docs = folder.get('documents', [])

            # Folder line
            prefix = "└──" if is_last_item else "├──"
            if len(folder_docs) == 0:
                tree_lines.append(f"{prefix} {folder_display_name}/ (empty)")
            else:
                tree_lines.append(f"{prefix} {folder_display_name}/")

                # Add documents in folder
                for doc_idx, doc in enumerate(folder_docs):
                    is_last_doc = (doc_idx == len(folder_docs) - 1)
                    doc_name = doc.get('fileName', 'Unknown')
                    renders = doc.get('renders', [])

                    # Filter renders to only show non-original (anonymized, translated, etc.)
                    additional_renders = [r for r in renders if r.get('type') != 'original']
                    has_additional_renders = len(additional_renders) > 0

                    # Determine the prefix for the document
                    if is_last_item:
                        # Last folder, use spaces
                        doc_prefix = "    └──" if is_last_doc else "    ├──"
                        render_continuation = "    " if is_last_doc else "    │"
                    else:
                        # Not last folder, use vertical bar continuation
                        doc_prefix = "│   └──" if is_last_doc else "│   ├──"
                        render_continuation = "│   " if is_last_doc else "│   │"

                    # Show document with render count if has additional renders
                    if has_additional_renders:
                        tree_lines.append(f"{doc_prefix} {doc_name} [+{len(additional_renders)} render(s)]")
                        # Add each render under the document
                        for render_idx, render in enumerate(additional_renders):
                            is_last_render = (render_idx == len(additional_renders) - 1)
                            render_type = render.get('type', 'unknown')
                            render_name = render.get('name', 'Unknown')
                            render_prefix = f"{render_continuation}   └──" if is_last_render else f"{render_continuation}   ├──"
                            tree_lines.append(f"{render_prefix} [{render_type}] {render_name}")
                    else:
                        tree_lines.append(f"{doc_prefix} {doc_name}")

        # Add root documents (documents not in any folder)
        for root_doc in root_documents:
            current_item += 1
            is_last_item = (current_item == total_items)

            doc_name = root_doc.get('fileName', 'Unknown')
            prefix = "└──" if is_last_item else "├──"
            tree_lines.append(f"{prefix} {doc_name}")

        # If no folders and no documents
        if total_items == 0:
            tree_lines.append("└── (empty)")

        tree_text = "\n".join(tree_lines)

        # Cache the result
        _tree_view_cache[case_id] = (tree_text, datetime.now(timezone.utc))
        logger.info(f"Generated and cached tree view for {case_id} ({len(documents)} documents)")

        return tree_text

    except Exception as e:
        logger.error(f"Failed to generate tree view for {case_id}: {e}", exc_info=True)
        return f"Case: {case_id}\n└── (error generating tree view)"


def invalidate_tree_cache(case_id: str) -> None:
    """
    S5-011: Invalidate the cached tree view for a case.

    Should be called whenever documents are added, deleted, or moved
    to ensure the tree view stays up-to-date.

    Args:
        case_id: The case ID whose cache should be invalidated
    """
    if case_id in _tree_view_cache:
        del _tree_view_cache[case_id]
        logger.debug(f"Invalidated tree view cache for {case_id}")
    else:
        logger.debug(f"No cached tree view to invalidate for {case_id}")


def get_cached_tree_stats() -> Dict[str, Any]:
    """
    S5-011: Get statistics about the tree view cache.

    Useful for monitoring and debugging cache performance.

    Returns:
        dict: Cache statistics including size and entries
    """
    return {
        "cache_size": len(_tree_view_cache),
        "cached_cases": list(_tree_view_cache.keys()),
        "cache_timestamps": {
            case_id: timestamp.isoformat()
            for case_id, (_, timestamp) in _tree_view_cache.items()
        }
    }
