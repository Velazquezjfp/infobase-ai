# F-005: Case-Level Form Management (Case-Instance Scoped)

## Test Cases

### TC-F-005-01: Display Case Form on Case Load

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that when a case is loaded, the FormViewer displays the case's form with the correct fields and case name.

**Preconditions:**
- Case object loaded in AppContext
- FormViewer component displays case-level form
- initialFormFields array defined with 7 fields

**Test Steps:**
1. Open case ACTE-2024-001
2. Navigate to Form Viewer panel
3. Examine displayed form title and fields

**Expected Results:**
- FormViewer displays form with title "German Integration Course Application"
- Case ID "ACTE-2024-001" shown
- Fields visible:
  - Full Name (text, required)
  - Date of Birth (date, required)
  - Country of Origin (text, required)
  - Existing Language Certificates (text, optional)
  - Course Preference (select, optional)
  - Current Address (textarea, required)
  - Reason for Application (textarea, required)
- Total of 7 fields displayed
- Field counter shows "0/7 filled"

**Test Data:**
- Case ID: "ACTE-2024-001"
- Case Title: "German Integration Course Application"

**Notes:**
- Verify form is at case level, not folder level
- Check required indicator (asterisk) displayed

---

### TC-F-005-02: Form Persists Across Folder Navigation

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that the form remains unchanged when navigating between different folders within the same case.

**Preconditions:**
- Case loaded with multiple folders
- Form displayed in FormViewer

**Test Steps:**
1. Navigate to ACTE-2024-001 case
2. Verify form displays in FormViewer
3. Click "Personal Data" folder
4. Verify form remains the same
5. Click "Certificates" folder
6. Verify form remains the same
7. Click "Integration Course Documents" folder
8. Verify form remains the same

**Expected Results:**
- Form title stays "German Integration Course Application"
- Same 7 fields visible regardless of folder selected
- Form data does not change on folder switch
- No form schema change when navigating folders

**Test Data:**
- Folders: Personal Data, Certificates, Integration Course Documents, Applications, Emails, Additional Evidence

**Notes:**
- This confirms forms are at case level, NOT folder level
- Form should be independent of folder selection

---

### TC-F-005-03: Data Persistence Across Folder Navigation

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Ensure that form data entered persists when switching between folders within the same case.

**Preconditions:**
- Case loaded with form fields
- Form editable in FormViewer

**Test Steps:**
1. Select case ACTE-2024-001
2. Fill in Full Name: "Ahmad Ali"
3. Fill in Date of Birth: "1990-05-15"
4. Click "Certificates" folder
5. Check form values still present
6. Click "Personal Data" folder
7. Check form values still present
8. Fill in Country of Origin: "Afghanistan"
9. Switch to "Emails" folder
10. Check all values still present

**Expected Results:**
- Form retains all entered values:
  - Full Name: "Ahmad Ali"
  - Date of Birth: "1990-05-15"
  - Country of Origin: "Afghanistan"
- No data loss during folder navigation
- Form state persists across the entire case

**Test Data:**
N/A (interactive test)

**Notes:**
- This is different from the old folder-specific model
- Form data belongs to the case, not individual folders

---

### TC-F-005-04: Form Data Changes When Switching Cases

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that switching between cases loads different form data while maintaining the same form structure.

**Preconditions:**
- Multiple cases available via search
- Each case has its own form data in sampleCaseFormData

**Test Steps:**
1. Load case ACTE-2024-001
2. Note form values (if any)
3. Click Search button
4. Select case ACTE-2024-002 (Asylum Application)
5. Verify form loads with different data
6. Verify form structure (7 fields) remains same
7. Switch back to ACTE-2024-001
8. Verify original data restored

**Expected Results:**
- ACTE-2024-001 shows "German Integration Course Application"
- ACTE-2024-002 shows "Asylum Application" with different data
- Form field structure consistent (7 fields)
- Form data differs per case
- Switching back restores original case data

**Test Data:**
- Case 1: ACTE-2024-001 (German Integration Course Application)
- Case 2: ACTE-2024-002 (Asylum Application)
- Case 3: ACTE-2024-003 (Family Reunification)

**Notes:**
- Each case maintains independent form data (case-instance scoped)
- Form template may be the same but data differs per case
- Critical test for case isolation at form data level
- Form data stored separately: cases/ACTE-2024-001/, cases/ACTE-2024-002/, etc.

---

### TC-F-005-05: Admin Edit Case Form

**Type:** E2E
**Priority:** High
**Status:** Pending

