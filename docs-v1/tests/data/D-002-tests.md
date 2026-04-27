# D-002: Case-Type Form Schemas (Case-Instance Scoped)

## Test Cases

### TC-D-002-01: Initial Form Fields Completeness

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify that initialFormFields array contains all 7 required fields with correct specifications for the Integration Course Application form.

**Preconditions:**
- initialFormFields defined in src/data/mockData.ts
- FormField interface available

**Test Steps:**
1. Import initialFormFields from mockData
2. Verify array length equals 7
3. Check each field for required properties: id, label, type, value, required
4. Verify required fields have required=true
5. List all field IDs

**Expected Results:**
- Array length: 7 fields
- Fields present:
  1. fullName (text, required)
  2. birthDate (date, required)
  3. countryOfOrigin (text, required)
  4. existingLanguageCertificates (text, optional)
  5. coursePreference (select, optional)
  6. currentAddress (textarea, required)
  7. reasonForApplication (textarea, required)
- 5 fields required, 2 optional
- All fields have empty value: ""
- Field types appropriate for data

**Test Data:**
Expected field IDs: fullName, birthDate, countryOfOrigin, existingLanguageCertificates, coursePreference, currentAddress, reasonForApplication

**Notes:**
- Form is at case level, applies to all Integration Course cases
- Same structure used for all cases of this type

---

### TC-D-002-02: Course Preference Options

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test that coursePreference field contains all expected course type options.

**Preconditions:**
- coursePreference field defined in initialFormFields
- Select field with options array

**Test Steps:**
1. Import initialFormFields
2. Find field with id="coursePreference"
3. Verify type="select"
4. Check options array
5. Verify all course preferences present

**Expected Results:**
- coursePreference field exists
- type: "select"
- required: false (optional)
- options array length: 3
- options: ["Intensive Course", "Evening Course", "Weekend Course"]
- Options represent common BAMF course types

**Test Data:**
Expected options: Intensive Course, Evening Course, Weekend Course

**Notes:**
- Course preferences match BAMF integration course offerings
- Used for enrollment preference tracking

---

### TC-D-002-03: Sample Case Form Data Structure

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify sampleCaseFormData has entries for all mock cases with correct data structure.

**Preconditions:**
- sampleCaseFormData defined in mockData.ts
- Multiple cases exist in mockCases

**Test Steps:**
1. Load sampleCaseFormData
2. Verify entries exist for ACTE-2024-001, ACTE-2024-002, ACTE-2024-003
3. Check each entry has Record<string, string> structure
4. Verify field IDs match initialFormFields

**Expected Results:**
- sampleCaseFormData has 3 entries
- Keys: "ACTE-2024-001", "ACTE-2024-002", "ACTE-2024-003"
- Each value is Record<string, string>
- Field keys match initialFormFields field IDs
- Data values are strings (can be empty)

**Test Data:**
Expected case IDs: ACTE-2024-001, ACTE-2024-002, ACTE-2024-003

**Notes:**
- Each case has independent form data
- Data structure allows per-case customization

---

### TC-D-002-04: Form Fields Match Initial Schema

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that when loading a case, the form fields match the initialFormFields schema.

**Preconditions:**
- Case loaded in AppContext
- FormViewer displays form fields

**Test Steps:**
1. Load case ACTE-2024-001
2. Access formFields from AppContext
3. Compare structure to initialFormFields
4. Verify field count matches
5. Verify field properties match

**Expected Results:**
- formFields has same structure as initialFormFields
- All 7 fields present
- Field IDs match
- Field types match
- Field labels match
- Required flags match

**Test Data:**
- Case ID: "ACTE-2024-001"

**Notes:**
- Form schema is consistent across cases
- Only form data (values) differs per case

---

### TC-D-002-05: Form Field Interface Validation

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Validate that all form fields conform to the FormField interface schema.

**Preconditions:**
- FormField interface defined in src/types/case.ts
- initialFormFields array created

**Test Steps:**
1. Load initialFormFields from mockData
2. For each field, iterate through properties
3. Verify each field has required properties:
   - id (string, unique within form)
   - label (string, non-empty)
   - type ('text' | 'date' | 'select' | 'textarea')
   - value (string)
   - required (boolean)
4. For select fields, verify options array exists
5. Check no duplicate field IDs

**Expected Results:**
- All fields conform to FormField interface
- No missing required properties
- Field types valid
- Select fields have options array
- No duplicate IDs
- Labels are clear and user-friendly
- Initial values are empty strings

**Test Data:**
initialFormFields array with 7 fields

**Notes:**
- TypeScript compilation catches many issues
- Runtime validation still valuable

---

### TC-D-002-06: Case-Specific Form Data Loading

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that switching between cases loads different form data while maintaining consistent form structure.

**Preconditions:**
- Multiple cases available
- sampleCaseFormData has entries for each case

**Test Steps:**
1. Load case ACTE-2024-001
2. Note form field values
3. Switch to case ACTE-2024-002
4. Verify form structure unchanged (7 fields)
5. Verify form values changed
6. Switch back to ACTE-2024-001
7. Verify original values restored

