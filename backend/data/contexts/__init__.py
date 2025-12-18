"""
Contexts - Hierarchical AI Context Data (Case-Instance Scoped).

This package contains JSON files that provide domain-specific context
to AI agents for generating relevant, accurate responses. Each case (ACTE)
has its own isolated context directory ensuring complete modularity.

Context Hierarchy:
    1. Case-level: cases/{caseId}/case.json - regulations, required documents
    2. Folder-level: cases/{caseId}/folders/{folderId}.json - validation criteria
    3. Document-level: Selected document content (passed at runtime from frontend)

Directory Structure:
    contexts/
    ├── cases/                      # Case-instance specific contexts
    │   ├── ACTE-2024-001/          # German Integration Course case
    │   │   ├── case.json           # Case-level context
    │   │   └── folders/
    │   │       ├── personal-data.json
    │   │       ├── certificates.json
    │   │       └── ...
    │   ├── ACTE-2024-002/          # Asylum Application case
    │   └── ACTE-2024-003/          # Family Reunification case
    └── templates/                   # Templates for new case creation
        ├── integration_course/
        ├── asylum_application/
        └── family_reunification/

Context Loading:
    Context files are loaded by the context_manager service (F-002).
    - load_case_context(case_id) → loads cases/{case_id}/case.json
    - load_folder_context(case_id, folder_id) → loads cases/{case_id}/folders/{folder_id}.json
    - create_case_from_template(case_id, case_type) → copies template to new case

When switching cases, context switches completely - ensuring AI responses
are always scoped to the active case.

Schema Version: 1.0
"""

__all__: list[str] = []