**Description:**
Verify admin can edit form fields for the current case in the AdminConfigPanel.

**Preconditions:**
- Admin Mode enabled
- Admin Config Panel accessible
- Forms tab available

**Test Steps:**
1. Click "Admin" button to enable Admin Mode
2. Open Admin Config Panel
3. Navigate to Forms tab
4. Current case's form should be displayed
5. Add new field: "emergencyContact" (text, optional)
6. Save changes
7. Navigate back to FormViewer
8. Verify new field appears
9. Switch to User Mode
10. Verify field still visible

**Expected Results:**
- Forms tab shows current case's form fields
- New field added successfully
- Field appears in FormViewer for this case
- Changes persist after page refresh
- Field visible in both Admin and User modes

**Test Data:**
- New field: `{"id": "emergencyContact", "label": "Emergency Contact", "type": "text", "required": false}`

**Notes:**
- Admin edits apply to current case only
- No folder-specific form editing (removed concept)

---

### TC-F-005-06: Form Auto-Fill from Any Folder

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that form auto-fill command works from any folder since the form applies to the entire case.

**Preconditions:**
- Document available in case
- WebSocket connection established
- Form auto-fill feature functional

**Test Steps:**
1. Select case ACTE-2024-001
2. Navigate to "Personal Data" folder
3. Select birth certificate document
4. Send AI command: "/fillForm"
5. Verify form fields populated
6. Navigate to "Certificates" folder
7. Select language certificate document
8. Send AI command: "/fillForm"
9. Verify additional fields populated

**Expected Results:**
- Form parser uses case's form schema (not folder-specific)
- Fields populated from birth certificate:
  - Full Name: extracted value
  - Date of Birth: extracted value
  - Country of Origin: extracted value
- Fields populated from language certificate:
  - Existing Language Certificates: updated if relevant
- Same form used regardless of which folder document is in

**Test Data:**
```json
{
  "caseId": "ACTE-2024-001",
  "documentContent": "Birth Certificate content...",
  "formFields": [initialFormFields]
}
```

**Notes:**
- AI assistant fills case-level form from any document
- No folder-specific form schemas

---

### TC-F-005-07: New Case Gets Empty Form

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Ensure that creating a new case provides an empty form with the appropriate template for the case type.

**Preconditions:**
- New Case creation functional
- Form templates defined for case types

**Test Steps:**
1. Click "New Case" button
2. Select case type (if applicable)
3. Create new case
4. Open FormViewer
5. Verify form is empty
6. Verify form has correct structure

**Expected Results:**
- New case created successfully
- Form displays with appropriate template
- All fields are empty (no pre-filled data)
- Required fields marked
- Form ready for data entry
- No data from other cases

**Test Data:**
- New case type: Integration Course Application

**Notes:**
- New cases start with blank form
- Template based on case type

---

## Edge Cases

### TC-F-005-E01: Case Without Form Data

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test behavior when a case doesn't have form data in sampleCaseFormData.

**Test Steps:**
1. Load case that has no entry in sampleCaseFormData
2. Open Form Viewer
3. Check what form is displayed

**Expected Results:**
- Form displays with empty fields
- Uses default initialFormFields structure
- No errors or crashes
- User can fill in and save form

**Test Data:**
- Case ID with no sampleCaseFormData entry

**Notes:**
- Graceful handling of missing form data
- Default to empty form

---

### TC-F-005-E02: Very Large Form (50+ Fields)

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Test UI performance and usability with large form.

**Test Steps:**
1. Add 50+ fields to case form via Admin panel
2. Open FormViewer
3. Measure render time and responsiveness

**Expected Results:**
- Form renders within 2 seconds
- Scrolling smooth
- Field interactions responsive
- No UI freezing or lag

---

## Error Handling Tests

### TC-F-005-ERR01: Concurrent Form Updates

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test handling when multiple browser tabs modify the same case's form simultaneously.

**Test Steps:**
1. Open case in two browser tabs
2. Tab 1: Edit Full Name field
3. Tab 2: Edit Date of Birth field
4. Save in both tabs
5. Refresh and check final state

**Expected Results:**
- Last write wins (no merge conflicts in POC)
- No data corruption
- LocalStorage remains consistent

**Notes:**
- POC phase: Simple last-write-wins acceptable

---

### TC-F-005-ERR02: Invalid Case ID

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Handle requests with invalid or non-existent case IDs.

**Test Steps:**
1. Programmatically set currentCase to invalid value
2. Attempt to display form
3. Verify error handling

