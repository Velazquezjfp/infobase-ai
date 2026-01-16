"""
Folder Management API for BAMF ACTE Companion.

Provides CRUD endpoints for managing case folder configurations.
Folders are persisted in folder_config.json for each case and synchronized
with the document explorer and admin panel.

Features:
    - Get folder configuration for a case
    - Add new folders (creates physical directory)
    - Update folder properties (name, order, mandatory)
    - Delete folders (only if empty, preserves documents)
    - Sync with admin panel changes
"""

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/folders", tags=["folders"])

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONTEXTS_DIR = BASE_DIR / "data" / "contexts" / "cases"
DOCUMENTS_DIR = Path(__file__).parent.parent.parent / "public" / "documents"


# Pydantic models
class FolderName(BaseModel):
    """Localized folder name."""
    de: str = Field(..., description="German name")
    en: str = Field(..., description="English name")


class FolderConfig(BaseModel):
    """Folder configuration."""
    id: str = Field(..., description="Folder ID (kebab-case)")
    nameKey: str = Field(..., description="Translation key")
    name: FolderName = Field(..., description="Localized names")
    mandatory: bool = Field(default=False, description="Whether folder is required")
    order: int = Field(..., description="Display order")


class FolderConfigResponse(BaseModel):
    """Response containing folder configuration."""
    schemaVersion: str
    caseId: str
    lastUpdated: str
    folders: List[FolderConfig]


class CreateFolderRequest(BaseModel):
    """Request to create a new folder."""
    id: str = Field(..., description="Folder ID (kebab-case, e.g., 'my-folder')")
    name: FolderName = Field(..., description="Localized names")
    mandatory: bool = Field(default=False, description="Whether folder is required")


class UpdateFolderRequest(BaseModel):
    """Request to update folder properties."""
    name: Optional[FolderName] = Field(None, description="New localized names")
    mandatory: Optional[bool] = Field(None, description="Whether folder is required")
    order: Optional[int] = Field(None, description="New display order")


class BulkUpdateFoldersRequest(BaseModel):
    """Request to update all folders at once (from admin panel)."""
    folders: List[FolderConfig]


def get_folder_config_path(case_id: str) -> Path:
    """Get path to folder configuration file for a case."""
    return CONTEXTS_DIR / case_id / "folder_config.json"


def get_documents_path(case_id: str) -> Path:
    """Get path to documents directory for a case."""
    return DOCUMENTS_DIR / case_id