**Expected Results:**
- Form structure consistent (7 fields)
- Field IDs unchanged between cases
- Field values differ per case
- Values from sampleCaseFormData loaded correctly
- No data mixing between cases

**Test Data:**
- Case 1: ACTE-2024-001
- Case 2: ACTE-2024-002

**Notes:**
- Forms are case-level, not folder-level
- Same schema, different data per case

---

### TC-D-002-07: Form Rendering in FormViewer

**Type:** E2E
**Priority:** High
**Status:** Pending

**Description:**
Test that the form renders correctly in the FormViewer component with proper inputs and dropdowns.

**Preconditions:**
- Application running
- FormViewer component displays case form
- All fields accessible

**Test Steps:**
1. Navigate to case
2. Open FormViewer panel
3. Verify all 7 fields display
4. Test text inputs are functional
5. Test date input works
6. Test select dropdown populates correctly
7. Test textarea allows multi-line input

**Expected Results:**
- All 7 fields visible:
  - Full Name (text input)
  - Date of Birth (date picker)
  - Country of Origin (text input)
  - Existing Language Certificates (text input)
  - Course Preference (select dropdown)
  - Current Address (textarea)
  - Reason for Application (textarea)
- Select dropdown shows 3 options
- All fields editable
- Required indicators visible (asterisk)
- Form layout clean and usable

**Test Data:**
N/A (interactive test)

**Notes:**
- Visual/functional test
- Verify user experience acceptable

---

## Field-Level Validation Tests

### TC-D-002-FIELD01: Date Field Format

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify date fields accept valid date formats and handle invalid input appropriately.

**Test Steps:**
1. Test birthDate field
2. Enter valid date: "1990-05-15" (ISO format)
3. Check browser date validation
4. Verify date picker available

**Expected Results:**
- ISO format (YYYY-MM-DD) accepted by HTML date input
- Browser handles date validation
- Date picker available in modern browsers
- Appropriate error messages for invalid dates

**Notes:**
- HTML5 date input provides built-in validation

---

### TC-D-002-FIELD02: Select Field Default Values

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test default value behavior for the coursePreference select field.

**Test Steps:**
1. Load form with coursePreference field
2. Check initial value
3. Verify placeholder or empty as default
4. Test user selection updates value

**Expected Results:**
- Select field initially shows placeholder "Select course preference"
- User can select any of 3 options
- Value updates in form state
- Optional field doesn't require selection

---

### TC-D-002-FIELD03: Textarea Field Behavior

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test textarea fields (currentAddress, reasonForApplication) handle multi-line input.

**Test Steps:**
1. Access currentAddress textarea field
2. Enter multi-line address:
   ```
   Hauptstraße 123
   12345 Berlin
   Germany
   ```
3. Verify line breaks preserved
4. Test reasonForApplication similarly
5. Check scrolling behavior for long content

**Expected Results:**
- Multi-line input supported
- Line breaks preserved in value
- Long text doesn't break layout
- Scrollbar appears for long content
- Text wraps appropriately

---

## Data Integrity Tests

### TC-D-002-DATA01: Field ID Uniqueness

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Ensure field IDs are unique within the form (no duplicates).

**Test Steps:**
1. Load initialFormFields
2. Extract all field IDs
3. Check for duplicates
4. Verify uniqueness

**Expected Results:**
- No duplicate field IDs
- All 7 IDs unique
- Clear error if duplicates found

**Notes:**
- Duplicate IDs break state management

---

### TC-D-002-DATA02: Required Field Distribution

**Type:** Analysis
**Priority:** Medium
**Status:** Pending

**Description:**
Analyze distribution of required vs. optional fields.

**Test Steps:**
1. Count required fields
2. Count optional fields
3. Verify appropriate balance

**Expected Results:**
- Required fields (5):
  - fullName
  - birthDate
  - countryOfOrigin
  - currentAddress
  - reasonForApplication
- Optional fields (2):
  - existingLanguageCertificates
  - coursePreference
- Balance appropriate for integration course application

**Notes:**
- Too many required fields burdensome
- Critical identity fields are required

---

### TC-D-002-DATA03: Label Clarity

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Review all field labels for clarity and user-friendliness.

**Test Steps:**
1. Review each field label
2. Check for clear, descriptive text
3. Verify no jargon or abbreviations
4. Check consistency in capitalization

**Expected Results:**
- Labels clear and descriptive:
  - "Full Name" (not just "Name")
  - "Date of Birth" (not "DOB")
  - "Country of Origin" (clear context)
  - "Existing Language Certificates" (descriptive)
  - "Course Preference" (clear purpose)
  - "Current Address" (obvious)
  - "Reason for Application" (explains what to write)
- Consistent style (Title Case)
- Appropriate length

---

## Automated Test Implementation

### Form Schema Tests (TypeScript/Jest)

**File:** `src/data/__tests__/formSchemas.test.ts`

