# S4-002 UI Integration Tests - Manual Test Cases

These tests validate the frontend integration of file deletion functionality including delete button visibility, confirmation dialog behavior, and state synchronization.

## Test Setup

1. Start the development server: `npm run dev`
2. Start the backend server: `cd backend && python -m uvicorn main:app --reload`
3. Navigate to the application: `http://localhost:5173`
4. Select case: **ACTE-2024-001**
5. Upload test files to the "uploads" folder using drag-and-drop

---

## TC-S4-002-01: Click delete on uploaded file, verify confirmation dialog appears

**Objective:** Verify that clicking the delete button displays a confirmation dialog.

**Prerequisites:**
- At least one file exists in the uploads folder

**Steps:**
1. Navigate to case ACTE-2024-001
2. Expand the "uploads" folder in the document tree
3. Hover over any uploaded file
4. Observe the delete button (trash icon) appears on hover
5. Click the delete button

**Expected Results:**
- ✓ Delete button (Trash2 icon) is visible on hover
- ✓ Button has red color indicating destructive action
- ✓ Confirmation dialog appears with title "Delete File"
- ✓ Dialog shows message: "Are you sure you want to delete [filename]? This action cannot be undone."
- ✓ Dialog has two buttons: "Cancel" and "Delete"
- ✓ "Delete" button has destructive styling (red)

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-03: Cancel deletion, verify file remains unchanged

**Objective:** Verify that clicking "Cancel" in the confirmation dialog preserves the file.

**Prerequisites:**
- File exists in uploads folder
- Confirmation dialog is open

**Steps:**
1. Click delete button on an uploaded file
2. Confirmation dialog appears
3. Click the "Cancel" button

**Expected Results:**
- ✓ Dialog closes
- ✓ File remains in the document tree
- ✓ File still exists in filesystem (verify in backend)
- ✓ No toast notification displayed
- ✓ File can still be selected and viewed

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-04: Delete file, verify removed from document tree immediately

**Objective:** Verify that file is removed from the UI document tree after successful deletion.

**Prerequisites:**
- File exists in uploads folder

**Steps:**
1. Note the filename to delete (e.g., "test-upload.txt")
2. Click delete button on the file
3. Click "Delete" in confirmation dialog
4. Observe the document tree

**Expected Results:**
- ✓ File disappears from document tree immediately
- ✓ Success toast notification appears: "File deleted successfully"
- ✓ Toast shows filename that was deleted
- ✓ Folder structure remains intact
- ✓ Other files in the folder are unaffected

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-08: Success deletion, verify toast notification shown

**Objective:** Verify that a success toast notification is displayed after file deletion.

**Prerequisites:**
- File exists in uploads folder

**Steps:**
1. Click delete button on an uploaded file
2. Click "Delete" in confirmation dialog
3. Observe the toast notification area (top-right corner)

**Expected Results:**
- ✓ Toast appears with title "File deleted successfully"
- ✓ Toast description shows filename: "Deleted [filename]"
- ✓ Toast has default (success) styling
- ✓ Toast auto-dismisses after a few seconds
- ✓ Toast can be manually dismissed

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-09: Delete button only visible in uploads folder (not other folders)

**Objective:** Verify that the delete button is only shown for files in the uploads folder.

**Prerequisites:**
- Files exist in both uploads folder and system folders (e.g., personal-data, certificates)

**Steps:**
1. Navigate to case ACTE-2024-001
2. Expand the "uploads" folder
3. Hover over an uploaded file
4. Observe the delete button appears
5. Expand a system folder (e.g., "personal-data")
6. Hover over a file in the system folder
7. Observe whether delete button appears

**Expected Results:**
- ✓ Delete button (Trash2 icon) visible for files in "uploads" folder
- ✓ Delete button NOT visible for files in system folders
- ✓ Context menu for system folder files does not show "Delete File" option
- ✓ Only uploads folder files can be deleted

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-10: Verify selected document cleared if deleted file was selected

**Objective:** Verify that if the currently selected/viewed document is deleted, the DocumentViewer is cleared.

**Prerequisites:**
- File exists in uploads folder

**Steps:**
1. Click on a file in uploads folder to select and view it
2. Verify the file content is displayed in DocumentViewer
3. Click the delete button for the same file
4. Confirm deletion in the dialog
5. Observe the DocumentViewer panel

**Expected Results:**
- ✓ File is deleted from tree
- ✓ DocumentViewer is cleared (shows placeholder or empty state)
- ✓ No error occurs in the console
- ✓ User can select another document
- ✓ Application state is consistent

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-Context-Menu: Delete via context menu

**Objective:** Verify that files can be deleted using the right-click context menu.

**Prerequisites:**
- File exists in uploads folder

**Steps:**
1. Right-click on a file in uploads folder
2. Observe the context menu
3. Click "Delete File" option with trash icon
4. Confirm in the dialog

**Expected Results:**
- ✓ Context menu shows "Delete File" option with Trash2 icon
- ✓ Option has red (destructive) text color
- ✓ Clicking option opens confirmation dialog
- ✓ File can be deleted via context menu
- ✓ Same behavior as delete button

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-Error-Network: Network error during deletion

**Objective:** Verify error handling when backend is unavailable during deletion.

**Prerequisites:**
- File exists in uploads folder
- Backend server is running

**Steps:**
1. Start deletion process
2. Stop the backend server before clicking "Delete" in confirmation
3. Click "Delete" button
4. Observe the behavior

**Expected Results:**
- ✓ Loading state shown while attempting deletion
- ✓ Error toast appears: "Failed to delete file"
- ✓ Error message describes the issue (network error)
- ✓ File remains in document tree (not removed)
- ✓ User can retry after backend is back

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## TC-S4-002-Multiple-Files: Delete multiple files sequentially

**Objective:** Verify that multiple files can be deleted one after another without issues.

**Prerequisites:**
- Multiple files exist in uploads folder (at least 3)

**Steps:**
1. Upload 3 test files to uploads folder
2. Delete the first file, confirm
3. Immediately delete the second file, confirm
4. Delete the third file, confirm

**Expected Results:**
- ✓ All three files deleted successfully
- ✓ Each deletion shows confirmation dialog
- ✓ Each deletion shows success toast
- ✓ Document tree updates correctly after each deletion
- ✓ No state inconsistencies or errors
- ✓ Folder remains after deleting all files

**Status:** ⬜ Not Run | ⬜ Pass | ⬜ Fail

**Notes:**
_______________________________________________________________________

---

## Test Execution Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-S4-002-01 | ⬜ | Confirmation dialog appears |
| TC-S4-002-03 | ⬜ | Cancel preserves file |
| TC-S4-002-04 | ⬜ | File removed from tree |
| TC-S4-002-08 | ⬜ | Success toast shown |
| TC-S4-002-09 | ⬜ | Delete button only in uploads |
| TC-S4-002-10 | ⬜ | Selected document cleared |
| Context Menu | ⬜ | Delete via right-click |
| Network Error | ⬜ | Error handling |
| Multiple Files | ⬜ | Sequential deletion |

**Total Tests:** 9
**Passed:** 0
**Failed:** 0
**Not Run:** 9

---

## Notes

- These tests require manual execution as they involve UI interactions
- Alternatively, these can be automated using Playwright or similar UI testing framework
- All tests should be executed in a clean test environment
- Test files should be backed up before deletion tests
