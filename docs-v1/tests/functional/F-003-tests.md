# F-003: Form Auto-Fill from Document Content (Case-Aware)

## Test Cases

### TC-F-003-01: Extract Simple Name Field

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify the AI agent can extract a person's name from document content and populate the corresponding form field.

**Preconditions:**
- WebSocket connection established
- Document with clear name reference loaded
- Form schema includes "name" field of type "text"
- Form parser tool registered in Gemini service

**Test Steps:**
1. Select document containing: "Name: John Doe"
2. Send command: "/fillForm"
3. Include current formFields schema in request
4. Wait for FormUpdateMessage response
5. Verify frontend updates formFields['name'].value

**Expected Results:**
- FormUpdateMessage received within 5 seconds
- Message type: "form_update"
- Updates object: `{"name": "John Doe"}`
- Confidence score > 0.8 for name field
- Frontend AppContext.formFields['name'].value = "John Doe"

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Name: John Doe\nPassport Number: P123456789",
  "formFields": [
    {"id": "name", "label": "Full Name", "type": "text", "value": "", "required": true}
  ],
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data"
}
```

**Notes:**
- Test with variations: "Full Name:", "Applicant:", "Name of Person:"
- Verify exact text match (no extra spaces)

---

### TC-F-003-02: Extract and Format Date Field

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test extraction of birth date from German format (DD.MM.YYYY) and conversion to ISO format (YYYY-MM-DD) for date input fields.

**Preconditions:**
- Document with German date format
- Form has birthDate field of type "date"
- Date parsing logic implemented

**Test Steps:**
1. Load document with text: "Born: 15.05.1990"
2. Send "/fillForm" command
3. Include date field in form schema
4. Verify date extracted and converted to ISO format

**Expected Results:**
- FormUpdateMessage contains: `{"birthDate": "1990-05-15"}`
- Date converted from German format (15.05.1990) to ISO (1990-05-15)
- Frontend date input displays formatted correctly
- Invalid dates rejected or flagged for review

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Name: Ahmad Ali\nBorn: 15.05.1990\nPlace of Birth: Kabul",
  "formFields": [
    {"id": "birthDate", "label": "Date of Birth", "type": "date", "value": "", "required": true}
  ]
}
```

**Notes:**
- Test multiple date formats: DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
- Test with German keywords: "Geburtsdatum", "Geboren"
- Verify February 29 leap year handling

---

### TC-F-003-03: Extract Country from Text

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Validate extraction of country of origin from document text, handling various phrasings.

**Preconditions:**
- Document mentions country name
- Form has countryOfOrigin field (text or select type)

**Test Steps:**
1. Load document: "Country of Origin: Afghanistan"
2. Send form fill command
3. Verify country name extracted correctly
4. If select field, verify value matches options array

**Expected Results:**
- FormUpdateMessage: `{"countryOfOrigin": "Afghanistan"}`
- If select field, value matches one of the predefined options
- Handles variations: "from Afghanistan", "Afghan citizen", "Afghanistan origin"
- Country name standardized (proper capitalization)

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Applicant from Afghanistan, residing in Germany since 2020",
  "formFields": [
    {"id": "countryOfOrigin", "label": "Country of Origin", "type": "text", "value": ""}
  ]
}
```

**Notes:**
- Test with both English and German country names
- Test with common misspellings
- Verify handling of country name changes (e.g., Myanmar/Burma)

---

### TC-F-003-04: Extract from German Document

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Ensure form auto-fill works correctly with German language documents, extracting data despite language difference.

**Preconditions:**
- German document loaded
- Form schema in English
- Multilingual extraction capability

**Test Steps:**
1. Load German birth certificate: "Geburtsdatum: 15.05.1990"
2. Send "/fillForm" command
3. Verify data extracted despite language
4. Check field mapping accuracy

**Expected Results:**
- Date extracted: `{"birthDate": "1990-05-15"}`
- German text understood: "Geburtsdatum" → birthDate field
- Other German fields correctly mapped:
  - "Vorname" → firstName
  - "Nachname" → lastName
  - "Geburtsort" → placeOfBirth
- No data loss due to language barrier

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Geburtsurkunde\nVorname: Ahmad\nNachname: Ali\nGeburtsdatum: 15.05.1990\nGeburtsort: Kabul, Afghanistan",
  "formFields": [
    {"id": "firstName", "label": "First Name", "type": "text", "value": ""},
    {"id": "lastName", "label": "Last Name", "type": "text", "value": ""},
    {"id": "birthDate", "label": "Date of Birth", "type": "date", "value": ""},
    {"id": "placeOfBirth", "label": "Place of Birth", "type": "text", "value": ""}
  ]
}
```

