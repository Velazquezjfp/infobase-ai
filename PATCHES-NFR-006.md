# NFR-006 path-fix patches — manual application guide

> Use this if the GitHub tarball is delivering stale content. Each section is a
> single file with the exact "find this" / "replace with this" snippets. Copy the
> file path on your local checkout, apply each change, save, and on the remote VM
> rebuild the backend image once at the end.
>
> **Total surface:** ~18 line swaps + 6 import additions + 1 helper function + 1 dict entry across 10 files.
>
> **Editor approach:** for each block, use Find/Replace (Ctrl-H or `:s` in vim).
> Lines with `+` are additions, lines with `-` are removals/replacements. Don't
> include the leading `+ ` or `- ` characters in your editor — they're just
> markers for the diff view here.

---

## 1. `backend/config.py` — add the helper (1 import + ~30 line addition)

### A. Add import near the top (line 8 area, with other imports)

Find:
```python
import os
from typing import Optional
```

Replace with:
```python
import os
from pathlib import Path
from typing import Optional
```

### B. Add the helper at the end of the file (or after `DOCUMENTS_BASE_PATH`)

Find:
```python
DOCUMENTS_BASE_PATH: str = get_documents_path()
```

Replace with:
```python
DOCUMENTS_BASE_PATH: str = get_documents_path()


# ----------------------------------------------------------------------------
# S001-NFR-006: legacy `public/documents/` path translation
# ----------------------------------------------------------------------------
LEGACY_DOCUMENTS_PREFIX = "public/documents/"


def resolve_document_path(path: str) -> Path:
    """
    Translate legacy `public/documents/<rest>` → `${DOCUMENTS_BASE_PATH}/<rest>`.
    Pass-through for absolute paths and other relative paths.
    See `docs/requirements/sprint-001/S001-NFR-006.md` for full rationale.
    """
    if path.startswith(LEGACY_DOCUMENTS_PREFIX):
        relative = path[len(LEGACY_DOCUMENTS_PREFIX):]
        return Path(DOCUMENTS_BASE_PATH) / relative
    return Path(path)
```

---

## 2. `backend/services/pdf_service.py` — 1 import + 4 line swaps

### A. Add import after the existing imports

Find:
```python
import pdfplumber
```

Replace with:
```python
import pdfplumber

from backend.config import resolve_document_path  # S001-NFR-006
```

### B. Swap all four `path = Path(pdf_path)` (one per function)

There are **4 occurrences** in this file. Use Find/Replace ALL:

Find (exactly):
```python
        path = Path(pdf_path)
```

Replace (all 4):
```python
        path = resolve_document_path(pdf_path)  # S001-NFR-006
```

After replacement: 4 occurrences become 4 swaps.

---

## 3. `backend/services/email_service.py` — 1 import + 1 line swap

### A. Add import after existing imports

Find:
```python
import html2text
```

Replace with:
```python
import html2text

from backend.config import resolve_document_path  # S001-NFR-006
```

### B. Swap `path = Path(file_path)` in `parse_eml_file`

Find:
```python
        path = Path(file_path)
```

Replace:
```python
        path = resolve_document_path(file_path)  # S001-NFR-006
```

---

## 4. `backend/services/translation_service.py` — 1 import + 1 line swap

### A. Add import after existing imports

Find:
```python
from dataclasses import dataclass
```

Replace with:
```python
from dataclasses import dataclass

from backend.config import resolve_document_path  # S001-NFR-006
```

### B. Swap `path = Path(email_path)` in `translate_email`

Find:
```python
        path = Path(email_path)
```

Replace:
```python
        path = resolve_document_path(email_path)  # S001-NFR-006
```

---

## 5. `backend/services/document_registry.py` — 1 import + 1 block swap

### A. Add import after existing imports

Find:
```python
from typing import Dict, List, Optional, Tuple, NamedTuple
```

Replace with:
```python
from typing import Dict, List, Optional, Tuple, NamedTuple

from backend.config import resolve_document_path  # S001-NFR-006
```

### B. Swap the integrity-check block (in `_verify_file_integrity`)

Find:
```python
        if not Path(file_path).exists():
            return True  # File doesn't exist, can't verify

        actual_hash = calculate_file_hash(file_path)
```