def load_folder_config(case_id: str) -> Dict[str, Any]:
    """
    Load folder configuration for a case.

    Creates default config if not exists.
    """
    config_path = get_folder_config_path(case_id)

    if not config_path.exists():
        # Create default configuration
        default_config = {
            "schemaVersion": "1.0",
            "caseId": case_id,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "folders": [
                {
                    "id": "personal-data",
                    "nameKey": "personal-data",
                    "name": {"de": "Persönliche Daten", "en": "Personal Data"},
                    "mandatory": True,
                    "order": 1
                },
                {
                    "id": "evidence",
                    "nameKey": "evidence",
                    "name": {"de": "Evidence", "en": "Evidence"},
                    "mandatory": True,
                    "order": 2
                },
                {
                    "id": "emails",
                    "nameKey": "emails",
                    "name": {"de": "E-mails", "en": "Emails"},
                    "mandatory": True,
                    "order": 3
                },
                {
                    "id": "certificates",
                    "nameKey": "certificates",
                    "name": {"de": "Zertifikate", "en": "Certificates"},
                    "mandatory": True,
                    "order": 4
                },
                {
                    "id": "applications",
                    "nameKey": "applications",
                    "name": {"de": "Anträge", "en": "Applications"},
                    "mandatory": True,
                    "order": 5
                }
            ]
        }

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        logger.info(f"Created default folder config for case {case_id}")
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load folder config for {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load folder config: {str(e)}")


def save_folder_config(case_id: str, config: Dict[str, Any]) -> None:
    """Save folder configuration for a case."""
    config_path = get_folder_config_path(case_id)

    # Update timestamp
    config["lastUpdated"] = datetime.now(timezone.utc).isoformat()

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved folder config for case {case_id}")

        # Invalidate cached tree view so AI gets fresh folder names
        try:
            from backend.services.context_manager import invalidate_tree_cache
            invalidate_tree_cache(case_id)
            logger.info(f"Invalidated tree cache for case {case_id}")
        except Exception as cache_error:
            logger.warning(f"Could not invalidate tree cache: {cache_error}")

    except Exception as e:
        logger.error(f"Failed to save folder config for {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save folder config: {str(e)}")


def ensure_folder_directory(case_id: str, folder_id: str) -> Path:
    """Ensure physical folder directory exists."""
    folder_path = get_documents_path(case_id) / folder_id
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def is_folder_empty(case_id: str, folder_id: str) -> bool:
    """Check if a folder is empty (no files)."""
    folder_path = get_documents_path(case_id) / folder_id
    if not folder_path.exists():
        return True

    # Check for any files (excluding hidden files)
    files = [f for f in folder_path.iterdir() if not f.name.startswith('.')]
    return len(files) == 0


@router.get("/{case_id}", response_model=FolderConfigResponse)
async def get_folders(case_id: str) -> FolderConfigResponse:
    """
    Get folder configuration for a case.

    Returns all configured folders with their localized names,
    order, and mandatory status.
    """
    config = load_folder_config(case_id)

    # Ensure all physical directories exist
    for folder in config.get("folders", []):
        ensure_folder_directory(case_id, folder["id"])

    return FolderConfigResponse(**config)


@router.post("/{case_id}", response_model=FolderConfig)
async def create_folder(case_id: str, request: CreateFolderRequest) -> FolderConfig:
    """
    Create a new folder for a case.

    Creates both the configuration entry and the physical directory.
    """
    config = load_folder_config(case_id)
    folders = config.get("folders", [])

    # Check if folder ID already exists
    if any(f["id"] == request.id for f in folders):
        raise HTTPException(status_code=400, detail=f"Folder '{request.id}' already exists")

    # Validate folder ID (kebab-case)
    if not request.id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Folder ID must be alphanumeric with hyphens/underscores only")

    # Calculate next order
    max_order = max((f.get("order", 0) for f in folders), default=0)

    new_folder = {
        "id": request.id,
        "nameKey": request.id,
        "name": request.name.model_dump(),
        "mandatory": request.mandatory,
        "order": max_order + 1
    }

    folders.append(new_folder)
    config["folders"] = folders

    # Create physical directory
    ensure_folder_directory(case_id, request.id)

    save_folder_config(case_id, config)

    logger.info(f"Created folder '{request.id}' for case {case_id}")

    return FolderConfig(**new_folder)


@router.put("/{case_id}/{folder_id}", response_model=FolderConfig)
async def update_folder(case_id: str, folder_id: str, request: UpdateFolderRequest) -> FolderConfig:
    """
    Update folder properties.

    Can update name, mandatory status, and order.
    """
    config = load_folder_config(case_id)
    folders = config.get("folders", [])

    # Find folder
    folder_index = next((i for i, f in enumerate(folders) if f["id"] == folder_id), None)
    if folder_index is None:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_id}' not found")

    folder = folders[folder_index]

    # Apply updates
    if request.name is not None:
        folder["name"] = request.name.model_dump()
    if request.mandatory is not None:
        folder["mandatory"] = request.mandatory
    if request.order is not None:
        folder["order"] = request.order

    folders[folder_index] = folder
    config["folders"] = folders

    save_folder_config(case_id, config)

    logger.info(f"Updated folder '{folder_id}' for case {case_id}")

    return FolderConfig(**folder)


