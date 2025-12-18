"""
Data Layer - Configuration and Context Files.

This package contains data files and utilities for loading configuration
and context information. Data is stored as JSON files and loaded at runtime.

Subpackages:
    - contexts: Hierarchical context data for AI responses (D-001)
        - cases/: Case-instance specific context directories
        - templates/: Templates for creating new case contexts

Data Design Principles:
    - Case Isolation: Each case (ACTE) has its own context directory
    - JSON Format: All data stored as human-readable JSON
    - Schema Versioning: All files include schemaVersion field
    - Graceful Fallbacks: Missing files return empty context, not errors
    - UTF-8 Encoding: All files use UTF-8 for international character support

File Organization:
    data/
    └── contexts/
        ├── cases/              # Case-instance contexts
        │   ├── ACTE-2024-001/  # Each case has isolated context
        │   │   ├── case.json
        │   │   └── folders/
        │   └── ...
        └── templates/          # Templates for new case creation
            ├── integration_course/
            ├── asylum_application/
            └── family_reunification/
"""

__all__: list[str] = []
