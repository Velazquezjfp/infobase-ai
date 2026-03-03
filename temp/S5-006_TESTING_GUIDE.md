# S5-006 Testing Guide - Document Renders Management System

## Current Status: Implementation Complete, Testing Required

**Date:** 2026-01-12
**Requirement:** S5-006 - Document Renders Management System
**Status:** All code changes complete, needs end-to-end testing with Playwright MCP

---

## What Was Implemented

S5-006 replaces the document cloning system with a **document renders management system**. When a document is anonymized, translated, or modified, it creates different "renders" of the same parent document instead of separate files.

### Key Features:
- Documents with multiple renders appear as collapsible containers
- Show badge with render count (e.g., "2 renders")
- Expandable to see all versions (Original, Anonymized, Translated, etc.)
- Each render has an icon (EyeOff for anonymized, Globe for translated, etc.)
- Can delete non-original renders
- Persists in document manifest (S5-007 integration)

---

## Complete Implementation Summary

### Frontend Changes (4 files modified):

**1. src/types/case.ts**
- Added `RenderType` = 'original' | 'anonymized' | 'translated' | 'annotated'
- Added `DocumentRender` interface:
  ```typescript
  interface DocumentRender {
    id: string;
    type: RenderType;
    name: string;
    filePath: string;
    createdAt: string;
    metadata?: Record<string, any>;
  }
  ```
- Updated `Document` interface with optional `renders?: DocumentRender[]`

**2. src/contexts/AppContext.tsx**
- Added state: `selectedRender: string | null`
- Added function: `selectDocumentWithRender(doc: Document, renderId?: string)`
- **Line 440:** Added `renders: doc.renders || []` to `loadDocumentsFromBackend()` mapping
- **Lines 584-627:** Updated `anonymization_complete` WebSocket handler to:
  - Check for `renderMetadata` in response
  - Add render to document's `renders` array
  - Refresh from backend after anonymization (line 625)
  - Fallback to old behavior if no renderMetadata

**3. src/components/workspace/CaseTreeExplorer.tsx**
- **Lines 40-70:** Added helper functions:
  - `getRenderIcon(renderType)` - Maps render types to Lucide icons
  - `getRenderDisplayName(render, t)` - Gets i18n display names
- **Lines 72-158:** Added `RenderContainer` component:
  - Only shows if `document.renders.length > 1`
  - Displays expandable container with chevron
  - Shows badge with render count
  - Lists all renders with icons
  - Delete button on hover (except 'original')
  - Calls `selectDocumentWithRender()` on click
- **Lines 307-323:** Modified document mapping in FolderItem:
  - Check if `hasMultipleRenders`
  - Use `RenderContainer` if multiple renders
  - Otherwise use normal document display
- **Lines 240-267:** Added `handleDeleteRender()` function

**4. src/types/websocket.ts**
- **Line 100:** Added `documentId?: string` to `AnonymizationRequest`
- **Lines 114-115:** Added to `AnonymizationResponse`:
  - `renderMetadata?: any`
  - `documentId?: string`

**5. src/components/workspace/DocumentViewer.tsx**
- **Line 108:** Fixed file path to use `selectedDocument.folderId` instead of `selectedDocument.id`
- **Line 119:** Added `documentId: selectedDocument.id` to anonymization request

### Backend Changes (3 files modified):

**1. backend/services/document_registry.py**
- **Lines 717-764:** Added `add_render_to_document(document_id, render_data)`
  - Loads manifest
  - Finds document by documentId
  - Adds render to document's renders array
  - Saves manifest
- **Lines 767-792:** Added `get_document_renders(document_id)`
  - Returns list of renders for a document
- **Lines 795-831:** Added `remove_render_from_document(document_id, render_id)`
  - Prevents deletion of 'original' type
  - Deletes render file from filesystem
  - Removes render from manifest

**2. backend/services/file_service.py**
- **Lines 512-548:** Added `add_document_render()` wrapper function
  - Creates render metadata with unique ID
  - Calls `document_registry.add_render_to_document()`
  - Returns render data dict
- **Lines 569-580:** Added `get_document_renders()` wrapper
- **Lines 619-655:** Added `delete_document_render()` wrapper
  - Security: Prevents deletion of 'original'
  - Deletes file then removes from registry

**3. backend/tools/anonymization_tool.py**
- **Line 54:** Added `render_metadata: Optional[dict] = None` to result dataclass
- **Lines 160-162:** Added optional parameters:
  - `document_id: str = None`
  - `register_render: bool = False`
