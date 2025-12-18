# F-006 Manual Test Guide
## Document Loading System - UI Validation

**Requirement:** F-006 - Replace Mock Documents with Text Files (Case-Instance Scoped)
**Test Type:** Manual UI Testing
**Prerequisites:**
- Application running locally (npm run dev)
- ACTE-2024-001 case with sample documents in public/documents/
- Multiple test cases available (ACTE-2024-001, ACTE-2024-002, ACTE-2024-003)

---

## Test Case: TC-F-006-UI-01
### Document Loading with Async Feedback

**Objective:** Verify document loading displays loading spinner and success notification

**Steps:**
1. Log in to the application
2. Navigate to workspace
3. Ensure ACTE-2024-001 is the active case
4. Expand the "Personal Data" folder in the case tree
5. Click on "Birth_Certificate.txt"

**Expected Results:**
- [ ] Loading spinner appears immediately after click
- [ ] Toast notification displays "Document loaded successfully" (or similar)
- [ ] Document content appears in the DocumentViewer panel
- [ ] Document content is readable and properly formatted
- [ ] German umlauts (ä, ö, ü, ß) display correctly

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-02
### Case-Scoped Document Tree

**Objective:** Verify document tree shows only current case's documents

**Steps:**
1. Open workspace with ACTE-2024-001 active
2. Observe the document tree in the left sidebar
3. Note the folders and documents visible
4. Use case search dialog to switch to ACTE-2024-002
5. Observe the document tree after case switch

**Expected Results:**
- [ ] ACTE-2024-001 shows 6 folders (personal-data, certificates, integration-docs, applications, emails, evidence)
- [ ] ACTE-2024-001 documents are clearly listed under their folders
- [ ] After switching to ACTE-2024-002, the document tree updates
- [ ] ACTE-2024-002 shows different documents (or empty folders if no documents)
- [ ] No ACTE-2024-001 documents are visible when ACTE-2024-002 is active

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-03
### Document Viewer Clears on Case Switch

**Objective:** Verify document content clears when switching cases

**Steps:**
1. Open workspace with ACTE-2024-001
2. Click on "Birth_Certificate.txt" in the Personal Data folder
3. Verify document content displays in DocumentViewer
4. Note the current view mode (should show document content)
5. Use case search to switch to ACTE-2024-002 or ACTE-2024-003
6. Observe the DocumentViewer panel

**Expected Results:**
- [ ] Document content is visible after step 3
- [ ] After case switch, DocumentViewer clears/resets
- [ ] No content from previous case remains visible
- [ ] View mode resets to 'form' view
- [ ] FormViewer shows the new case's form (not the document)

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-04
### UTF-8 Text Display with German Characters

**Objective:** Verify German special characters display correctly

**Steps:**
1. Open workspace with ACTE-2024-001
2. Load each of the following documents:
   - Birth_Certificate.txt (Personal Data folder)
   - Passport_Scan.txt (Personal Data folder)
   - Language_Certificate_A1.txt (Certificates folder)
   - Integration_Application.txt (Applications folder)
   - Confirmation_Email.txt (Emails folder)
   - School_Transcripts.txt (Evidence folder)
3. For each document, check for German special characters

**Expected Results:**
For each document:
- [ ] Text is displayed in pre-formatted style (monospace, preserves line breaks)
- [ ] German umlauts display correctly: ä, ö, ü, Ä, Ö, Ü
- [ ] German ß (eszett) displays correctly
- [ ] No character encoding errors or replacement characters (�)
- [ ] Text is scrollable if content exceeds viewport
- [ ] No horizontal scroll needed for normal text

**Pass Criteria:** All documents display German characters correctly

---

## Test Case: TC-F-006-UI-05
### Error Handling for Missing Documents

**Objective:** Verify graceful error handling when document file is missing

**Steps:**
1. Open browser developer tools (F12)
2. Go to Network tab
3. In workspace, try to load a document
4. Observe the network request
5. Manually attempt to access a non-existent document URL in a new tab:
   `http://localhost:5173/documents/ACTE-2024-001/personal-data/NonExistent.txt`

**Expected Results:**
- [ ] Network request shows proper path: /documents/{caseId}/{folderId}/{filename}
- [ ] For non-existent file, response is 404 Not Found
- [ ] Application displays error toast notification
- [ ] Error message is user-friendly (e.g., "Failed to load document content")
- [ ] Application does not crash or show unhandled error
- [ ] Document tree remains functional after error

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-06
### Cross-Case Access Prevention

**Objective:** Verify users cannot access documents from other cases

**Steps:**
1. Open workspace with ACTE-2024-001 active
2. Note a document URL for ACTE-2024-001 (e.g., Birth_Certificate.txt)
3. Switch to ACTE-2024-002 or ACTE-2024-003
4. Try to manually navigate to ACTE-2024-001 document via:
   - Direct URL manipulation in browser
   - Attempting to click cached UI elements (if any)