```typescript
import { initialFormFields, sampleCaseFormData } from '../mockData';
import { FormField } from '@/types/case';

describe('Case-Type Form Schemas', () => {
  describe('initialFormFields', () => {
    it('has exactly 7 fields', () => {
      expect(initialFormFields).toHaveLength(7);
    });

    it('has correct required fields', () => {
      const requiredFields = initialFormFields.filter(f => f.required);
      expect(requiredFields).toHaveLength(5);

      const requiredIds = requiredFields.map(f => f.id);
      expect(requiredIds).toContain('fullName');
      expect(requiredIds).toContain('birthDate');
      expect(requiredIds).toContain('countryOfOrigin');
      expect(requiredIds).toContain('currentAddress');
      expect(requiredIds).toContain('reasonForApplication');
    });

    it('has all expected field IDs', () => {
      const ids = initialFormFields.map(f => f.id);
      expect(ids).toContain('fullName');
      expect(ids).toContain('birthDate');
      expect(ids).toContain('countryOfOrigin');
      expect(ids).toContain('existingLanguageCertificates');
      expect(ids).toContain('coursePreference');
      expect(ids).toContain('currentAddress');
      expect(ids).toContain('reasonForApplication');
    });

    it('coursePreference has correct options', () => {
      const courseField = initialFormFields.find(f => f.id === 'coursePreference');
      expect(courseField?.type).toBe('select');
      expect(courseField?.options).toEqual([
        'Intensive Course',
        'Evening Course',
        'Weekend Course'
      ]);
    });

    it('textarea fields are correctly typed', () => {
      const addressField = initialFormFields.find(f => f.id === 'currentAddress');
      const reasonField = initialFormFields.find(f => f.id === 'reasonForApplication');

      expect(addressField?.type).toBe('textarea');
      expect(reasonField?.type).toBe('textarea');
    });

    it('birthDate is date type', () => {
      const dateField = initialFormFields.find(f => f.id === 'birthDate');
      expect(dateField?.type).toBe('date');
    });
  });

  describe('sampleCaseFormData', () => {
    it('has entries for all mock cases', () => {
      expect(sampleCaseFormData['ACTE-2024-001']).toBeDefined();
      expect(sampleCaseFormData['ACTE-2024-002']).toBeDefined();
      expect(sampleCaseFormData['ACTE-2024-003']).toBeDefined();
    });

    it('each case has Record<string, string> structure', () => {
      Object.values(sampleCaseFormData).forEach(caseData => {
        expect(typeof caseData).toBe('object');
        Object.entries(caseData).forEach(([key, value]) => {
          expect(typeof key).toBe('string');
          expect(typeof value).toBe('string');
        });
      });
    });
  });

  describe('Form Field Validation', () => {
    it('all fields have valid structure', () => {
      initialFormFields.forEach(field => {
        expect(field).toHaveProperty('id');
        expect(field).toHaveProperty('label');
        expect(field).toHaveProperty('type');
        expect(field).toHaveProperty('value');
        expect(field).toHaveProperty('required');

        expect(typeof field.id).toBe('string');
        expect(typeof field.label).toBe('string');
        expect(['text', 'date', 'select', 'textarea']).toContain(field.type);
        expect(typeof field.value).toBe('string');
        expect(typeof field.required).toBe('boolean');

        if (field.type === 'select') {
          expect(field.options).toBeDefined();
          expect(Array.isArray(field.options)).toBe(true);
        }
      });
    });

    it('has unique field IDs', () => {
      const ids = initialFormFields.map(f => f.id);
      const uniqueIds = new Set(ids);
      expect(ids.length).toBe(uniqueIds.size);
    });

    it('initial values are empty strings', () => {
      initialFormFields.forEach(field => {
        expect(field.value).toBe('');
      });
    });
  });
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Unit | 6 | 5 | 1 | 0 |
| Integration | 2 | 2 | 0 | 0 |
| E2E | 1 | 1 | 0 | 0 |
| Field Validation | 3 | 0 | 3 | 0 |
| Data Integrity | 3 | 1 | 2 | 0 |
| **Total** | **15** | **9** | **6** | **0** |

---

## Form Schema Summary

| Property | Value |
|----------|-------|
| Total Fields | 7 |
| Required Fields | 5 |
| Optional Fields | 2 |
| Text Fields | 3 |
| Date Fields | 1 |
| Select Fields | 1 |
| Textarea Fields | 2 |

---

## Test Execution Checklist

- [ ] initialFormFields has 7 fields
- [ ] 5 required, 2 optional fields
- [ ] coursePreference has 3 course options
- [ ] sampleCaseFormData has entries for 3 cases
- [ ] All fields conform to FormField interface
- [ ] Field IDs unique
- [ ] Date field uses correct type
- [ ] Textarea fields configured properly
- [ ] Form renders correctly in FormViewer
- [ ] Required fields marked appropriately
- [ ] Labels clear and user-friendly
- [ ] Automated tests passing
