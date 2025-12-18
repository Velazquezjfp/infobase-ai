# NFR-003: Local Storage Without Database

## Test Cases

### TC-NFR-003-01: Form Fields Persistence

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that form fields added via admin panel persist to localStorage and survive page refresh.

**Preconditions:**
- LocalStorage utility implemented
- AppContext syncs formFields to localStorage
- localStorage available in browser

**Test Steps:**
1. Start with clean localStorage (clear all)
2. Open Admin Config Panel
3. Add 3 new form fields:
   - Field 1: text field "middleName"
   - Field 2: date field "visaExpiry"
   - Field 3: select field "educationLevel"
4. Verify fields added to AppContext
5. Check localStorage key "bamf_form_fields"
6. Refresh browser page (F5)
7. Navigate to Form Viewer
8. Verify all 3 fields still present

**Expected Results:**
- Fields immediately saved to localStorage after adding
- localStorage contains serialized FormField array
- After refresh, fields load from localStorage
- Fields visible and functional in Form Viewer
- Field values, types, and options preserved
- No data loss

**Test Data:**
```json
{
  "fields": [
    {"id": "middleName", "label": "Middle Name", "type": "text", "value": ""},
    {"id": "visaExpiry", "label": "Visa Expiry", "type": "date", "value": ""},
    {"id": "educationLevel", "label": "Education Level", "type": "select", "options": ["High School", "Bachelor", "Master"]}
  ]
}
```

**Notes:**
- localStorage key: "bamf_form_fields"
- Data serialized as JSON string

---

### TC-NFR-003-02: Fallback to Default on Empty LocalStorage

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that application loads with default initialFormFields when localStorage is empty or cleared.

**Preconditions:**
- Default initialFormFields defined in mockData
- LocalStorage fallback logic implemented

**Test Steps:**
1. Clear browser localStorage completely
2. Refresh page or open application fresh
3. Navigate to Form Viewer
4. Check which fields are displayed
5. Verify default fields from initialFormFields

**Expected Results:**
- Application loads without errors
- Form Viewer displays default fields from mockData
- No blank or broken form state
- User can immediately start working
- Default fields functional
- Application creates localStorage entries on first use

**Test Data:**
- Expected default fields from src/data/mockData.ts

**Notes:**
- Graceful fallback is critical for first-time users
- No error messages on clean start

---

### TC-NFR-003-03: LocalStorage Quota Warning

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify application warns user when localStorage usage approaches quota limit (5MB).

**Preconditions:**
- LocalStorage utility checks quota before saves
- Warning mechanism implemented
- localStorage quota detection functional

**Test Steps:**
1. Add many form fields to approach 5MB limit
2. Alternative: Generate 50+ complex form fields
3. Monitor localStorage size
4. Attempt to add more when near limit
5. Observe warning behavior
6. Test with artificially filled localStorage (4.5MB+)

**Expected Results:**
- Warning displayed when localStorage > 4.5MB
- Warning message: "Storage limit approaching. Consider removing unused data."
- Save prevented when > 4.9MB
- User notified: "Cannot save. Storage limit reached."
- Application remains functional
- User can delete old data to free space

**Test Data:**
- Large data payload to fill localStorage

**Notes:**
- localStorage quota typically 5-10MB per domain
- Exact quota varies by browser
- Check: `localStorage.length` and estimate size

---

### TC-NFR-003-04: Malformed JSON Handling

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test graceful handling when localStorage contains malformed JSON that cannot be parsed.

**Preconditions:**
- Error handling for JSON.parse exceptions
- Fallback to defaults on parse error

**Test Steps:**
1. Manually set malformed JSON in localStorage:
   ```javascript
   localStorage.setItem('bamf_form_fields', '{invalid json}')
   ```
2. Refresh page
3. Observe application behavior
4. Check console for error messages
5. Verify fallback to defaults

**Expected Results:**
- JSONSyntaxError caught gracefully
- Error logged to console with details
- Application falls back to default initialFormFields
- User notification: "Saved data corrupted. Loading defaults."
- Application remains functional
- No crash or blank screen