**Notes:**
- Test with documents mixing German and English
- Verify umlauts handled correctly (ä → ae, ü → ue if needed)

---

### TC-F-003-05: Ambiguous Data Clarification

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test agent behavior when document contains ambiguous or conflicting information, ensuring it asks for clarification rather than guessing.

**Preconditions:**
- Document with ambiguous data
- Multiple possible interpretations

**Test Steps:**
1. Load document with two dates: "Born 15.05.1990, arrived 20.03.2020"
2. Request form fill with single birthDate field
3. Observe agent response
4. Verify clarification requested

**Expected Results:**
- Agent does not auto-fill ambiguous field
- Response includes clarification question: "I found two dates. Which one is the birth date?"
- OR agent fills with highest confidence and flags for review
- Confidence score low (<0.6) for ambiguous extractions
- User prompted to verify extracted value

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Ahmad Ali, dates: 15.05.1990 and 20.03.2020",
  "formFields": [
    {"id": "birthDate", "label": "Date of Birth", "type": "date", "value": ""}
  ]
}
```

**Notes:**
- Test various ambiguous scenarios
- Verify user experience remains smooth

---

### TC-F-003-06: Select Field Option Matching

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify form auto-fill correctly matches document text to predefined select field options, including fuzzy matching.

**Preconditions:**
- Document mentions course type: "intensive course"
- Form has courseType select field with options

**Test Steps:**
1. Load document: "Enrolling in intensive German course"
2. Form has select field with options: ["Intensive", "Evening", "Weekend", "Online"]
3. Send form fill command
4. Verify extracted value matches option exactly

**Expected Results:**
- FormUpdateMessage: `{"courseType": "Intensive"}`
- Fuzzy matching: "intensive course" → "Intensive" (exact option)
- Case-insensitive matching
- Partial match handled: "evening classes" → "Evening"
- If no match found, field left empty with explanation

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Preference: intensive German language course, 20 hours per week",
  "formFields": [
    {
      "id": "courseType",
      "label": "Course Type",
      "type": "select",
      "options": ["Intensive", "Evening", "Weekend", "Online"],
      "value": ""
    }
  ]
}
```

**Notes:**
- Test with all select field types
- Verify spelling variations handled
- Test multiple languages for options

---

### TC-F-003-07: Multiple Documents Merge

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test form auto-fill when multiple documents are selected, verifying data merge without conflicts.

**Preconditions:**
- Multiple documents selected (birth certificate + passport)
- Form has fields covered by both documents
- No conflicting data between documents

**Test Steps:**
1. Select birth certificate (has name and birthDate)
2. Select passport (has passportNumber and passportExpiry)
3. Send "/fillForm" command
4. Verify data from both documents merged

**Expected Results:**
- All non-conflicting fields populated:
  - name: from birth certificate
  - birthDate: from birth certificate
  - passportNumber: from passport
  - passportExpiry: from passport
- No data overwritten incorrectly
- If conflicting data (e.g., different names), agent flags conflict

**Test Data:**
```json
{
  "type": "chat",
  "content": "/fillForm",
  "documentContent": "Document 1:\nName: Ahmad Ali\nBorn: 15.05.1990\n\nDocument 2:\nPassport: P123456789\nExpiry: 20.05.2028",
  "formFields": [
    {"id": "name", "type": "text"},
    {"id": "birthDate", "type": "date"},
    {"id": "passportNumber", "type": "text"},
    {"id": "passportExpiry", "type": "date"}
  ]
}
```