@router.delete("/{case_id}/{folder_id}")
async def delete_folder(case_id: str, folder_id: str, force: bool = False) -> Dict[str, str]:
    """
    Delete a folder.

    By default, only allows deletion of empty folders.
    Use force=true to delete folder with contents (documents will be moved to uploads).
    """
    config = load_folder_config(case_id)
    folders = config.get("folders", [])

    # Find folder
    folder_index = next((i for i, f in enumerate(folders) if f["id"] == folder_id), None)
    if folder_index is None:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_id}' not found")

    folder = folders[folder_index]

    # Check if folder is empty
    if not is_folder_empty(case_id, folder_id):
        if not force:
            raise HTTPException(
                status_code=400,
                detail=f"Folder '{folder_id}' is not empty. Use force=true to delete and move contents to uploads."
            )
        else:
            # Move contents to uploads folder
            source_path = get_documents_path(case_id) / folder_id
            uploads_path = get_documents_path(case_id) / "uploads"
            uploads_path.mkdir(parents=True, exist_ok=True)

            for item in source_path.iterdir():
                if not item.name.startswith('.'):
                    dest = uploads_path / item.name
                    # Handle name conflicts
                    counter = 1
                    while dest.exists():
                        stem = item.stem
                        suffix = item.suffix
                        dest = uploads_path / f"{stem}_{counter}{suffix}"
                        counter += 1
                    shutil.move(str(item), str(dest))
                    logger.info(f"Moved {item.name} to uploads folder")

    # Delete physical directory if empty now
    folder_path = get_documents_path(case_id) / folder_id
    if folder_path.exists() and is_folder_empty(case_id, folder_id):
        try:
            folder_path.rmdir()
            logger.info(f"Deleted physical directory for folder '{folder_id}'")
        except Exception as e:
            logger.warning(f"Could not delete directory {folder_path}: {e}")

    # Remove from config
    folders.pop(folder_index)
    config["folders"] = folders

    # Reorder remaining folders
    for i, f in enumerate(sorted(folders, key=lambda x: x.get("order", 0))):
        f["order"] = i + 1

    save_folder_config(case_id, config)

    logger.info(f"Deleted folder '{folder_id}' from case {case_id}")

    return {"message": f"Folder '{folder_id}' deleted successfully"}


@router.put("/{case_id}")
async def bulk_update_folders(case_id: str, request: BulkUpdateFoldersRequest) -> FolderConfigResponse:
    """
    Bulk update all folders (used by admin panel save).

    Replaces all folder configurations and creates/removes physical directories as needed.
    """
    config = load_folder_config(case_id)
    old_folders = {f["id"]: f for f in config.get("folders", [])}
    new_folders = {f.id: f for f in request.folders}

    # Determine folders to create and delete
    to_create = set(new_folders.keys()) - set(old_folders.keys())
    to_delete = set(old_folders.keys()) - set(new_folders.keys())

    # Create new folder directories
    for folder_id in to_create:
        ensure_folder_directory(case_id, folder_id)
        logger.info(f"Created directory for new folder '{folder_id}'")

    # Handle deleted folders (only if empty)
    for folder_id in to_delete:
        if not is_folder_empty(case_id, folder_id):
            logger.warning(f"Folder '{folder_id}' not empty, keeping directory but removing from config")
        else:
            folder_path = get_documents_path(case_id) / folder_id
            if folder_path.exists():
                try:
                    folder_path.rmdir()
                    logger.info(f"Deleted empty directory for folder '{folder_id}'")
                except Exception as e:
                    logger.warning(f"Could not delete directory {folder_path}: {e}")

    # Update config
    config["folders"] = [f.model_dump() for f in request.folders]
    save_folder_config(case_id, config)

    logger.info(f"Bulk updated folders for case {case_id}: +{len(to_create)} -{len(to_delete)}")

    return FolderConfigResponse(**config)


@router.post("/{case_id}/reorder")
async def reorder_folders(case_id: str, folder_order: List[str]) -> FolderConfigResponse:
    """
    Reorder folders by providing list of folder IDs in desired order.
    """
    config = load_folder_config(case_id)
    folders = config.get("folders", [])

    # Validate all IDs exist
    existing_ids = {f["id"] for f in folders}
    if set(folder_order) != existing_ids:
        raise HTTPException(status_code=400, detail="Folder order must contain exactly all existing folder IDs")

    # Reorder
    folder_map = {f["id"]: f for f in folders}
    reordered = []
    for i, folder_id in enumerate(folder_order):
        folder = folder_map[folder_id]
        folder["order"] = i + 1
        reordered.append(folder)

    config["folders"] = reordered
    save_folder_config(case_id, config)

    return FolderConfigResponse(**config)