Replace:
```python
        # S001-NFR-006: translate legacy `public/documents/<rest>` paths
        resolved = resolve_document_path(file_path)
        if not resolved.exists():
            return True  # File doesn't exist, can't verify

        actual_hash = calculate_file_hash(str(resolved))
```

---

## 6. `backend/services/file_service.py` — 1 import + 3 line swaps

### A. Extend the existing import (or add if not present)

Find:
```python
from backend.config import resolve_document_path  # S001-NFR-006
```

(If this import isn't present yet, find `logger = logging.getLogger(__name__)` and add the import line just above it.)

Replace with:
```python
from backend.config import resolve_document_path, DOCUMENTS_BASE_PATH  # S001-NFR-006
```

### B. Swap `file_path = Path(file_path)` in `save_uploaded_file`

Find:
```python
    file_path = Path(file_path)

    # Ensure parent directory exists
    create_folder_if_needed(file_path.parent)
```

Replace:
```python
    file_path = resolve_document_path(str(file_path))  # S001-NFR-006

    # Ensure parent directory exists
    create_folder_if_needed(file_path.parent)
```

### C. Swap `base_dir = Path("public") / "documents"` in `delete_file`

Find:
```python
    # Construct paths
    base_dir = Path("public") / "documents"
    expected_case_dir = base_dir / case_id
    file_path = base_dir / case_id / folder_id / safe_filename
```

Replace:
```python
    # Construct paths. S001-NFR-006: anchor on DOCUMENTS_BASE_PATH.
    base_dir = Path(DOCUMENTS_BASE_PATH)
    expected_case_dir = base_dir / case_id
    file_path = base_dir / case_id / folder_id / safe_filename
```

### D. Swap the same in `file_exists`

Find:
```python
    # Construct path
    file_path = Path("public") / "documents" / case_id / folder_id / safe_filename
```

Replace:
```python
    # Construct path. S001-NFR-006: anchor on DOCUMENTS_BASE_PATH.
    file_path = Path(DOCUMENTS_BASE_PATH) / case_id / folder_id / safe_filename
```

---

## 7. `backend/services/session_manager.py` — 1 dict entry

Find:
```python
ROOT_DOCS_MAPPING: Dict[str, str] = {
    "Aufenthalstitel.png": "personal-data",
    "Geburtsurkunde.jpg": "personal-data",
    "Personalausweis.png": "personal-data",
    "Sprachzeugnis-Zertifikat.pdf": "certificates",
    "Anmeldeformular.pdf": "applications",
    "Notenspiegel.pdf": "evidence",
}
```

Replace:
```python
# S001-NFR-006 polish: added Email.eml → emails for translation/parse-email demo.
ROOT_DOCS_MAPPING: Dict[str, str] = {
    "Aufenthalstitel.png": "personal-data",
    "Geburtsurkunde.jpg": "personal-data",
    "Personalausweis.png": "personal-data",
    "Sprachzeugnis-Zertifikat.pdf": "certificates",
    "Anmeldeformular.pdf": "applications",
    "Notenspiegel.pdf": "evidence",
    "Email.eml": "emails",
}
```

(Optional: in the same file, find `the six ROOT_DOCS_MAPPING files` in the docstring of `reset_case_to_seed` and change `six` → `seven` for accuracy.)

---

## 8. `backend/api/documents.py` — inline import + 1 line swap

### Single block swap (in `_transform_doc`, file size lookup)

Find:
```python
    from pathlib import Path

    file_name = registry_doc.get('fileName', 'unknown')
    file_path = registry_doc.get('filePath', '')

    # Extract file extension
    file_ext = Path(file_name).suffix.lstrip('.').lower() or 'unknown'

    # Calculate file size if file exists
    file_size = "0 KB"
    if file_path:
        try:
            path = Path(file_path)
            if path.exists():
```

Replace:
```python
    from pathlib import Path
    from backend.config import resolve_document_path  # S001-NFR-006

    file_name = registry_doc.get('fileName', 'unknown')
    file_path = registry_doc.get('filePath', '')

    # Extract file extension
    file_ext = Path(file_name).suffix.lstrip('.').lower() or 'unknown'

    # Calculate file size if file exists
    file_size = "0 KB"
    if file_path:
        try:
            path = resolve_document_path(file_path)  # S001-NFR-006
            if path.exists():
```

---

## 9. `backend/api/files.py` — 2 line swaps (no new imports needed)

This file already has `from backend import config` — we just use `config.DOCUMENTS_BASE_PATH`.

### A. Swap `target_dir` in the upload endpoint

Find:
```python
        # Construct target path
        target_dir = Path("public") / "documents" / case_id / folder_id
        target_path = target_dir / safe_filename
```

Replace:
```python
        # Construct target path. S001-NFR-006: anchor on DOCUMENTS_BASE_PATH.
        target_dir = Path(config.DOCUMENTS_BASE_PATH) / case_id / folder_id
        target_path = target_dir / safe_filename
```

### B. Swap `docs_dir` in the health endpoint

Find:
```python
    # Check if public/documents directory exists
    docs_dir = Path("public") / "documents"
    storage_available = docs_dir.exists() and docs_dir.is_dir()
```

Replace:
```python
    # S001-NFR-006: anchor on DOCUMENTS_BASE_PATH.
    docs_dir = Path(config.DOCUMENTS_BASE_PATH)
    storage_available = docs_dir.exists() and docs_dir.is_dir()
```

---

## 10. `backend/api/folders.py` — 1 import + 1 line swap (the folders fix)

### A. Add the config import

Find:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
```

Replace:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend import config  # S001-NFR-006: DOCUMENTS_BASE_PATH
```

### B. Swap `DOCUMENTS_DIR`

Find:
```python
DOCUMENTS_DIR = Path(__file__).parent.parent.parent / "public" / "documents"
```

Replace:
```python
# S001-NFR-006: was Path(__file__).parent.parent.parent / "public" / "documents"
# which inside the container resolved to /app/public/documents → PermissionError.
# Anchor on DOCUMENTS_BASE_PATH (= /var/app/documents in container).
DOCUMENTS_DIR = Path(config.DOCUMENTS_BASE_PATH)
```

---

## After all edits — rebuild + restart on the VM

```bash
cd /path/to/bamf-acte-companion

# Sanity check (each command should print ≥ 1):
grep -c "def resolve_document_path" backend/config.py
grep -c "S001-NFR-006" backend/api/folders.py
grep -c "Email.eml" backend/services/session_manager.py
grep -c "config.DOCUMENTS_BASE_PATH" backend/api/files.py

# If all ≥ 1, rebuild backend and restart:
docker compose build backend
docker compose up -d backend

# Wait for healthy:
until docker compose ps --format json 2>/dev/null | grep '"Service":"backend"' | grep -q '"Health":"healthy"'; do sleep 2; done
echo "✓ backend healthy"

# Confirm path errors are gone:
docker compose logs --tail=200 backend 2>&1 | grep -E "PermissionError|/app/public" \
  || echo "✓ no path errors"
```

If `grep -c` for any of the four sanity checks prints `0`, that file's edit didn't take. Re-open it, redo the corresponding section above.

## What this resolves

| Symptom in your VM | Fixed by |
|---|---|
| Folders not visible in admin/user panes | §10 (folders.py) |
| `PermissionError: '/app/public'` in backend logs | §10 + §6.C/D + §9 |
| Add-field admin form doesn't load | §10 (depends on folders endpoint working) |
| `0 KB` file sizes in document tree | §8 (documents.py) |
| Translate / parse-email failures | §3, §4 |
| `extract-pdf-text` returns 404 | §1 (helper) + §2 (pdf_service) |
| Email file missing in `Emails` folder | §7 (session_manager — adds Email.eml seed) |

## What this does NOT cover

- `backend/Dockerfile` and `docker-compose.yml` — your closed-environment edits (`PIP_TRUSTED_HOST`, no-apt, python healthcheck) live there. Don't replace from this guide; keep what you have.
- `frontend/Dockerfile` — has `node:20-alpine` + `strict-ssl false` + verbose npm install. Keep yours.
- `.env` and `litellm/.env` — local secrets/config; never overwrite.
