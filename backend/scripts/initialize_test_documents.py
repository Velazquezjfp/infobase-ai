"""
Initialize Test Documents for ACTE-2024-001.

This script copies sample documents from the root_docs directory to the appropriate
folders within the ACTE-2024-001 case. It's designed to be idempotent (safe to run
multiple times) and integrates with the document registry system.

The script copies 7 sample documents:
    - Geburtsurkunde.jpg → Personal Data folder
    - Email.eml → Emails folder
    - Sprachzeugnis-Zertifikat.pdf → Certificates folder
    - Anmeldeformular.pdf → Applications & Forms folder
    - Personalausweis.png → Personal Data folder
    - Aufenthalstitel.png → Personal Data folder
    - Notenspiegel.pdf → Additional Evidence folder

Related Requirements:
    - S5-015: Initial Document Setup for Test Acte
    - S5-007: Container-Compatible File Persistence

Note: The document registry reconciliation system will automatically register
these files in the manifest on startup, so no explicit registration is needed.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

# Document mapping configuration
# Maps source filenames to their target folder and metadata
DOCUMENT_MAPPING: Dict[str, Dict[str, str]] = {
    "Geburtsurkunde.jpg": {
        "target_folder": "personal-data",
        "name": "Birth Certificate (Geburtsurkunde)",
        "type": "jpg"
    },
    "Email.eml": {
        "target_folder": "emails",
        "name": "BAMF Confirmation Email",
        "type": "eml"
    },
    "Sprachzeugnis-Zertifikat.pdf": {
        "target_folder": "certificates",
        "name": "German Language Certificate A2",
        "type": "pdf"
    },
    "Anmeldeformular.pdf": {
        "target_folder": "applications",
        "name": "Integration Course Application Form",
        "type": "pdf"
    },
    "Personalausweis.png": {
        "target_folder": "personal-data",
        "name": "ID Card (Personalausweis)",
        "type": "png"
    },
    "Aufenthalstitel.png": {
        "target_folder": "personal-data",
        "name": "Residence Permit (Aufenthaltstitel)",
        "type": "png"
    },
    "Notenspiegel.pdf": {
        "target_folder": "evidence",
        "name": "University Transcript (Notenspiegel)",
        "type": "pdf"
    }
}


def initialize_test_documents() -> Dict[str, int]:
    """
    Initialize test documents for ACTE-2024-001 case.

    Copies sample documents from root_docs/ to the appropriate case folders.
    The function is idempotent - it only copies files that don't already exist
    at the destination.

    The document registry reconciliation system (S5-007) will automatically
    detect and register these files in the manifest on startup.

    Returns:
        dict: Statistics about the initialization process.
            {
                "copied": int,      # Number of files successfully copied
                "skipped": int,     # Number of files skipped (already exist)
                "failed": int       # Number of files that failed to copy
            }

    Example:
        >>> stats = initialize_test_documents()
        >>> print(f"Copied {stats['copied']} files, skipped {stats['skipped']}")
    """
    # Initialize statistics
    stats = {
        "copied": 0,
        "skipped": 0,
        "failed": 0
    }

    # Define paths
    source_dir = Path("root_docs")
    base_target_dir = Path("public/documents/ACTE-2024-001")

    # Validate source directory exists
    if not source_dir.exists():
        logger.warning(f"Source directory not found: {source_dir}")
        logger.warning("Skipping test document initialization - root_docs directory is missing")
        return stats

    logger.info("Starting test document initialization for ACTE-2024-001...")

    # Process each document in the mapping
    for filename, config in DOCUMENT_MAPPING.items():
        try:
            # Construct source and target paths
            source_file = source_dir / filename
            target_folder = base_target_dir / config["target_folder"]
            target_file = target_folder / filename

            # Check if source file exists
            if not source_file.exists():
                logger.warning(f"Source file not found: {source_file}")
                stats["failed"] += 1
                continue

            # Skip if target file already exists (idempotent behavior)
            if target_file.exists():
                logger.debug(f"File already exists, skipping: {target_file}")
                stats["skipped"] += 1
                continue

            # Create target folder if it doesn't exist
            target_folder.mkdir(parents=True, exist_ok=True)

            # Copy file (copy2 preserves metadata like timestamps)
            shutil.copy2(source_file, target_file)

            logger.info(
                f"✓ Copied {filename} → {config['target_folder']}/ "
                f"({source_file.stat().st_size} bytes)"
            )
            stats["copied"] += 1

        except Exception as e:
            logger.error(f"Failed to copy {filename}: {e}", exc_info=True)
            stats["failed"] += 1

    # Log summary
    logger.info(
        f"Test document initialization complete: "
        f"{stats['copied']} copied, "
        f"{stats['skipped']} skipped, "
        f"{stats['failed']} failed"
    )

    if stats["copied"] > 0:
        logger.info(
            "New documents will be registered in the manifest automatically "
            "by the document registry reconciliation system."
        )

    return stats


def cleanup_old_test_documents() -> int:
    """
    Remove old irrelevant test documents (.txt files) from ACTE-2024-001.

    This removes the placeholder .txt files that were used for testing
    before the realistic sample documents were created. Also unregisters
    them from the document manifest.

    Returns:
        int: Number of files deleted.
    """
    base_dir = Path("public/documents/ACTE-2024-001")
    deleted_count = 0

    # Files to remove (old .txt placeholders) - with case_id, folder_id, filename
    old_files = [
        ("ACTE-2024-001", "personal-data", "Passport_Scan.txt"),
        ("ACTE-2024-001", "certificates", "Language_Certificate_A1.txt"),
        ("ACTE-2024-001", "applications", "Integration_Application.txt"),
        ("ACTE-2024-001", "evidence", "School_Transcripts.txt"),
        ("ACTE-2024-001", "emails", "Confirmation_Email.txt")
    ]

    logger.info("Cleaning up old test documents (.txt files)...")

    for case_id, folder_id, filename in old_files:
        try:
            # Delete physical file
            file_path = base_dir / folder_id / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted old test file: {file_path}")
                deleted_count += 1

            # Unregister from manifest
            try:
                from backend.services.document_registry import find_document_by_path, unregister_document

                doc_entry = find_document_by_path(case_id, folder_id, filename)
                if doc_entry:
                    document_id = doc_entry.get('documentId')
                    if document_id:
                        unregister_document(document_id)
                        logger.info(f"Unregistered {filename} from manifest")
            except Exception as e:
                # Log but don't fail - file was already deleted
                logger.debug(f"Could not unregister {filename} from manifest: {e}")

        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}", exc_info=True)

    logger.info(f"Cleanup complete: {deleted_count} old files removed")
    return deleted_count


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run initialization
    print("=" * 60)
    print("Test Document Initialization Script")
    print("=" * 60)
    print()

    # Initialize new documents
    stats = initialize_test_documents()
    print()

    # Cleanup old documents
    deleted = cleanup_old_test_documents()
    print()

    # Print summary
    print("=" * 60)
    print("Summary:")
    print(f"  New documents copied: {stats['copied']}")
    print(f"  Files skipped (already exist): {stats['skipped']}")
    print(f"  Copy failures: {stats['failed']}")
    print(f"  Old documents deleted: {deleted}")
    print("=" * 60)

    if stats["copied"] > 0:
        print()
        print("✓ Test documents initialized successfully!")
        print("  The document registry will auto-register them on app startup.")
    elif stats["skipped"] == len(DOCUMENT_MAPPING):
        print()
        print("✓ All test documents already exist - no action needed.")
    else:
        print()
        print("⚠ Some documents could not be initialized. Check logs above.")