**Test Data:**
```javascript
// Malformed JSON examples:
'{invalid json}'
'{"incomplete": '
'not json at all'
```

**Notes:**
- Important for robustness
- Prevents application crash from corrupted storage

---

### TC-NFR-003-05: Backend Missing Context File Handling

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify backend context manager handles missing JSON files gracefully without crashing.

**Preconditions:**
- Context manager implemented
- Error handling for FileNotFoundError

**Test Steps:**
1. Request context for non-existent case type
2. OR temporarily rename integration_course.json
3. Attempt to load case context
4. Observe backend behavior
5. Check error logs

**Expected Results:**
- FileNotFoundError caught in context_manager.py
- Error logged with file path: "Context file not found: path/to/file.json"
- Empty context returned instead of crash
- Backend continues running
- Subsequent requests still work
- User notified if context unavailable

**Test Data:**
- Non-existent file path: `backend/data/contexts/case_types/nonexistent.json`

**Notes:**
- Use try/except with FileNotFoundError
- Log errors for debugging

---

### TC-NFR-003-06: Backend Invalid JSON Handling

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test backend handling of context files with invalid JSON syntax.

**Preconditions:**
- JSON parsing error handling
- Validation logic in context manager

**Test Steps:**
1. Create context file with invalid JSON:
   ```json
   {
     "name": "Test",
     "missing": "closing brace"
   ```
2. Attempt to load context
3. Catch JSONDecodeError
4. Verify error logging
5. Check return value

**Expected Results:**
- JSONDecodeError caught gracefully
- Detailed error logged:
  - File path
  - Error message
  - Line number if available
- Empty context returned with error flag
- Backend remains operational
- No application crash

**Test Data:**
- Malformed JSON file in data/contexts/

**Notes:**
- Use json.load() with try/except JSONDecodeError
- Provide helpful error messages

---

### TC-NFR-003-07: No Real-Time Sync Between Tabs

**Type:** Integration
**Priority:** Low
**Status:** Pending

**Description:**
Document and test that changes in one browser tab do NOT automatically sync to other tabs (POC limitation).

**Preconditions:**
- Application running in multiple browser tabs
- No storage event listeners implemented (POC)

**Test Steps:**
1. Open application in Tab 1
2. Open same application in Tab 2
3. In Tab 1: Add new form field "testField"
4. Wait 5 seconds
5. In Tab 2: Check if "testField" appears
6. Refresh Tab 2
7. Check if "testField" appears after refresh

**Expected Results:**
- Tab 2 does NOT see changes from Tab 1 automatically
- After refresh, Tab 2 loads latest from localStorage (last write wins)
- This is documented limitation for POC phase
- No sync conflicts or errors
- Last write wins strategy acceptable for single-user POC

**Test Data:**
N/A

**Notes:**
- Future enhancement: storage event listeners for sync
- POC: Single user, single tab expected
- Document this limitation clearly

---

## Edge Cases

### TC-NFR-003-E01: Very Large Form Persistence

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test persistence of form with 50+ fields.

**Test Steps:**
1. Create form with 50 fields
2. Save to localStorage
3. Measure save time
4. Refresh page
5. Measure load time
6. Verify all fields loaded

**Expected Results:**
- Save time < 500ms
- Load time < 1 second
- All 50 fields restored correctly
- Application responsive
- No data loss

**Notes:**
- Test localStorage performance limits
- Consider pagination if needed

---

### TC-NFR-003-E02: LocalStorage Disabled or Unavailable

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Handle scenario where localStorage is disabled (private browsing, browser settings).

**Test Steps:**
1. Disable localStorage (browser settings or mock)
2. Attempt to save form fields
3. Observe application behavior
4. Check error handling

**Expected Results:**
- Error caught when localStorage.setItem fails
- User notified: "Storage unavailable. Changes will not persist."
- Application continues in "session-only" mode
- Data works during session but lost on refresh
- Graceful degradation