5. Observe the behavior

**Expected Results:**
- [ ] Current case ID is clearly displayed in the UI header
- [ ] Document paths always use current case ID
- [ ] Attempting to access other case's document URL results in error or 404
- [ ] No way to bypass case isolation through UI
- [ ] Document loader always constructs paths with currentCase.id

**Pass Criteria:** Cross-case access is prevented

---

## Test Case: TC-F-006-UI-07
### Multiple Document Loading

**Objective:** Verify smooth experience when loading multiple documents

**Steps:**
1. Open workspace with ACTE-2024-001
2. Quickly load documents in sequence:
   - Click Birth_Certificate.txt
   - Wait for load (observe spinner)
   - Click Passport_Scan.txt
   - Wait for load
   - Click Language_Certificate_A1.txt
   - Wait for load
3. Load documents rapidly without waiting:
   - Click Birth_Certificate.txt
   - Immediately click Passport_Scan.txt
   - Immediately click Language_Certificate_A1.txt

**Expected Results:**
- [ ] Each document loads successfully in sequence
- [ ] Loading spinner appears for each load operation
- [ ] Toast notifications appear for each successful load
- [ ] Rapid clicks don't cause errors or race conditions
- [ ] Final document loaded is the last one clicked
- [ ] Previous document content is replaced, not appended

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-08
### Folder Structure Display

**Objective:** Verify all case folders are displayed correctly

**Steps:**
1. Open workspace with ACTE-2024-001
2. Observe the folder structure in the case tree
3. Expand each folder
4. Note the folder icons and labels

**Expected Results:**
- [ ] All 6 folders are visible:
  - Personal Data
  - Certificates
  - Integration Docs (may be empty)
  - Applications
  - Emails
  - Evidence
- [ ] Folders use appropriate icons
- [ ] Folder expand/collapse works smoothly
- [ ] Document count or indicators show correctly
- [ ] Empty folders (Integration Docs) are still visible and accessible

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-09
### Document Content Scrolling

**Objective:** Verify long documents are scrollable

**Steps:**
1. Open workspace with ACTE-2024-001
2. Load "School_Transcripts.txt" (Evidence folder) - this is the longest document (~4.7 KB)
3. Observe the document display

**Expected Results:**
- [ ] Full document content is loaded
- [ ] Vertical scrollbar appears if content exceeds viewport height
- [ ] Scrolling works smoothly
- [ ] No content is cut off or hidden
- [ ] Document viewer panel respects layout boundaries
- [ ] Pre-formatted text preserves original formatting

**Pass Criteria:** All checkboxes above are checked

---

## Test Case: TC-F-006-UI-10
### View Mode Persistence

**Objective:** Verify view modes work correctly with document loading

**Steps:**
1. Open workspace with ACTE-2024-001
2. Ensure view mode is 'form' (default)
3. Click a document (e.g., Birth_Certificate.txt)
4. Observe view mode change
5. Navigate to different folder
6. Click back to the document tree

**Expected Results:**
- [ ] Default view mode is 'form' showing FormViewer
- [ ] Clicking a document switches view mode to 'document'
- [ ] DocumentViewer becomes visible
- [ ] View mode indicator (if any) reflects current mode
- [ ] Switching folders doesn't clear the document if still selected
- [ ] Switching cases resets view mode to 'form'

**Pass Criteria:** All checkboxes above are checked

---

## Summary Checklist

After completing all manual tests above, verify:

- [ ] Document loading system works reliably
- [ ] Case-scoped paths are enforced
- [ ] UTF-8 encoding displays German characters correctly
- [ ] Error handling is graceful and user-friendly
- [ ] UI provides clear feedback (spinners, toasts)
- [ ] Case switching clears previous case's document content
- [ ] No cross-case data contamination
- [ ] Performance is acceptable (loads within 1-2 seconds)
- [ ] TypeScript compilation has no errors (verified in automated tests)

---

## Failure Reporting

If any test fails, document:

1. Test Case ID (e.g., TC-F-006-UI-03)
2. Step where failure occurred
3. Expected result that was not met
4. Actual behavior observed
5. Screenshots or error messages
6. Browser console errors (if any)
7. Network tab information (if relevant)

---

## Test Environment

- **Application URL:** http://localhost:5173 (or configured port)
- **Browser:** Chrome/Firefox/Edge (latest version recommended)
- **Test Data:** ACTE-2024-001 sample documents in public/documents/
- **Cases Available:** ACTE-2024-001, ACTE-2024-002, ACTE-2024-003

---

## Notes

- All automated tests passed (10/10) - see test-results.json
- These manual tests complement automated tests for UI-specific validation
- Some tests require visual inspection that cannot be automated
- Run manual tests after any UI changes to document loading system