**Expected Results:**
- Invalid case ID caught
- Warning logged
- Falls back to default form or empty form
- No application crash

---

## Performance Tests

### TC-F-005-PERF01: Form Load Time

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Measure time to load and render form when switching cases.

**Test Steps:**
1. Start with case ACTE-2024-001
2. Switch to case ACTE-2024-002 via search
3. Measure time until form fully rendered
4. Repeat 10 times
5. Calculate average load time

**Expected Results:**
- Average form load time < 500ms
- No noticeable lag or delay
- Smooth user experience

---

## Data Integrity Tests

### TC-F-005-DATA01: Form Field ID Uniqueness

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Ensure field IDs are unique within the form.

**Test Steps:**
1. Load initialFormFields
2. Extract all field IDs
3. Check for duplicates
4. Verify uniqueness

**Expected Results:**
- No duplicate field IDs
- Clear error if duplicates found
- Each field uniquely identifiable

---

### TC-F-005-DATA02: Form Schema Validation

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Validate that form conforms to FormField interface schema.

**Test Steps:**
1. Load form fields from mockData
2. Validate each field against FormField interface
3. Check required properties present
4. Verify field types valid

**Expected Results:**
- All fields pass validation
- Each field has: id, label, type, value
- Field types in allowed set: text, date, select, textarea
- Select fields have options array
- No schema violations

---

## Automated Test Implementation

### Frontend Unit Tests (Jest/React Testing Library)

**File:** `src/components/workspace/__tests__/FormViewer.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import { FormViewer } from '../FormViewer';
import { AppContext } from '@/contexts/AppContext';

describe('FormViewer - Case-Level Forms', () => {
  it('displays case form title and ID', () => {
    const mockContext = {
      currentCase: {
        id: 'ACTE-2024-001',
        title: 'German Integration Course Application'
      },
      formFields: [
        { id: 'name', label: 'Full Name', type: 'text', value: '', required: true },
        { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '', required: true }
      ]
    };

    render(
      <AppContext.Provider value={mockContext}>
        <FormViewer />
      </AppContext.Provider>
    );

    expect(screen.getByText('German Integration Course Application')).toBeInTheDocument();
    expect(screen.getByText('ACTE-2024-001')).toBeInTheDocument();
  });

  it('form persists across folder changes', () => {
    // Test implementation - verify form doesn't change when folder changes
  });

  it('form data persists across folder navigation', () => {
    // Test implementation
  });

  it('loads different form data when switching cases', () => {
    // Test implementation
  });
});
```

### Integration Tests (Playwright)

**File:** `tests/e2e/case-forms.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('Case-level form management', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Verify form displays for case
  await expect(page.locator('text=German Integration Course Application')).toBeVisible();
  await expect(page.locator('text=ACTE-2024-001')).toBeVisible();

  // Verify 7 fields present
  await expect(page.locator('label:has-text("Full Name")')).toBeVisible();
  await expect(page.locator('label:has-text("Date of Birth")')).toBeVisible();

  // Fill form
  await page.fill('[data-field="name"]', 'Ahmad Ali');
  await page.fill('[data-field="birthDate"]', '1990-05-15');

  // Navigate to different folder
  await page.click('text=Certificates');

  // Verify form unchanged
  const nameValue = await page.inputValue('[data-field="name"]');
  expect(nameValue).toBe('Ahmad Ali');

  // Switch cases via search
  await page.click('button:has-text("Search")');
  await page.click('text=ACTE-2024-002');

  // Verify different case data
  await expect(page.locator('text=Asylum Application')).toBeVisible();
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 7 | 6 | 1 | 0 |
| E2E | 1 | 1 | 0 | 0 |
| Unit | 2 | 2 | 0 | 0 |
| Edge Cases | 2 | 0 | 1 | 1 |
| Error Handling | 2 | 0 | 2 | 0 |
| Performance | 1 | 0 | 1 | 0 |
| Data Integrity | 2 | 2 | 0 | 0 |
| **Total** | **17** | **11** | **5** | **1** |

---

## Test Execution Checklist

- [ ] Form displays for current case with title and ID
- [ ] Form has 7 fields matching initialFormFields
- [ ] Form persists when navigating between folders
- [ ] Form data persists across folder navigation
- [ ] Form data changes when switching cases
- [ ] Admin can edit form fields for current case
- [ ] AI auto-fill works from any folder
- [ ] New cases get empty form with correct template
- [ ] Performance benchmarks met
- [ ] Error scenarios tested
- [ ] User experience validated