**Notes:**
- Test with: `delete window.localStorage` (mock)
- Handle QuotaExceededError

---

### TC-NFR-003-E03: Concurrent Writes to LocalStorage

**Type:** Integration
**Priority:** Low
**Status:** Pending

**Description:**
Test behavior when rapid sequential writes occur to localStorage.

**Test Steps:**
1. Trigger multiple rapid form field updates
2. Each triggers localStorage save
3. Verify data consistency
4. Check final state

**Expected Results:**
- All writes complete
- Last write wins
- No corrupted data
- No race conditions causing parse errors
- Consistent final state

---

### TC-NFR-003-E04: Empty Context Files

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Handle context files that exist but are empty (0 bytes).

**Test Steps:**
1. Create empty context file
2. Attempt to load
3. Verify handling

**Expected Results:**
- JSONDecodeError caught (empty file)
- Empty context returned
- Warning logged
- No crash

---

## Data Integrity Tests

### TC-NFR-003-DATA01: LocalStorage Key Naming Convention

**Type:** Configuration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify consistent localStorage key naming and organization.

**Test Steps:**
1. Review all localStorage keys used
2. Check naming convention
3. Verify no conflicts with other apps

**Expected Results:**
- Keys prefixed with "bamf_"
- Clear, descriptive names:
  - "bamf_form_fields"
  - "bamf_case_form_data"
  - "bamf_admin_config"
- No generic names that might conflict
- Consistent naming pattern

**Test Data:**
Expected keys:
- bamf_form_fields
- bamf_case_form_data
- bamf_admin_config

**Notes:**
- Prefix prevents conflicts with other apps on same domain
- Document all localStorage keys

---

### TC-NFR-003-DATA02: Data Migration on Schema Change

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Plan for handling localStorage data when FormField schema changes in future.

**Test Steps:**
1. Simulate old schema data in localStorage
2. Implement version check or migration
3. Load application
4. Verify migration or compatibility

**Expected Results:**
- Version field in stored data (future proofing)
- Migration function handles old → new schema
- OR: Clear old data and use defaults if incompatible
- User notified of migration
- No data corruption

**Test Data:**
```json
{
  "version": "1.0",
  "fields": [...]
}
```

**Notes:**
- Important for future updates
- Plan migration strategy early

---

## Backend File Storage Tests

### TC-NFR-003-BACK01: Context File Paths

**Type:** Configuration
**Priority:** High
**Status:** Pending

**Description:**
Verify all context files are in correct locations with proper paths.

**Test Steps:**
1. Check directory structure: backend/data/contexts/
2. Verify subdirectories: case_types/, folders/
3. List all JSON files
4. Verify paths in code match actual locations
5. Test file access with relative and absolute paths

**Expected Results:**
- All context files in backend/data/contexts/
- Case types in case_types/ subdirectory
- Folder contexts in folders/ subdirectory
- Code uses correct paths (relative to project root)
- Files accessible when backend runs

**Test Data:**
Expected structure:
```
backend/data/contexts/
├── case_types/
│   └── integration_course.json
└── folders/
    ├── personal_data.json
    ├── certificates.json
    ├── integration_docs.json
    ├── applications.json
    ├── emails.json
    └── evidence.json
```

**Notes:**
- Use Path from pathlib for cross-platform compatibility
- Document base path configuration

---

### TC-NFR-003-BACK02: Context File Permissions

**Type:** Configuration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify context files have appropriate read permissions.

**Test Steps:**
1. Check file permissions on context JSON files
2. Verify backend user can read files
3. Test loading in different environments (dev, prod-like)

**Expected Results:**
- Files readable by backend process
- No permission denied errors
- Consistent across environments
- Files not writable by backend (read-only data)

**Test Data:**
N/A

**Notes:**
- Permissions: 644 (rw-r--r--) typical for data files
- Backend should not write to these files (read-only)

---

## Automated Test Implementation

### Frontend LocalStorage Tests (Jest)

**File:** `src/lib/__tests__/localStorage.test.ts`

