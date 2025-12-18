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
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