**Notes:**
- Test conflict resolution strategy
- Verify user notified of conflicts

---

## Edge Cases

### TC-F-003-E01: Empty Document with Form Fill Request

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test behavior when user requests form fill with no document selected or empty document.

**Test Steps:**
1. Send "/fillForm" command without document content
2. OR send with empty documentContent: ""
3. Verify appropriate error or guidance message

**Expected Results:**
- Error message: "No document content available to extract data from"
- OR: "Please select a document first"
- No form fields modified
- User guided to next step

---

### TC-F-003-E02: Document with No Relevant Data

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test handling when document doesn't contain data matching any form fields.

**Test Steps:**
1. Load document about course schedule (no personal data)
2. Form expects personal data fields (name, birthDate)
3. Send form fill command
4. Verify graceful handling

**Expected Results:**
- Message: "No relevant data found to fill the form"
- OR: "Could not find: name, date of birth"
- No fields modified with incorrect data
- Confidence scores all low or zero

---

### TC-F-003-E03: Form with No Fields

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Handle edge case where form schema is empty or undefined.

**Test Steps:**
1. Send form fill request with empty formFields: []
2. Verify no error thrown
3. Check response message

**Expected Results:**
- Graceful handling, no crash
- Message: "No form fields available to fill"
- Backend validates form schema exists

---

### TC-F-003-E04: Very Long Form (20+ Fields)

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test performance and accuracy with large forms containing many fields.

**Test Steps:**
1. Create form with 20+ fields
2. Document contains data for 15 of them
3. Send form fill request
4. Measure response time and accuracy

**Expected Results:**
- All matching fields populated correctly
- Response time < 10 seconds
- Fields without matches left empty
- No timeout errors

---

### TC-F-003-E05: Special Characters in Field Values

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify handling of special characters, accents, and symbols in extracted values.

**Test Steps:**
1. Document contains: "Name: François Müller-O'Brien"
2. Extract to name field
3. Verify all characters preserved

**Expected Results:**
- Name extracted exactly: "François Müller-O'Brien"
- Accents preserved: é, ç
- Umlauts preserved: ü
- Hyphens and apostrophes maintained
- No character encoding issues

---

## Error Handling Tests

### TC-F-003-ERR01: Form Parser Tool Failure

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test behavior when form parser tool encounters an error or exception.

**Test Steps:**
1. Simulate form parser exception (mock or inject error)
2. Send form fill request
3. Verify error handling and user notification

**Expected Results:**
- Exception caught gracefully
- Error logged with details
- User message: "Unable to process form fill request. Please try again."
- Application remains stable
- Partial results not applied

---

### TC-F-003-ERR02: Invalid Field Type in Schema

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Handle scenario where form schema contains invalid or unsupported field type.

**Test Steps:**
1. Send form schema with invalid type: `{"id": "test", "type": "unknown"}`
2. Attempt form fill
3. Verify validation catches invalid type

**Expected Results:**
- Validation error logged
- Invalid field skipped
- Other valid fields processed
- Warning returned to frontend

---

### TC-F-003-ERR03: Gemini API Timeout During Extraction

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test handling of API timeout during form data extraction.

**Test Steps:**
1. Send large document with complex form
2. Simulate or trigger Gemini API timeout
3. Verify timeout handling

**Expected Results:**
- Timeout detected (30 second limit)
- User notified: "Request timed out. Please try with a smaller document or fewer fields."
- Partial results not applied
- User can retry

---

## Performance Tests

### TC-F-003-PERF01: Extraction Speed Benchmark

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Measure form extraction performance against requirement: 2000-char document with 7 fields in 5 seconds.

**Test Steps:**
1. Prepare document with exactly 2000 characters
2. Form with 7 fields (mix of text, date, select)
3. Send form fill request and start timer
4. Measure time to FormUpdateMessage received
5. Repeat 10 times, calculate average

**Expected Results:**
- Average extraction time ≤ 5 seconds
- 95th percentile ≤ 7 seconds
- All 7 fields extracted correctly
- Consistency across runs (±1 second variation)