```typescript
import { saveToLocalStorage, loadFromLocalStorage, clearLocalStorage } from '../localStorage';

describe('localStorage utility', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('saves data to localStorage', () => {
    const data = { id: 'test', value: 'data' };
    saveToLocalStorage('test_key', data);

    const stored = localStorage.getItem('test_key');
    expect(stored).toBeTruthy();
    expect(JSON.parse(stored!)).toEqual(data);
  });

  it('loads data from localStorage', () => {
    const data = { id: 'test', value: 'data' };
    localStorage.setItem('test_key', JSON.stringify(data));

    const loaded = loadFromLocalStorage('test_key');
    expect(loaded).toEqual(data);
  });

  it('returns null for non-existent key', () => {
    const loaded = loadFromLocalStorage('non_existent');
    expect(loaded).toBeNull();
  });

  it('handles malformed JSON gracefully', () => {
    localStorage.setItem('test_key', '{invalid json}');

    const loaded = loadFromLocalStorage('test_key');
    expect(loaded).toBeNull(); // or default value
  });

  it('checks quota before save', () => {
    // Mock large data
    const largeData = 'x'.repeat(5 * 1024 * 1024); // 5MB

    expect(() => {
      saveToLocalStorage('large_key', largeData);
    }).toThrow('Storage quota exceeded');
  });
});
```

### Backend Context Loading Tests (Python)

**File:** `backend/tests/test_context_storage.py`

```python
import pytest
import json
from pathlib import Path
from backend.services.context_manager import ContextManager

def test_load_existing_context(tmp_path):
    """Test loading valid context file"""
    context_data = {"name": "Test", "description": "Test context"}
    context_file = tmp_path / "test_context.json"
    context_file.write_text(json.dumps(context_data))

    manager = ContextManager(base_path=tmp_path)
    loaded = manager.load_json_file(context_file)

    assert loaded == context_data

def test_missing_context_file(tmp_path):
    """Test handling of missing context file"""
    manager = ContextManager(base_path=tmp_path)
    loaded = manager.load_json_file(tmp_path / "nonexistent.json")

    assert loaded == {}  # Returns empty dict, not exception

def test_invalid_json_context(tmp_path):
    """Test handling of malformed JSON"""
    context_file = tmp_path / "invalid.json"
    context_file.write_text("{invalid json}")

    manager = ContextManager(base_path=tmp_path)
    loaded = manager.load_json_file(context_file)

    assert loaded == {}  # Returns empty dict
    # Check that error was logged (if using logging)
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 4 | 3 | 1 | 0 |
| Unit | 2 | 2 | 0 | 0 |
| Edge Cases | 4 | 0 | 2 | 2 |
| Data Integrity | 2 | 0 | 2 | 0 |
| Backend Storage | 2 | 1 | 1 | 0 |
| **Total** | **14** | **6** | **6** | **2** |

---

## LocalStorage Keys Documentation

| Key | Purpose | Data Type | Max Size Estimate |
|-----|---------|-----------|-------------------|
| bamf_form_fields | Form field schema template | FormField[] | ~50KB (100 fields) |
| bamf_case_form_data | Per-case form data values | Record<string, Record<string, string>> | ~300KB (10 cases × 30 fields) |
| bamf_admin_config | Admin panel settings | Object | ~10KB |
| bamf_case_data (future) | Case metadata | Case[] | TBD |

**Total Estimated Usage:** ~400KB (well under 5MB limit for typical usage)

---

## Test Execution Checklist

- [ ] LocalStorage utility implemented with error handling
- [ ] FormFields persistence working
- [ ] Case form data persistence working
- [ ] Quota checking implemented
- [ ] Fallback to defaults tested
- [ ] Malformed JSON handling verified
- [ ] Backend context file loading working
- [ ] Missing file handling tested
- [ ] Invalid JSON handling tested
- [ ] All localStorage keys documented
- [ ] Migration strategy planned
- [ ] POC limitations documented (no sync, no DB)