- **Lines 245-258:** Added render registration logic:
  - If `register_render and document_id`: call `add_document_render()`
  - Include `render_metadata` in result
  - Non-blocking: continues if render registration fails

**4. backend/api/chat.py**
- **Line 461:** Extract `document_id` from WebSocket message
- **Lines 493-497:** Call anonymization with render registration:
  ```python
  result = await anonymize_document(
      file_path,
      document_id=document_id,
      register_render=bool(document_id)
  )
  ```
- **Lines 508-509:** Include in WebSocket response:
  - `renderMetadata: result.render_metadata`
  - `documentId: document_id`

**5. backend/api/documents.py**
- **Line 43:** Added `renders: List[Dict]` field to `DocumentResponse` Pydantic model
- **Line 314:** Include renders in `_transform_document()`:
  ```python
  renders=registry_doc.get('renders', [])
  ```

---

## Critical Data Flow (Now Complete)

```
USER ACTION: Click "Anonymize" button
    ↓
FRONTEND: DocumentViewer.tsx (line 114-120)
    → Sends WebSocket message:
      {
        type: 'anonymize',
        filePath: 'public/documents/{caseId}/{folderId}/{filename}',
        documentId: selectedDocument.id,
        caseId: currentCase.id,
        folderId: selectedDocument.folderId
      }
    ↓
BACKEND: chat.py handle_anonymization() (lines 461, 493-497)
    → Extracts documentId from message
    → Calls: anonymize_document(file_path, document_id, register_render=True)
    ↓
BACKEND: anonymization_tool.py (lines 245-258)
    → Anonymizes image (calls anonymization service)
    → Saves anonymized file with '_anonymized' suffix
    → Calls: add_document_render(document_id, 'anonymized', file_path)
    ↓
BACKEND: file_service.py add_document_render() (lines 512-548)
    → Creates render metadata dict with:
      - id: 'render_{uuid}'
      - type: 'anonymized'
      - name: filename
      - filePath: path to anonymized file
      - createdAt: timestamp
    → Calls: document_registry.add_render_to_document(document_id, render_data)
    ↓
BACKEND: document_registry.py (lines 717-764)
    → Loads manifest from backend/data/document_manifest.json
    → Finds document entry with matching documentId
    → Appends render_data to document's renders array
    → Saves manifest back to disk
    ↓
BACKEND: chat.py (lines 500-510)
    → Sends WebSocket response:
      {
        type: 'anonymization_complete',
        success: true,
        renderMetadata: { id, type, name, filePath, createdAt },
        documentId: document_id,
        detectionsCount: 32
      }
    ↓
FRONTEND: AppContext.tsx anonymization_complete handler (lines 584-627)
    → Checks if renderMetadata present
    → If yes (NEW BEHAVIOR):
      - Updates currentCase state, adding render to document's renders array
      - Updates selectedDocument state with new render
      - Shows toast: "Anonymized render created"
      - Calls loadDocumentsFromBackend() after 500ms (line 625)
    ↓
FRONTEND: AppContext.tsx loadDocumentsFromBackend() (line 411-455)
    → Fetches: GET http://localhost:8000/api/documents/tree/{caseId}
    ↓
BACKEND: documents.py get_document_tree() (lines 90-151)
    → Calls: build_document_tree(case_id) from document_registry
    → Transforms documents using _transform_document()
    → Returns: { folders: [...], rootDocuments: [...] }
    ↓
BACKEND: documents.py _transform_document() (lines 266-315)
    → Line 314: includes renders=registry_doc.get('renders', [])
    ↓
FRONTEND: AppContext.tsx (line 440)
    → Maps documents, including: renders: doc.renders || []
    → Updates currentCase.folders with backend data
    ↓
UI: CaseTreeExplorer.tsx (lines 307-323)
    → Maps over folder.documents
    → Checks: hasMultipleRenders = doc.renders && doc.renders.length > 1
    → If true: Renders <RenderContainer /> component
    ↓
UI: RenderContainer component (lines 81-157)
    → Shows expandable container with chevron
    → Badge: "{renders.length} renders"
    → When expanded: Shows list of all renders
    → Each render has icon (getRenderIcon) and name (getRenderDisplayName)
    → Click render: calls selectDocumentWithRender(document, render.id)
    → Delete icon on hover (except 'original')
```

---

## Test Procedure with Playwright MCP