**Test Data:**
- Document: 2000 character birth certificate
- Fields: name, birthDate, placeOfBirth, nationality, passportNumber, passportExpiry, currentAddress

---

### TC-F-003-PERF02: Large Document Handling

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test with documents exceeding typical size (5000+ characters).

**Test Steps:**
1. Create 5000 character document
2. Form with 10 fields
3. Send extraction request
4. Measure performance

**Expected Results:**
- Extraction completes within 10 seconds
- No timeout errors
- Accuracy maintained despite document size
- Memory usage reasonable

---

## Confidence Score Tests

### TC-F-003-CONF01: High Confidence Extraction

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify confidence scores for clear, unambiguous extractions.

**Test Steps:**
1. Document with clear labels: "Full Name: John Doe"
2. Extract to name field
3. Check confidence score in response

**Expected Results:**
- Confidence score > 0.9 for clear match
- High confidence values auto-applied
- Confidence included in FormUpdateMessage

---

### TC-F-003-CONF02: Low Confidence Flag

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test that low confidence extractions are flagged for user review.

**Test Steps:**
1. Document with ambiguous data
2. Extract fields with low confidence
3. Verify user warned about uncertainty

**Expected Results:**
- Confidence score < 0.5 for ambiguous data
- Fields marked for review in UI
- User can accept/reject suggested values

---

## Automated Test Implementation

### Backend Unit Tests (Python/pytest)

**File:** `backend/tests/test_form_parser.py`

```python
import pytest
from backend.tools.form_parser import extract_form_data

def test_extract_simple_name():
    document = "Name: John Doe"
    form_fields = [{"id": "name", "label": "Full Name", "type": "text"}]

    result = extract_form_data(document, form_fields, context="")

    assert "name" in result
    assert result["name"] == "John Doe"

def test_extract_german_date():
    document = "Geburtsdatum: 15.05.1990"
    form_fields = [{"id": "birthDate", "label": "Date of Birth", "type": "date"}]

    result = extract_form_data(document, form_fields, context="")

    assert "birthDate" in result
    assert result["birthDate"] == "1990-05-15"

def test_extract_with_context():
    document = "Student enrolled in intensive course"
    form_fields = [{"id": "courseType", "type": "select", "options": ["Intensive", "Evening"]}]
    context = "Certificates folder expects language proficiency documentation"

    result = extract_form_data(document, form_fields, context)

    assert result["courseType"] == "Intensive"
```

### Frontend Integration Tests (Playwright)

**File:** `tests/e2e/form-autofill.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('Form auto-fill from document', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Select document with birth certificate
  await page.click('text=Birth_Certificate.txt');

  // Open form viewer
  await page.click('[data-testid="form-viewer-tab"]');

  // Trigger auto-fill
  await page.click('[data-testid="ai-chat-toggle"]');
  await page.fill('[data-testid="chat-input"]', '/fillForm');
  await page.click('[data-testid="chat-send"]');

  // Wait for form update
  await page.waitForTimeout(5000);

  // Verify fields populated
  const nameValue = await page.inputValue('[data-field="name"]');
  expect(nameValue).toBe('Ahmad Ali');

  const birthDateValue = await page.inputValue('[data-field="birthDate"]');
  expect(birthDateValue).toBe('1990-05-15');
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 7 | 5 | 2 | 0 |
| Unit | 3 | 1 | 2 | 0 |
| Edge Cases | 5 | 0 | 3 | 1 |
| Error Handling | 3 | 1 | 2 | 0 |
| Performance | 2 | 1 | 1 | 0 |
| Confidence | 2 | 0 | 2 | 0 |
| **Total** | **22** | **8** | **12** | **1** |

---

## Test Execution Checklist

- [ ] Form parser tool implemented and tested
- [ ] Sample documents with various formats prepared
- [ ] Form schemas for all field types created
- [ ] Confidence scoring implemented
- [ ] Date format conversion tested
- [ ] Multilingual extraction verified
- [ ] Performance benchmarks met
- [ ] Error handling comprehensive
- [ ] User experience validated
