"""
Document Registry Service for BAMF AI Case Management System.

This module manages the document registry/manifest system that tracks all uploaded
documents, their metadata, renders (anonymized/translated versions), and folder
locations. The registry persists across application restarts to ensure documents
remain visible after container restarts.

Key Features:
    - Document manifest persistence (JSON file)
    - Filesystem reconciliation on startup
    - Orphaned file detection and registration
    - Missing file detection and logging
    - File integrity verification (SHA-256 hashes)
    - Document tree building for frontend

Architecture:
    - Single source of truth: backend/data/document_manifest.json
    - Container-friendly: Uses configurable DOCUMENTS_BASE_PATH
    - Stateless functions for testability and reliability

Related Requirements:
    - S5-007: Container-Compatible File Persistence
    - D-S5-002: Document Registry Schema
"""

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple

logger = logging.getLogger(__name__)

# Path to the document manifest file
MANIFEST_PATH = Path("backend/data/document_manifest.json")


# ============================================================================
# Type Definitions
# ============================================================================

class DocumentRender(NamedTuple):
    """Represents a render (anonymized or translated version) of a document."""
    renderId: str
    type: str  # 'anonymized' or 'translated'
    filePath: str
    createdAt: str
    language: Optional[str] = None


class DocumentRegistryEntry(NamedTuple):
    """Represents a document entry in the registry."""
    documentId: str
    caseId: str
    folderId: Optional[str]
    fileName: str
    filePath: str
    uploadedAt: str
    fileHash: str
    renders: List[Dict]


class DocumentRegistry(NamedTuple):
    """Root structure of the document registry manifest."""
    version: str
    schemaVersion: str
    lastUpdated: str
    documents: List[Dict]


class FileInfo(NamedTuple):
    """Information about a file found during filesystem scan."""
    filePath: str
    caseId: str
    folderId: Optional[str]
    fileName: str
    fileHash: str


class ReconcileReport(NamedTuple):
    """Report of reconciliation between manifest and filesystem."""
    added: List[str]  # Files added to manifest (orphaned files)
    missing: List[str]  # Files in manifest but not on disk
    integrity_failed: List[str]  # Files with hash mismatches


# ============================================================================
# Part 1: Manifest I/O
# ============================================================================

def load_manifest() -> DocumentRegistry:
    """
    Load the document manifest from disk.

    Reads the manifest JSON file and returns a DocumentRegistry object.
    If the manifest doesn't exist or is corrupt, returns an empty registry.

    Returns:
        DocumentRegistry: The loaded document registry.

    Example:
        >>> registry = load_manifest()
        >>> print(f"Loaded {len(registry.documents)} documents")
    """
    try:
        if not MANIFEST_PATH.exists():
            logger.warning(f"Manifest file not found at {MANIFEST_PATH}. Creating new empty manifest.")
            return _create_empty_manifest()

        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required fields
        if not all(key in data for key in ['version', 'schemaVersion', 'lastUpdated', 'documents']):
            logger.error("Manifest file is missing required fields. Creating new empty manifest.")
            return _create_empty_manifest()

        logger.info(f"Successfully loaded manifest with {len(data['documents'])} documents")
        return DocumentRegistry(
            version=data['version'],
            schemaVersion=data['schemaVersion'],
            lastUpdated=data['lastUpdated'],
            documents=data['documents']
        )

    except json.JSONDecodeError as e:
        logger.error(f"Manifest file is corrupt (invalid JSON): {e}. Creating new empty manifest.")
        return _create_empty_manifest()

    except Exception as e:
        logger.error(f"Unexpected error loading manifest: {e}. Creating new empty manifest.", exc_info=True)
        return _create_empty_manifest()


