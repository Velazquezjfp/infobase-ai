"""
Session Manager Service for BAMF ACTE Companion (S001-F-007).

Owns the ephemeral one-shot-session reset logic. The sprint-1 demo treats the
backend as a deterministic seed: on logout, browser close, idle timeout, or
container startup the case state is wiped and reseeded from ``root_docs/`` and
the corresponding ``backend/data/contexts/templates/{caseType}/`` template.

Public API:
    - ROOT_DOCS_MAPPING: filename -> target folder under the case directory.
    - reset_case_to_seed(case_id): perform the documented reset for a case.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict

from backend.config import DOCUMENTS_BASE_PATH
from backend.services.document_registry import (
    load_manifest,
    reconcile,
    save_manifest,
    scan_filesystem,
    DocumentRegistry,
)

logger = logging.getLogger(__name__)


# Sprint-1 seed mapping: source filename in root_docs/ -> target case folder.
ROOT_DOCS_MAPPING: Dict[str, str] = {
    "Aufenthalstitel.png": "personal-data",
    "Geburtsurkunde.jpg": "personal-data",
    "Personalausweis.png": "personal-data",
    "Sprachzeugnis-Zertifikat.pdf": "certificates",
    "Anmeldeformular.pdf": "applications",
    "Notenspiegel.pdf": "evidence",
}

ROOT_DOCS_DIR = Path("root_docs")
CONTEXTS_BASE = Path("backend/data/contexts")
CASES_DIR = CONTEXTS_BASE / "cases"
TEMPLATES_DIR = CONTEXTS_BASE / "templates"

# Default case template when the case directory has been wiped and we cannot
# look up its caseType from disk. Sprint-1 only ships ACTE-2024-001 which is an
# integration_course case (see backend/data/contexts/templates/).
_DEFAULT_TEMPLATE = "integration_course"


def _detect_case_type(case_id: str) -> str:
    """Return caseType for ``case_id`` from its current case.json, or default."""
    case_json = CASES_DIR / case_id / "case.json"
    if case_json.exists():
        try:
            with open(case_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            case_type = data.get("caseType")
            if isinstance(case_type, str) and case_type:
                return case_type
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "Could not read caseType from %s (%s); defaulting to %s",
                case_json, exc, _DEFAULT_TEMPLATE,
            )
    return _DEFAULT_TEMPLATE


def _purge_documents(case_id: str) -> None:
    """Remove every file under ${DOCUMENTS_PATH}/{case_id}/."""
    case_docs = Path(DOCUMENTS_BASE_PATH) / case_id
    if case_docs.exists():
        shutil.rmtree(case_docs)
    case_docs.mkdir(parents=True, exist_ok=True)


def _restore_case_context(case_id: str, case_type: str) -> None:
    """Replace ${case_id}/ context dir with a fresh copy of the template."""
    template_path = TEMPLATES_DIR / case_type
    case_path = CASES_DIR / case_id

    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found for caseType={case_type}: {template_path}"
        )

    if case_path.exists():
        shutil.rmtree(case_path)

    shutil.copytree(template_path, case_path)

    # The template's case.json carries a placeholder caseId; rewrite it so the
    # file is consistent with the case_id we just restored.
    case_json = case_path / "case.json"
    if case_json.exists():
        try:
            with open(case_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["caseId"] = case_id
            with open(case_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to rewrite caseId in %s: %s", case_json, exc)


def _seed_documents(case_id: str) -> int:
    """Copy ROOT_DOCS_MAPPING files into the case folder. Returns count copied."""
    base = Path(DOCUMENTS_BASE_PATH) / case_id
    copied = 0
    for filename, folder in ROOT_DOCS_MAPPING.items():
        source = ROOT_DOCS_DIR / filename
        if not source.exists():
            logger.warning("Seed file missing: %s", source)
            continue
        target_folder = base / folder
        target_folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_folder / filename)
        copied += 1
    return copied


def _reset_manifest_for_case(case_id: str) -> None:
    """Drop existing manifest entries for ``case_id`` so reconcile re-creates them
    with fresh documentId / fileHash values for the new on-disk files."""
    registry = load_manifest()
    remaining = [
        doc for doc in registry.documents if doc.get("caseId") != case_id
    ]
    if len(remaining) != len(registry.documents):
        save_manifest(DocumentRegistry(
            version=registry.version,
            schemaVersion=registry.schemaVersion,
            lastUpdated=registry.lastUpdated,
            documents=remaining,
        ))


def reset_case_to_seed(case_id: str) -> Dict[str, int]:
    """Reset ``case_id`` back to its sprint-1 seed state.

    Steps (in order):
        1. Wipe ${DOCUMENTS_PATH}/{case_id}/ entirely.
        2. Restore backend/data/contexts/cases/{case_id}/ from the matching
           template under backend/data/contexts/templates/{caseType}/.
        3. Copy the six ROOT_DOCS_MAPPING files into the case folder structure.
        4. Drop manifest entries for {case_id} and call ``reconcile()`` so the
           manifest is rebuilt with fresh documentId / fileHash values.

    Args:
        case_id: case identifier, e.g. "ACTE-2024-001".

    Returns:
        dict with keys ``copied`` (seed files placed) and ``registered``
        (documents added by reconcile).
    """
    logger.info("Resetting case '%s' to seed state...", case_id)

    case_type = _detect_case_type(case_id)
    _purge_documents(case_id)
    _restore_case_context(case_id, case_type)
    copied = _seed_documents(case_id)
    _reset_manifest_for_case(case_id)

    # Rebuild manifest entries for the reseeded files.
    registry = load_manifest()
    fs_files = scan_filesystem(DOCUMENTS_BASE_PATH)
    report = reconcile(registry, fs_files)
    registered = len(report.added)

    logger.info(
        "Reset complete for '%s': copied=%d, manifest_added=%d",
        case_id, copied, registered,
    )
    return {"copied": copied, "registered": registered}
