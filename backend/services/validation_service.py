"""
Case Validation Service for BAMF AI Case Management System.

This module provides AI-powered case validation functionality using the Gemini API.
It analyzes form data, documents, and case context to evaluate case completeness
before submission.

Features:
    - AI-powered validation using Gemini
    - Structured validation results with score, warnings, and recommendations
    - Document tree analysis
    - Form field completeness checking
    - Multi-language support (German/English)
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from backend.services.context_manager import ContextManager, generate_document_tree
from backend.services.document_registry import get_documents_by_case
from backend.api.custom_context import load_custom_rules

logger = logging.getLogger(__name__)


@dataclass
class ValidationWarning:
    """Represents a single validation warning."""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # e.g., 'missing_documents', 'incomplete_form'
    title: str
    details: List[str]


@dataclass
class ValidationResult:
    """Result of case validation."""
    success: bool
    score: int = 0  # 1-100
    summary: str = ""
    warnings: List[ValidationWarning] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "score": self.score,
            "summary": self.summary,
            "warnings": [
                {
                    "severity": w.severity,
                    "category": w.category,
                    "title": w.title,
                    "details": w.details
                }
                for w in self.warnings
            ],
            "recommendations": self.recommendations,
            "error": self.error
        }


class CaseValidationService:
    """
    Service for AI-powered case validation.

    Analyzes case data including form fields, documents, and context
    to provide a structured validation assessment.
    """

    _instance: Optional['CaseValidationService'] = None
    _model: Optional[Any] = None
    _context_manager: Optional[ContextManager] = None

    def __new__(cls) -> 'CaseValidationService':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the validation service."""
        if self._model is None:
            self._initialize_model()
        if self._context_manager is None:
            try:
                self._context_manager = ContextManager()
            except ValueError as e:
                logger.warning(f"Could not initialize context manager: {e}")

    def _initialize_model(self) -> None:
        """Initialize the Gemini model directly for validation."""
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found")
            raise ValueError("API key not configured")

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Validation service Gemini model initialized")

    async def validate_case(
        self,
        case_id: str,
        form_data: Dict[str, str],
        language: str = 'de',
        document_contents: Optional[Dict[str, str]] = None
    ) -> ValidationResult:
        """
        Validate a case for completeness before submission.

        Args:
            case_id: The case ID to validate (e.g., "ACTE-2024-001")
            form_data: Dictionary of form field IDs to values
            language: Language code ('de' or 'en') for responses
            document_contents: Optional dict of document IDs to cached text content

        Returns:
            ValidationResult: Structured validation assessment

        Example:
            >>> service = CaseValidationService()
            >>> result = await service.validate_case(
            ...     "ACTE-2024-001",
            ...     {"fullName": "John Doe", "dateOfBirth": "1990-01-15"},
            ...     "en"
            ... )
            >>> print(result.score)
            85
        """
        try:
            logger.info(f"Starting case validation for {case_id}")

            # Build the validation prompt
            prompt = self._build_validation_prompt(
                case_id,
                form_data,
                language,
                document_contents
            )

            logger.info(f"Validation prompt length: {len(prompt)} chars")

            # Call Gemini API directly with focused config for validation
            generation_config = GenerationConfig(
                temperature=0.3,  # Lower temperature for consistent JSON
                top_p=0.8,
                top_k=40,
                max_output_tokens=4096,  # Plenty of room for response
            )

            response_obj = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            response = response_obj.text

            logger.info(f"Gemini response length: {len(response)} chars")

            # Parse the structured response
            result = self._parse_validation_response(response, language)

            logger.info(
                f"Validation complete for {case_id}: "
                f"score={result.score}, warnings={len(result.warnings)}"
            )

            return result

        except Exception as e:
            logger.error(f"Validation failed for case {case_id}: {e}", exc_info=True)
            return ValidationResult(
                success=False,
                error=str(e)
            )

    def _build_validation_prompt(
        self,
        case_id: str,
        form_data: Dict[str, str],
        language: str,
        document_contents: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Build the validation prompt for Gemini.

        Args:
            case_id: The case ID
            form_data: Form field data
            language: Response language
            document_contents: Optional cached document content

        Returns:
            str: The complete validation prompt
        """
        parts = []

        # System instruction
        language_name = 'German' if language == 'de' else 'English'
        parts.append(f"""You are a BAMF case validation assistant. Analyze the following case for completeness and accuracy.
IMPORTANT: Respond ONLY with a valid JSON object. Do not include any other text before or after the JSON.
IMPORTANT: Respond in {language_name} language for the summary, warnings, and recommendations.""")

        # Case context
        case_context = None
        if self._context_manager:
            try:
                case_context = self._context_manager.load_case_context(case_id)
            except FileNotFoundError:
                logger.warning(f"Case context not found for {case_id}")
            except Exception as e:
                logger.error(f"Error loading case context: {e}")

        if case_context:
            parts.append("\n**Case Information:**")
            parts.append(f"- Case ID: {case_context.get('caseId', case_id)}")
            parts.append(f"- Case Type: {case_context.get('caseType', 'Unknown')}")
            parts.append(f"- Case Name: {case_context.get('name', 'Unknown')}")

            # Required documents from context
            required_docs = case_context.get('requiredDocuments', [])
            if required_docs:
                parts.append("\n**Required Documents:**")
                for doc in required_docs:
                    criticality = doc.get('criticality', 'optional')
                    doc_name = doc.get('name', 'Unknown')
                    parts.append(f"- [{criticality.upper()}] {doc_name}")

        # Form data
        parts.append("\n**Form Data:**")
        if form_data:
            for field_id, value in form_data.items():
                status = "filled" if value and value.strip() else "empty"
                display_value = value if value else "(not provided)"
                parts.append(f"- {field_id}: {display_value} [{status}]")
        else:
            parts.append("- (no form data provided)")

        # Document tree
        try:
            tree_view = generate_document_tree(case_id)
            parts.append(f"\n**Document Tree:**\n{tree_view}")
        except Exception as e:
            logger.warning(f"Could not generate document tree: {e}")
            parts.append(f"\n**Document Tree:** (unavailable)")

        # Document contents if provided
        if document_contents:
            parts.append("\n**Document Contents (extracted text):**")
            for doc_id, content in document_contents.items():
                preview = content[:500] + "..." if len(content) > 500 else content
                parts.append(f"\n[Document: {doc_id}]\n{preview}")

        # S5-017: Load and include custom rules in validation
        try:
            custom_rules = load_custom_rules(case_id)
            if custom_rules:
                custom_validation_rules = [r for r in custom_rules if r.get('type') == 'validation_rule']
                custom_documents = [r for r in custom_rules if r.get('type') == 'required_document']

                if custom_validation_rules:
                    parts.append("\n**Custom Validation Rules (user-defined - MUST be checked):**")
                    for rule in custom_validation_rules:
                        target_folder = rule.get('targetFolder')
                        rule_text = rule.get('rule', '')
                        if target_folder:
                            parts.append(f"- [Folder: {target_folder}] {rule_text}")
                        else:
                            parts.append(f"- {rule_text}")

                if custom_documents:
                    parts.append("\n**Custom Required Documents (user-defined - MUST be verified):**")
                    for doc in custom_documents:
                        doc_desc = doc.get('rule', '')
                        parts.append(f"- [CUSTOM REQUIREMENT] {doc_desc}")
                        parts.append("  (Check if an anonymized/rendered version exists for this requirement)")
        except Exception as e:
            logger.warning(f"Could not load custom rules for validation: {e}")

        # Validation task - Keep instructions concise to leave room for response
        parts.append("""
**Task:**
Return a JSON object with this EXACT structure (keep values SHORT):
{"score":<1-100>,"summary":"<1 sentence max 50 words>","warnings":[{"severity":"critical|high|medium|low","category":"<type>","title":"<5 words max>","details":["<issue>"]}],"recommendations":["<step 1>","<step 2>"]}

Score: 90-100=ready, 70-89=minor issues, 50-69=significant, <50=critical issues.
Check: documents, form fields, consistency, CUSTOM RULES.
Return ONLY valid JSON, no markdown, no extra text.""")

        return "\n".join(parts)

    def _parse_validation_response(self, response: str, language: str = 'de') -> ValidationResult:
        """
        Parse the Gemini response into a ValidationResult.

        Args:
            response: Raw response text from Gemini
            language: Language code for fallback messages

        Returns:
            ValidationResult: Parsed validation result
        """
        # Localized fallback messages
        fallback_messages = {
            'de': {
                'parsing_title': 'Antwort-Parsing-Problem',
                'parsing_detail': 'Die KI-Antwort konnte nicht verarbeitet werden. Bitte manuell überprüfen.',
                'review_manually': 'Fall manuell überprüfen',
                'try_again': 'Validierung erneut versuchen',
                'parse_failed': 'Validierung abgeschlossen, aber Antwort konnte nicht verarbeitet werden.',
            },
            'en': {
                'parsing_title': 'Response Parsing Issue',
                'parsing_detail': 'The AI response could not be parsed. Please review manually.',
                'review_manually': 'Review case manually',
                'try_again': 'Try validation again',
                'parse_failed': 'Validation completed but response parsing failed.',
            }
        }
        msgs = fallback_messages.get(language, fallback_messages['de'])

        try:
            # Clean up the response - remove markdown code blocks if present
            cleaned_response = response.strip()

            # Log raw response for debugging
            logger.info(f"Raw validation response length: {len(cleaned_response)}")
            logger.info(f"Raw validation response (first 500): {repr(cleaned_response[:500])}")

            # Remove markdown code block wrappers (```json ... ``` or ``` ... ```)
            if '```' in cleaned_response:
                # Try to extract content between code blocks
                code_block_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', cleaned_response)
                if code_block_match:
                    cleaned_response = code_block_match.group(1).strip()
                    logger.info(f"Extracted from code block, length: {len(cleaned_response)}")
                else:
                    # Fallback: just remove the ``` markers
                    cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
                    logger.info(f"Removed code markers, length: {len(cleaned_response)}")
                    logger.info(f"After code marker removal (first 300): {repr(cleaned_response[:300])}")

            # Try to extract JSON object from the response
            # First try to find complete JSON (with closing brace)
            json_match = re.search(r'\{[\s\S]*\}', cleaned_response)
            if json_match:
                cleaned_response = json_match.group(0)
                logger.info(f"Extracted complete JSON object, length: {len(cleaned_response)}")
            else:
                # Response might be truncated - try to find partial JSON starting with {
                json_start = re.search(r'\{[\s\S]*', cleaned_response)
                if json_start:
                    cleaned_response = json_start.group(0)
                    logger.warning(f"Found truncated JSON (no closing brace), length: {len(cleaned_response)}")
                else:
                    logger.warning("No JSON object found in response")
                    raise json.JSONDecodeError("No JSON object found", cleaned_response, 0)

            # Try to fix truncated JSON before parsing
            if cleaned_response:
                # Check if string is unterminated (odd number of quotes excluding escaped ones)
                # Count unescaped quotes
                unescaped_quotes = len(re.findall(r'(?<!\\)"', cleaned_response))
                if unescaped_quotes % 2 == 1:
                    # Odd number of quotes - need to close the string
                    cleaned_response += '"'
                    logger.info("Added closing quote for truncated string")

                open_braces = cleaned_response.count('{')
                close_braces = cleaned_response.count('}')
                open_brackets = cleaned_response.count('[')
                close_brackets = cleaned_response.count(']')

                # Fix missing closing brackets/braces
                if open_brackets > close_brackets:
                    cleaned_response += ']' * (open_brackets - close_brackets)
                    logger.info(f"Added {open_brackets - close_brackets} closing brackets")
                if open_braces > close_braces:
                    cleaned_response += '}' * (open_braces - close_braces)
                    logger.info(f"Added {open_braces - close_braces} closing braces")

                logger.debug(f"Fixed JSON (last 100 chars): {cleaned_response[-100:]}")

            # Parse JSON
            data = json.loads(cleaned_response)

            # Extract warnings
            warnings = []
            for w in data.get('warnings', []):
                warnings.append(ValidationWarning(
                    severity=w.get('severity', 'medium'),
                    category=w.get('category', 'general'),
                    title=w.get('title', 'Issue'),
                    details=w.get('details', [])
                ))

            return ValidationResult(
                success=True,
                score=data.get('score', 50),
                summary=data.get('summary', ''),
                warnings=warnings,
                recommendations=data.get('recommendations', [])
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation response as JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}")

            # Return a fallback result with localized messages
            return ValidationResult(
                success=True,
                score=50,
                summary=response[:200] if response else msgs['parse_failed'],
                warnings=[ValidationWarning(
                    severity='medium',
                    category='parsing',
                    title=msgs['parsing_title'],
                    details=[msgs['parsing_detail']]
                )],
                recommendations=[msgs['review_manually'], msgs['try_again']]
            )

        except Exception as e:
            logger.error(f"Error parsing validation response: {e}", exc_info=True)
            return ValidationResult(
                success=False,
                error=f"Failed to parse validation response: {str(e)}"
            )


# Singleton accessor
def get_validation_service() -> CaseValidationService:
    """Get the singleton validation service instance."""
    return CaseValidationService()