def save_manifest(registry: DocumentRegistry) -> None:
    """
    Save the document manifest to disk.

    Writes the registry to the manifest JSON file with pretty formatting.
    Automatically updates the lastUpdated timestamp.

    Args:
        registry: The DocumentRegistry to save.

    Raises:
        OSError: If file write operation fails.

    Example:
        >>> registry = load_manifest()
        >>> # ... modify registry ...
        >>> save_manifest(registry)
    """
    try:
        # Ensure the data directory exists
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Update lastUpdated timestamp
        registry_dict = registry._asdict()
        registry_dict['lastUpdated'] = datetime.now(timezone.utc).isoformat()

        # Write to file with pretty formatting
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(registry_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved manifest with {len(registry.documents)} documents")

    except OSError as e:
        logger.error(f"Failed to save manifest: {e}", exc_info=True)
        raise

    except Exception as e:
        logger.error(f"Unexpected error saving manifest: {e}", exc_info=True)
        raise


def _create_empty_manifest() -> DocumentRegistry:
    """
    Create a new empty document registry.

    Returns:
        DocumentRegistry: A new empty registry with current timestamp.
    """
    now = datetime.now(timezone.utc).isoformat()
    return DocumentRegistry(
        version="1.0",
        schemaVersion="1.0",
        lastUpdated=now,
        documents=[]
    )


# ============================================================================
# Part 2: Registry Operations - Register Document
# ============================================================================

def register_document(
    case_id: str,
    folder_id: Optional[str],
    file_path: str,
    file_name: str
) -> Dict:
    """
    Register a new document in the manifest.

    Creates a new document entry with metadata, calculates file hash,
    and adds it to the manifest. Automatically saves the manifest after registration.

    Args:
        case_id: Case ID the document belongs to (e.g., "ACTE-2024-001")
        folder_id: Optional folder ID within the case (e.g., "personal-data")
        file_path: Full file path to the document (e.g., "public/documents/...")
        file_name: Original filename of the document

    Returns:
        dict: The created DocumentRegistryEntry as a dictionary.

    Example:
        >>> entry = register_document(
        ...     "ACTE-2024-001",
        ...     "personal-data",
        ...     "public/documents/ACTE-2024-001/personal-data/Birth_Certificate.jpg",
        ...     "Birth_Certificate.jpg"
        ... )
        >>> print(f"Registered document {entry['documentId']}")
    """
    try:
        # Load current manifest
        registry = load_manifest()

        # Generate unique document ID
        document_id = generate_document_id()

        # Calculate file hash for integrity verification
        file_hash = calculate_file_hash(file_path)

        # Get current timestamp
        uploaded_at = datetime.now(timezone.utc).isoformat()

        # S5-006: Create original render entry for the document
        original_render = {
            "id": f"render_{generate_document_id()}",
            "type": "original",
            "name": file_name,
            "filePath": file_path,
            "createdAt": uploaded_at,
            "metadata": {}
        }

        # Create document entry with original render
        document_entry = {
            "documentId": document_id,
            "caseId": case_id,
            "folderId": folder_id,
            "fileName": file_name,
            "filePath": file_path,
            "uploadedAt": uploaded_at,
            "fileHash": file_hash,
            "renders": [original_render]  # S5-006: Include original as first render
        }

        # Add to manifest
        documents_list = list(registry.documents)
        documents_list.append(document_entry)

        # Create updated registry
        updated_registry = DocumentRegistry(
            version=registry.version,
            schemaVersion=registry.schemaVersion,
            lastUpdated=datetime.now(timezone.utc).isoformat(),
            documents=documents_list
        )

        # Save manifest
        save_manifest(updated_registry)

        logger.info(f"Registered document {document_id}: {file_name} in case {case_id}/{folder_id or 'root'}")
        return document_entry

    except Exception as e:
        logger.error(f"Failed to register document {file_name}: {e}", exc_info=True)
        raise


# ============================================================================
# Part 3: Unregister Document
# ============================================================================

def unregister_document(document_id: str) -> bool:
    """
    Unregister a document from the manifest with cascade deletion.

    Removes the document entry from the manifest and saves the changes.
    S5-003/S5-006: Also deletes all associated render files from filesystem.

    Args:
        document_id: The unique document ID to unregister.

    Returns:
        bool: True if document was found and removed, False if not found.

    Example:
        >>> success = unregister_document("doc_001")
        >>> if success:
        ...     print("Document unregistered successfully")
    """
    try:
        # Load current manifest
        registry = load_manifest()

        # S5-003/S5-006: Find the document to get its renders before deletion
        document_to_delete = None
        for doc in registry.documents:
            if doc.get('documentId') == document_id:
                document_to_delete = doc
                break

        # S5-003/S5-006: Cascade delete all render files (except original)
        if document_to_delete and document_to_delete.get('renders'):
            from pathlib import Path
            for render in document_to_delete['renders']:
                # Skip 'original' render (it's the main file, deleted separately)
                if render.get('type') == 'original':
                    continue

                # Delete render file from filesystem
                render_file_path = Path(render.get('filePath', ''))
                if render_file_path.exists():
                    try:
                        render_file_path.unlink()
                        logger.info(f"Cascade deleted render file: {render_file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete render file {render_file_path}: {e}")
                        # Continue with other renders even if one fails

        # Find and remove the document
        original_count = len(registry.documents)
        documents_list = [
            doc for doc in registry.documents
            if doc.get('documentId') != document_id
        ]
        new_count = len(documents_list)

        if original_count == new_count:
            logger.warning(f"Document {document_id} not found in manifest")
            return False

        # Create updated registry
        updated_registry = DocumentRegistry(
            version=registry.version,
            schemaVersion=registry.schemaVersion,
            lastUpdated=datetime.now(timezone.utc).isoformat(),
            documents=documents_list
        )

        # Save manifest
        save_manifest(updated_registry)

        logger.info(f"Unregistered document {document_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to unregister document {document_id}: {e}", exc_info=True)
        raise


def find_document_by_path(case_id: str, folder_id: Optional[str], file_name: str) -> Optional[Dict]:
    """
    Find a document in the manifest by its case, folder, and filename.

    Args:
        case_id: Case ID the document belongs to.
        folder_id: Optional folder ID within the case.
        file_name: Filename of the document.

    Returns:
        dict: The document entry if found, None otherwise.
    """
    try:
        registry = load_manifest()

        for doc in registry.documents:
            if (doc.get('caseId') == case_id and
                doc.get('folderId') == folder_id and
                doc.get('fileName') == file_name):
                return doc

        return None

    except Exception as e:
        logger.error(f"Failed to find document {file_name}: {e}", exc_info=True)
        return None


# ============================================================================
# Part 4: Filesystem Scanner
# ============================================================================

def scan_filesystem(base_path: str) -> List[FileInfo]:
    """
    Scan the documents directory and return information about all files found.

    Recursively walks the directory structure and extracts case_id, folder_id,
    and filename from the path. Calculates file hash for each file.

    Args:
        base_path: The base documents directory path (e.g., "public/documents").

    Returns:
        List[FileInfo]: List of file information tuples.

    Example:
        >>> files = scan_filesystem("public/documents")
        >>> print(f"Found {len(files)} files")
    """
    files = []
    base = Path(base_path)

    if not base.exists():
        logger.warning(f"Documents directory does not exist: {base_path}")
        return files

    try:
        # Walk the directory tree
        for file_path in base.rglob('*'):
            # Skip directories and hidden files
            if file_path.is_dir() or file_path.name.startswith('.'):
                continue

            # Skip system files
            if file_path.name in ['Thumbs.db', '.DS_Store', 'desktop.ini']:
                continue

            try:
                # Extract case_id and folder_id from path structure
                # Expected structure: base_path/case_id/folder_id/filename
                relative_path = file_path.relative_to(base)
                parts = relative_path.parts

                if len(parts) < 2:
                    logger.warning(f"Skipping file with unexpected path structure: {file_path}")
                    continue

                case_id = parts[0]

                # If there are 3+ parts, middle parts are folder_id
                if len(parts) == 2:
                    folder_id = None
                    file_name = parts[1]
                else:
                    folder_id = parts[1]
                    file_name = parts[-1]

                # Calculate file hash
                file_hash = calculate_file_hash(str(file_path))

                files.append(FileInfo(
                    filePath=str(file_path),
                    caseId=case_id,
                    folderId=folder_id,
                    fileName=file_name,
                    fileHash=file_hash
                ))

            except Exception as e:
                logger.warning(f"Failed to process file {file_path}: {e}")
                continue

        logger.info(f"Filesystem scan found {len(files)} files")
        return files

    except Exception as e:
        logger.error(f"Failed to scan filesystem: {e}", exc_info=True)
        return []


# ============================================================================
# Part 5: Reconciliation Logic
# ============================================================================

def reconcile(registry: DocumentRegistry, filesystem_files: List[FileInfo]) -> ReconcileReport:
    """
    Reconcile the manifest with the filesystem state.

    Compares manifest entries with files found on disk and:
    1. Adds orphaned files (on disk but not in manifest) to the manifest
    2. Logs missing files (in manifest but not on disk)
    3. Verifies file hashes for integrity

    Args:
        registry: The current document registry.
        filesystem_files: List of files found during filesystem scan.

    Returns:
        ReconcileReport: Report of reconciliation actions.

    Example:
        >>> registry = load_manifest()
        >>> files = scan_filesystem("public/documents")
        >>> report = reconcile(registry, files)
        >>> print(f"Added {len(report.added)} orphaned files")
    """
    added = []
    missing = []
    integrity_failed = []

    # Create a set of (caseId, folderId, fileName) from manifest for quick lookup
    manifest_files = {
        (doc.get('caseId'), doc.get('folderId'), doc.get('fileName')): doc
        for doc in registry.documents
    }

    # Create a set of (caseId, folderId, fileName) from filesystem for quick lookup
    fs_files_set = {
        (f.caseId, f.folderId, f.fileName): f
        for f in filesystem_files
    }

    # S5-006: Helper function to check if a file is a render file (not a top-level document)
    def is_render_file(filename: str) -> bool:
        """Check if a filename matches render file patterns (anonymized, translated, etc.)"""
        # S5-004/S5-008: Updated patterns to match _translated_de, _translated_en, etc.
        render_patterns = ['_anonymized.', '_translated_', '_translated.', '_annotated.']
        return any(pattern in filename for pattern in render_patterns)

    # Find orphaned files (on disk but not in manifest)
    documents_list = list(registry.documents)
    for file_info in filesystem_files:
        key = (file_info.caseId, file_info.folderId, file_info.fileName)
        if key not in manifest_files:
            # S5-006: Skip render files - they should only exist as renders, not top-level documents
            if is_render_file(file_info.fileName):
                logger.debug(f"Skipping render file during reconciliation: {file_info.filePath}")
                continue

            # Orphaned file - add to manifest
            document_id = generate_document_id()
            uploaded_at = datetime.now(timezone.utc).isoformat()

            # S5-006: Create original render entry for the document
            original_render = {
                "id": f"render_original_{generate_document_id()}",
                "type": "original",
                "name": file_info.fileName,
                "filePath": file_info.filePath,
                "createdAt": uploaded_at,
                "metadata": {}
            }

            document_entry = {
                "documentId": document_id,
                "caseId": file_info.caseId,
                "folderId": file_info.folderId,
                "fileName": file_info.fileName,
                "filePath": file_info.filePath,
                "uploadedAt": uploaded_at,
                "fileHash": file_info.fileHash,
                "renders": [original_render]  # S5-006: Include original render
            }

            documents_list.append(document_entry)
            added.append(file_info.filePath)
            logger.info(f"Added orphaned file to manifest: {file_info.filePath}")

    # Find missing files (in manifest but not on disk)
    for doc in registry.documents:
        key = (doc.get('caseId'), doc.get('folderId'), doc.get('fileName'))
        if key not in fs_files_set:
            missing.append(doc.get('filePath', 'unknown'))
            logger.warning(f"Missing file (in manifest but not on disk): {doc.get('filePath')}")

    # Verify file hashes for files that exist in both
    for doc in registry.documents:
        key = (doc.get('caseId'), doc.get('folderId'), doc.get('fileName'))
        if key in fs_files_set:
            fs_file = fs_files_set[key]
            manifest_hash = doc.get('fileHash', '')
            if manifest_hash and fs_file.fileHash != manifest_hash:
                integrity_failed.append(doc.get('filePath', 'unknown'))
                logger.warning(
                    f"File integrity check failed for {doc.get('filePath')}: "
                    f"manifest={manifest_hash}, disk={fs_file.fileHash}"
                )

    # Save updated manifest if changes were made
    if added:
        updated_registry = DocumentRegistry(
            version=registry.version,
            schemaVersion=registry.schemaVersion,
            lastUpdated=datetime.now(timezone.utc).isoformat(),
            documents=documents_list
        )
        save_manifest(updated_registry)

    return ReconcileReport(
        added=added,
        missing=missing,
        integrity_failed=integrity_failed
    )


# ============================================================================
# Part 6: Document Tree Builder
# ============================================================================

def get_all_documents() -> List[Dict]:
    """
    Get all documents from the manifest.

    Returns:
        List[dict]: List of all document entries.
    """
    registry = load_manifest()
    return registry.documents


def get_documents_by_case(case_id: str) -> List[Dict]:
    """
    Get all documents for a specific case.

    Args:
        case_id: The case ID to filter by.

    Returns:
        List[dict]: List of document entries for the case.
    """
    registry = load_manifest()
    return [
        doc for doc in registry.documents
        if doc.get('caseId') == case_id
    ]


def load_folder_config(case_id: str) -> Dict:
    """
    Load folder configuration for a case.

    Args:
        case_id: The case ID.

    Returns:
        dict: Folder configuration or empty config if not found.
    """
    config_path = Path("backend/data/contexts/cases") / case_id / "folder_config.json"

    if not config_path.exists():
        logger.debug(f"No folder config found for case {case_id}")
        return {"folders": []}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load folder config for {case_id}: {e}")
        return {"folders": []}


def build_document_tree(case_id: str, language: str = 'de') -> Dict:
    """
    Build a document tree for a specific case.

    Groups documents by folder and returns a structured tree that can be
    consumed by the frontend. Includes ALL configured folders, even empty ones,
    to ensure folder persistence.

    Args:
        case_id: The case ID to build the tree for.
        language: Language code for folder names ('de' or 'en'). Defaults to 'de'.

    Returns:
        dict: Document tree with folders and documents.
            Format: {
                "folders": [
                    {
                        "id": "folder-id",
                        "name": "Folder Name",
                        "nameKey": "folder-id",
                        "localizedName": {"de": "...", "en": "..."},
                        "documents": [...],
                        "subfolders": [],
                        "mandatory": true/false,
                        "order": 1
                    }
                ],
                "rootDocuments": [...]  # Documents not in any folder
            }

    Example:
        >>> tree = build_document_tree("ACTE-2024-001", "de")
        >>> print(f"Found {len(tree['folders'])} folders")
    """
    documents = get_documents_by_case(case_id)

    # Load folder configuration
    folder_config = load_folder_config(case_id)
    configured_folders = {f["id"]: f for f in folder_config.get("folders", [])}

    # Group documents by folder
    folders_dict: Dict[str, List[Dict]] = {}
    root_documents = []

    for doc in documents:
        folder_id = doc.get('folderId')
        if folder_id:
            if folder_id not in folders_dict:
                folders_dict[folder_id] = []
            folders_dict[folder_id].append(doc)
        else:
            root_documents.append(doc)

    # Build folder structures from configuration (includes empty folders)
    folders = []

    # First, add all configured folders in order
    sorted_config_folders = sorted(
        configured_folders.values(),
        key=lambda f: f.get("order", 999)
    )

    for config_folder in sorted_config_folders:
        folder_id = config_folder["id"]
        folder_docs = folders_dict.pop(folder_id, [])

        # Get localized name
        name_config = config_folder.get("name", {})
        if isinstance(name_config, dict):
            folder_name = name_config.get(language, name_config.get("en", folder_id))
            localized_name = name_config
        else:
            folder_name = name_config
            localized_name = {"de": name_config, "en": name_config}

        folders.append({
            "id": folder_id,
            "name": folder_name,
            "nameKey": config_folder.get("nameKey", folder_id),
            "localizedName": localized_name,
            "documents": folder_docs,
            "subfolders": [],
            "isExpanded": True,
            "mandatory": config_folder.get("mandatory", False),
            "order": config_folder.get("order", 999)
        })

    # Add any remaining folders not in config (orphaned folders with documents)
    for folder_id, folder_docs in folders_dict.items():
        folder_name = folder_id.replace('-', ' ').replace('_', ' ').title()

        folders.append({
            "id": folder_id,
            "name": folder_name,
            "nameKey": folder_id,
            "localizedName": {"de": folder_name, "en": folder_name},
            "documents": folder_docs,
            "subfolders": [],
            "isExpanded": True,
            "mandatory": False,
            "order": 999
        })

    return {
        "folders": folders,
        "rootDocuments": root_documents
    }


# ============================================================================
# Part 7: Helper Functions
# ============================================================================

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        str: SHA-256 hash in format "sha256:hexdigest".

    Raises:
        OSError: If file cannot be read.
    """
    try:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return f"sha256:{sha256_hash.hexdigest()}"

    except OSError as e:
        logger.error(f"Failed to calculate hash for {file_path}: {e}")
        raise


def verify_file_integrity(document_entry: Dict) -> bool:
    """
    Verify that a document's file hash matches the stored hash.

    Args:
        document_entry: The document entry from the manifest.

    Returns:
        bool: True if hash matches or file doesn't exist, False if mismatch.
    """
    try:
        file_path = document_entry.get('filePath')
        stored_hash = document_entry.get('fileHash')

        if not file_path or not stored_hash:
            return True  # No hash to verify

        if not Path(file_path).exists():
            return True  # File doesn't exist, can't verify

        actual_hash = calculate_file_hash(file_path)
        return actual_hash == stored_hash

    except Exception as e:
        logger.error(f"Failed to verify file integrity: {e}")
        return False


def generate_document_id() -> str:
    """
    Generate a unique document ID.

    Returns:
        str: A unique document ID (e.g., "doc_abc123...").
    """
    # Use UUID4 for guaranteed uniqueness
    return f"doc_{uuid.uuid4().hex[:12]}"


# ============================================================================
# S5-006: Document Render Management Functions
# ============================================================================

def add_render_to_document(document_id: str, render_data: Dict) -> None:
    """
    Add a render (anonymized, translated, etc.) to a document in the registry.

    This function updates the document manifest to include the new render.

    Args:
        document_id: The ID of the parent document
        render_data: Dictionary containing render metadata
                    {id, type, name, filePath, createdAt, metadata}

    Raises:
        ValueError: If document not found in registry

    Example:
        >>> render = {
        ...     'id': 'render_abc123',
        ...     'type': 'anonymized',
        ...     'name': 'document_anonymized.png',
        ...     'filePath': 'public/documents/ACTE-2024-001/uploads/document_anonymized.png',
        ...     'createdAt': '2026-01-12T20:00:00Z',
        ...     'metadata': {}
        ... }
        >>> add_render_to_document('doc_001', render)
    """
    registry = load_manifest()

    # Find the document
    document_found = False
    case_id = None
    for doc_entry in registry.documents:
        if doc_entry.get('documentId') == document_id:
            document_found = True
            case_id = doc_entry.get('caseId')

            # Ensure renders array exists
            if 'renders' not in doc_entry:
                doc_entry['renders'] = []

            # Add the new render
            doc_entry['renders'].append(render_data)

            logger.info(f"Added render {render_data['id']} to document {document_id}")
            break

    if not document_found:
        raise ValueError(f"Document {document_id} not found in registry")

    # Save updated manifest
    save_manifest(registry)

    # Invalidate tree cache so AI context includes new renders
    if case_id:
        # Import here to avoid circular imports
        from backend.services.context_manager import invalidate_tree_cache
        invalidate_tree_cache(case_id)
        logger.info(f"Invalidated tree cache for case {case_id} after adding render")


def get_document_renders(document_id: str) -> List[Dict]:
    """
    Get all renders for a specific document.

    Args:
        document_id: The ID of the document

    Returns:
        List[Dict]: List of render dictionaries, or empty list if no renders

    Example:
        >>> renders = get_document_renders('doc_001')
        >>> len(renders)
        2
        >>> renders[0]['type']
        'anonymized'
    """
    registry = load_manifest()

    # Find the document
    for doc_entry in registry.documents:
        if doc_entry.get('documentId') == document_id:
            return doc_entry.get('renders', [])

    logger.warning(f"Document {document_id} not found in registry")
    return []


def remove_render_from_document(document_id: str, render_id: str) -> bool:
    """
    Remove a specific render from a document.

    Args:
        document_id: The ID of the parent document
        render_id: The ID of the render to remove

    Returns:
        bool: True if render was removed, False if not found

    Example:
        >>> remove_render_from_document('doc_001', 'render_abc123')
        True
    """
    registry = load_manifest()

    # Find the document
    for doc_entry in registry.documents:
        if doc_entry.get('documentId') == document_id:
            renders = doc_entry.get('renders', [])

            # Find and remove the render
            initial_length = len(renders)
            doc_entry['renders'] = [r for r in renders if r.get('id') != render_id]

            if len(doc_entry['renders']) < initial_length:
                # Render was removed
                save_manifest(registry)
                logger.info(f"Removed render {render_id} from document {document_id}")
                return True
            else:
                logger.warning(f"Render {render_id} not found in document {document_id}")
                return False

    logger.warning(f"Document {document_id} not found in registry")
    return False
