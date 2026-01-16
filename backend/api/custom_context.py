"""
Custom Context Rules API for BAMF AI Case Management System.

S5-017: Provides endpoints for managing custom validation rules and required documents
that users can add via /Aktenkontext slash commands.

Endpoints:
    GET /api/custom-context/{case_id}: Get all custom rules for a case
    POST /api/custom-context/{case_id}/rule: Add a new validation rule
    POST /api/custom-context/{case_id}/document: Add a new required document
    DELETE /api/custom-context/{case_id}/{rule_id}: Remove a custom rule
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/custom-context")

# Base path for custom context rules
CUSTOM_CONTEXT_PATH = Path("backend/data/contexts/cases")


class ValidationRuleRequest(BaseModel):
    """Request model for adding a validation rule."""
    targetFolder: Optional[str] = Field(None, description="Target folder for the rule (optional)")
    ruleType: str = Field(..., description="Type of rule: file_type, content, metadata, completeness")
    rule: str = Field(..., description="The rule description/text")


class RequiredDocumentRequest(BaseModel):
    """Request model for adding a required document."""
    description: str = Field(..., description="Description of the required document")
    targetFolder: Optional[str] = Field(None, description="Target folder for the document")


class CustomContextRule(BaseModel):
    """Model for a custom context rule."""
    id: str
    type: Literal['validation_rule', 'required_document']
    createdAt: str
    targetFolder: Optional[str] = None
    rule: str
    ruleType: Optional[str] = None


class CustomContextResponse(BaseModel):
    """Response model for custom context operations."""
    success: bool
    message: str
    rule: Optional[CustomContextRule] = None
    rules: Optional[List[CustomContextRule]] = None


def get_custom_rules_path(case_id: str) -> Path:
    """Get the path to the custom rules file for a case."""
    return CUSTOM_CONTEXT_PATH / case_id / "custom_rules.json"


def load_custom_rules(case_id: str) -> List[Dict[str, Any]]:
    """Load custom rules for a case."""
    rules_path = get_custom_rules_path(case_id)

    if not rules_path.exists():
        return []

    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('rules', [])
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load custom rules for {case_id}: {e}")
        return []


def save_custom_rules(case_id: str, rules: List[Dict[str, Any]]) -> bool:
    """Save custom rules for a case."""
    rules_path = get_custom_rules_path(case_id)

    # Ensure parent directory exists
    rules_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump({
                'caseId': case_id,
                'lastModified': datetime.now(timezone.utc).isoformat(),
                'rules': rules
            }, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Failed to save custom rules for {case_id}: {e}")
        return False


@router.get(
    "/{case_id}",
    response_model=CustomContextResponse,
    summary="Get custom context rules for a case",
    description="Retrieve all custom validation rules and required documents for a case."
)
async def get_custom_rules(case_id: str) -> CustomContextResponse:
    """Get all custom context rules for a case."""
    logger.info(f"Getting custom rules for case: {case_id}")

    # Check if case exists
    case_path = CUSTOM_CONTEXT_PATH / case_id
    if not case_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Case not found", "case_id": case_id}
        )

    rules = load_custom_rules(case_id)

    return CustomContextResponse(
        success=True,
        message=f"Found {len(rules)} custom rule(s)",
        rules=[CustomContextRule(**r) for r in rules]
    )


@router.post(
    "/{case_id}/rule",
    response_model=CustomContextResponse,
    summary="Add a validation rule",
    description="Add a custom validation rule to the case context."
)
async def add_validation_rule(case_id: str, request: ValidationRuleRequest) -> CustomContextResponse:
    """Add a new validation rule to the case."""
    logger.info(f"Adding validation rule for case {case_id}: {request.rule}")

    # Check if case exists
    case_path = CUSTOM_CONTEXT_PATH / case_id
    if not case_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Case not found", "case_id": case_id}
        )

    # Create new rule
    new_rule = {
        'id': f"custom-rule-{uuid.uuid4().hex[:8]}",
        'type': 'validation_rule',
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'targetFolder': request.targetFolder,
        'rule': request.rule,
        'ruleType': request.ruleType
    }

    # Load existing rules and add new one
    rules = load_custom_rules(case_id)
    rules.append(new_rule)

    # Save rules
    if not save_custom_rules(case_id, rules):
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to save rule", "case_id": case_id}
        )

    logger.info(f"Successfully added validation rule {new_rule['id']} for case {case_id}")

    return CustomContextResponse(
        success=True,
        message="Validation rule added successfully",
        rule=CustomContextRule(**new_rule)
    )


@router.post(
    "/{case_id}/document",
    response_model=CustomContextResponse,
    summary="Add a required document",
    description="Add a custom required document to the case context."
)
async def add_required_document(case_id: str, request: RequiredDocumentRequest) -> CustomContextResponse:
    """Add a new required document to the case."""
    logger.info(f"Adding required document for case {case_id}: {request.description}")

    # Check if case exists
    case_path = CUSTOM_CONTEXT_PATH / case_id
    if not case_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Case not found", "case_id": case_id}
        )

    # Create new required document rule
    new_rule = {
        'id': f"custom-doc-{uuid.uuid4().hex[:8]}",
        'type': 'required_document',
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'targetFolder': request.targetFolder,
        'rule': request.description,
        'ruleType': 'document_requirement'
    }

    # Load existing rules and add new one
    rules = load_custom_rules(case_id)
    rules.append(new_rule)

    # Save rules
    if not save_custom_rules(case_id, rules):
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to save document requirement", "case_id": case_id}
        )

    logger.info(f"Successfully added required document {new_rule['id']} for case {case_id}")

    return CustomContextResponse(
        success=True,
        message="Required document added successfully",
        rule=CustomContextRule(**new_rule)
    )


@router.delete(
    "/{case_id}/{rule_id}",
    response_model=CustomContextResponse,
    summary="Remove a custom rule",
    description="Remove a custom validation rule or required document from the case."
)
async def remove_custom_rule(case_id: str, rule_id: str) -> CustomContextResponse:
    """Remove a custom rule from the case."""
    logger.info(f"Removing rule {rule_id} from case {case_id}")

    # Check if case exists
    case_path = CUSTOM_CONTEXT_PATH / case_id
    if not case_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Case not found", "case_id": case_id}
        )

    # Load existing rules
    rules = load_custom_rules(case_id)

    # Find and remove the rule
    rule_to_remove = None
    for rule in rules:
        if rule['id'] == rule_id:
            rule_to_remove = rule
            break

    if not rule_to_remove:
        raise HTTPException(
            status_code=404,
            detail={"error": "Rule not found", "rule_id": rule_id}
        )

    rules.remove(rule_to_remove)

    # Save updated rules
    if not save_custom_rules(case_id, rules):
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to save rules", "case_id": case_id}
        )

    logger.info(f"Successfully removed rule {rule_id} from case {case_id}")

    return CustomContextResponse(
        success=True,
        message="Rule removed successfully",
        rule=CustomContextRule(**rule_to_remove)
    )