### Prerequisites:
1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:8080`
3. MCP Playwright enabled
4. Document manifest exists: `backend/data/document_manifest.json`
5. Test case: ACTE-2024-001 with personal-data folder

### Playwright Test Steps:

```javascript
// 1. Navigate to app
await page.goto('http://localhost:8080');

// 2. Wait for app to load
await page.waitForSelector('[data-testid="fall-explorer"]', { timeout: 5000 });

// 3. Expand "Persönliche Daten" (Personal Data) folder
const personalDataFolder = page.locator('text=Persönliche Daten').or(page.locator('text=Personal Data'));
await personalDataFolder.click();

// 4. Click on "Personalausweis.png" document
const personalausweisDoc = page.locator('text=Personalausweis.png');
await personalausweisDoc.click();

// 5. Wait for document to load in viewer
await page.waitForSelector('[data-testid="document-viewer"]', { timeout: 3000 });

// 6. Click the "Anonymize" button
const anonymizeButton = page.locator('button:has-text("Anonymize")');
await anonymizeButton.click();

// 7. Wait for anonymization to complete (toast notification)
await page.waitForSelector('text=Anonymization Complete', { timeout: 15000 });

// 8. Wait for document tree to refresh
await page.waitForTimeout(1000);

// 9. Verify render container appears
const renderContainer = page.locator('[class*="animate-fade-in"]').filter({ hasText: 'Personalausweis.png' });
await expect(renderContainer).toBeVisible();

// 10. Verify badge shows "2 renders"
const renderBadge = renderContainer.locator('text=/2 renders/i');
await expect(renderBadge).toBeVisible();

// 11. Click chevron to expand renders
const chevron = renderContainer.locator('[class*="ChevronRight"]').first();
await chevron.click();

// 12. Verify "Original" render is visible
const originalRender = page.locator('text=Original');
await expect(originalRender).toBeVisible();

// 13. Verify "Anonymized" render is visible
const anonymizedRender = page.locator('text=Anonymized');
await expect(anonymizedRender).toBeVisible();

// 14. Verify no duplicate "Personalausweis_anonymized.png" file created
const duplicateFile = page.locator('text=Personalausweis_anonymized.png');
await expect(duplicateFile).not.toBeVisible();

// 15. Click on "Anonymized" render to view it
await anonymizedRender.click();

// 16. Verify image displays anonymized version
const documentImage = page.locator('[data-testid="document-viewer"] img');
await expect(documentImage).toHaveAttribute('src', /anonymized/i);
```

### Expected Results:

✅ **Before Anonymization:**
- Single file: "Personalausweis.png"
- Normal file icon (no chevron)
- No badge

✅ **After Anonymization:**
- Expandable container with chevron icon
- Badge showing "2 renders"
- When expanded:
  - "Original" with FileText icon
  - "Anonymized" with EyeOff icon
- Delete icon on hover (only on "Anonymized")
- NO separate "Personalausweis_anonymized.png" file

❌ **What NOT to See:**
- Duplicate document files (e.g., "Personalausweis_anonymized.png")
- Document cloning behavior
- Multiple separate files in the tree

---

## Key Files to Reference

### Document Manifest:
```bash
backend/data/document_manifest.json
```

Should contain entries like:
```json
{
  "documentId": "doc_abc123",
  "fileName": "Personalausweis.png",
  "filePath": "public/documents/ACTE-2024-001/personal-data/Personalausweis.png",
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data",
  "uploadedAt": "2026-01-12T20:00:00Z",
  "renders": [
    {
      "id": "render_xyz789",
      "type": "anonymized",
      "name": "Personalausweis_anonymized.png",
      "filePath": "public/documents/ACTE-2024-001/personal-data/Personalausweis_anonymized.png",
      "createdAt": "2026-01-12T20:05:00Z",
      "metadata": {}
    }
  ]
}
```

### API Endpoints to Verify:
```bash
# 1. Get document tree (should include renders array)
GET http://localhost:8000/api/documents/tree/ACTE-2024-001

# Response should have renders in documents:
{
  "folders": [{
    "id": "personal-data",
    "documents": [{
      "id": "doc_abc123",
      "name": "Personalausweis.png",
      "renders": [
        {"id": "render_xyz", "type": "anonymized", ...}
      ]
    }]
  }]
}

# 2. Check document service health
GET http://localhost:8000/api/documents/health

# 3. WebSocket endpoint (for anonymization)
WS ws://localhost:8000/api/chat/ws/{case_id}
```

---

## Debugging Commands

### Check manifest content:
```bash
cat backend/data/document_manifest.json | jq '.documents[] | select(.fileName == "Personalausweis.png")'
```

### Check if anonymized file exists:
```bash
ls -la public/documents/ACTE-2024-001/personal-data/Personalausweis*
```

### Test API endpoint directly:
```bash
curl http://localhost:8000/api/documents/tree/ACTE-2024-001 | jq '.folders[].documents[] | select(.name == "Personalausweis.png")'
```

### Check backend logs:
```bash
# Look for these log messages:
# - "Added anonymized render to document doc_abc123: render_xyz789"
# - "Successfully retrieved document tree for ACTE-2024-001"
```

### Check browser console:
```javascript
// Should see:
// "Loading documents from backend for case: ACTE-2024-001"
// "Loaded document tree from backend: {...}"
// "Successfully loaded N folders from backend"
```

---

## Common Issues & Solutions

### Issue 1: Renders array not showing in frontend
**Check:** Browser DevTools → Network → document tree API response
**Fix:** Verify backend includes `renders` field in response (documents.py line 314)

### Issue 2: Render container not appearing
**Check:** Document has `renders` array with length > 1
**Fix:** Verify `loadDocumentsFromBackend()` maps renders field (AppContext.tsx line 440)

### Issue 3: Anonymization creates duplicate file
**Check:** WebSocket response includes `renderMetadata`
**Fix:** Verify `anonymize_document()` called with `register_render=True` (chat.py line 496)

### Issue 4: Renders not persisting after refresh
**Check:** Document manifest file contains renders
**Fix:** Verify `add_render_to_document()` saves manifest (document_registry.py line 764)

### Issue 5: Frontend doesn't refresh after anonymization
**Check:** `loadDocumentsFromBackend()` called after anonymization
**Fix:** Verify setTimeout callback at AppContext.tsx line 625

---

## Component Hierarchy for Testing

```
App
└── AppProvider (AppContext.tsx)
    └── Workspace
        ├── CaseTreeExplorer.tsx
        │   ├── FolderItem (Persönliche Daten)
        │   │   └── RenderContainer (if renders.length > 1)
        │   │       ├── Document header (Personalausweis.png)
        │   │       ├── Badge (2 renders)
        │   │       └── Render list (when expanded)
        │   │           ├── Original (FileText icon)
        │   │           └── Anonymized (EyeOff icon, delete button)
        │   └── Regular document (if renders.length <= 1)
        └── DocumentViewer.tsx
            └── Anonymize button
```

---

## Success Criteria

The implementation is successful if:

1. ✅ Anonymizing a document creates a render, not a duplicate file
2. ✅ Document appears as expandable container with badge
3. ✅ Expanding shows "Original" and "Anonymized" options
4. ✅ Each render has appropriate icon (FileText, EyeOff, etc.)
5. ✅ Clicking a render displays that version
6. ✅ Delete button appears on non-original renders
7. ✅ Renders persist after page refresh
8. ✅ No "Personalausweis_anonymized.png" separate file in tree
9. ✅ Backend API returns renders array
10. ✅ Manifest file contains renders in document entry

---

## Next Session Action Items

1. **Start Playwright MCP session**
2. **Navigate to:** `http://localhost:8080`
3. **Execute test procedure** (see "Playwright Test Steps" above)
4. **Verify:** Document transforms to render container after anonymization
5. **Check:** No duplicate files created
6. **Verify:** Renders persist after refresh
7. **Test:** Delete render functionality
8. **Document results** in test report

---

## Related Requirements

- **S5-007:** Container-Compatible File Persistence (DEPENDENCY - provides document manifest)
- **S5-004:** Translation Service (FUTURE - will use render system)
- **S4-001:** File Upload (Uses document registry)
- **S4-002:** File Deletion (Uses document registry)

---

## Contact Points in Code

If issues arise, check these critical integration points:

1. **Frontend → Backend (WebSocket):** `src/components/workspace/DocumentViewer.tsx:114-120`
2. **Backend WebSocket Handler:** `backend/api/chat.py:443-520`
3. **Anonymization Tool:** `backend/tools/anonymization_tool.py:159-266`
4. **Render Registration:** `backend/services/file_service.py:478-548`
5. **Manifest Update:** `backend/services/document_registry.py:717-764`
6. **API Response:** `backend/api/documents.py:266-315`
7. **Frontend Data Loading:** `src/contexts/AppContext.tsx:411-455`
8. **Frontend Render Display:** `src/components/workspace/CaseTreeExplorer.tsx:81-157`

---

**End of Testing Guide**
