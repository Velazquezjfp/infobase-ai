# F-004: AI-Powered Form Field Generator - Admin Interface (Case-Aware)

## Test Cases

### TC-F-004-01: Generate Simple Text Field

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that the AI field generator can create a basic text field from a natural language description.

**Preconditions:**
- Admin Config Panel accessible
- AI Fields tab implemented
- Backend field generation endpoint running at POST /api/admin/generate-field
- Gemini API configured

**Test Steps:**
1. Navigate to Admin Config Panel
2. Click on "AI Fields" tab (6th tab)
3. Enter prompt: "Add text field for passport number"
4. Click "Generate Field" button
5. Wait for preview to appear
6. Verify field structure in preview

**Expected Results:**
- Preview shows within 5 seconds
- Field structure:
  - type: "text"
  - label: "Passport Number"
  - id: auto-generated (e.g., "passportNumber")
  - required: false (default)
  - value: ""
- Field properties editable in preview
- "Add to Form" button available

**Test Data:**
```json
{
  "prompt": "Add text field for passport number"
}
```

**Notes:**
- Verify label is user-friendly (capitalized, spaced)
- Check ID follows camelCase convention

---

### TC-F-004-02: Generate Required Date Field

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test generation of a required date field, verifying the AI understands the "required" constraint.

**Preconditions:**
- AI Fields tab open
- Field generator service ready

**Test Steps:**
1. Enter prompt in textarea: "Add required date field for visa expiry"
2. Click Generate button
3. Examine preview
4. Verify "required" property set to true

**Expected Results:**
- Preview displays:
  - type: "date"
  - label: "Visa Expiry" or "Visa Expiry Date"
  - id: "visaExpiry" or "visaExpiryDate"
  - required: true (explicitly set)
- Date field validation rules suggested (if applicable)
- Preview highlights required status visually (asterisk or indicator)

**Test Data:**
```json
{
  "prompt": "Add required date field for visa expiry"
}
```

**Notes:**
- Test keyword recognition: "required", "mandatory", "must have"
- Verify required indicator in UI

---

### TC-F-004-03: Generate Select Field with Options

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Validate generation of a select dropdown field with explicitly listed options.

**Preconditions:**
- AI Fields tab accessible
- Field generator handles select type

**Test Steps:**
1. Enter prompt: "Add dropdown for marital status: single, married, divorced, widowed"
2. Submit generation request
3. Review generated field structure
4. Verify options array

**Expected Results:**
- Field preview shows:
  - type: "select"
  - label: "Marital Status"
  - id: "maritalStatus"
  - options: ["single", "married", "divorced", "widowed"]
  - options array length: 4
  - options capitalized consistently
- Default value handling (empty or first option)

**Test Data:**
```json
{
  "prompt": "Add dropdown for marital status: single, married, divorced, widowed"
}
```

**Notes:**
- Test with different option delimiters: commas, semicolons, "or"
- Verify option order preserved

---

### TC-F-004-04: Generate Field from German Prompt

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Ensure the field generator works with German language prompts, creating appropriate English field structure.

**Preconditions:**
- Multilingual support in Gemini service
- German language context available

**Test Steps:**
1. Enter German prompt: "Füge Textfeld für Reisepassnummer hinzu"
2. Generate field
3. Verify English field structure created
4. Check label language (should be English or configurable)

**Expected Results:**
- Field generated successfully from German prompt
- Field structure in English:
  - type: "text"
  - label: "Passport Number" (English)
  - id: "passportNumber"
- OR label in German if locale configured: "Reisepassnummer"
- Prompt language doesn't prevent generation

**Test Data:**
```json
{
  "prompt": "Füge Textfeld für Reisepassnummer hinzu"
}
```

**Notes:**
- Test with both German and English labels
- Verify umlauts handled correctly
- Test mixed language prompts

---

### TC-F-004-05: Ambiguous Request Clarification

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test agent behavior when field request is ambiguous or lacks necessary details.

**Preconditions:**
- Field generator includes validation logic
- Clarification mechanism implemented

**Test Steps:**
1. Enter vague prompt: "add field for details"
2. Submit request
3. Observe response
4. Check for clarification request

**Expected Results:**
- Response asks for clarification: "What type of field would you like? (text, date, select, etc.)"
- OR: "What details should this field capture?"
- No field generated until clarification provided
- User can provide additional input
- Conversation continues until sufficient info gathered

**Test Data:**
```json
{
  "prompt": "add field for details"
}
```

**Notes:**
- Test multiple ambiguous scenarios
- Verify user experience remains smooth

---

### TC-F-004-06: Edit Generated Field Before Adding

**Type:** E2E
**Priority:** High
**Status:** Pending

**Description:**
Verify admin can edit generated field properties in preview before adding to form.

**Preconditions:**
- Field generated and displayed in preview
- Preview interface allows editing

**Test Steps:**
1. Generate field: "Add text field for middle name"
2. Preview shows label "Middle Name"
3. Edit label in preview to "Middle Name (Optional)"
4. Change required from false to true
5. Click "Add to Form" button
6. Verify edited values saved

**Expected Results:**
- All field properties editable in preview:
  - label (text input)
  - id (text input, with validation)
  - required (checkbox)
  - options (for select fields)
- Changes immediately reflected in preview
- "Add to Form" button adds edited version
- FormFields in AppContext contains edited values

**Test Data:**
N/A (manual interaction)

**Notes:**
- Validate ID uniqueness when editing
- Preserve edits if user regenerates

---

### TC-F-004-07: Field Persistence to LocalStorage

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that generated and added fields persist to localStorage and survive page refresh.

**Preconditions:**
- LocalStorage utility implemented
- FormFields synced to localStorage

**Test Steps:**
1. Generate and add new field: "Add email field"
2. Verify field added to formFields in AppContext
3. Check localStorage key "bamf_form_fields"
4. Refresh browser page
5. Navigate to Admin Config Panel, Forms tab
6. Verify generated field still present

**Expected Results:**
- Field immediately saved to localStorage after adding
- localStorage contains serialized FormField array
- After refresh, field loads from localStorage
- Field appears in Forms tab field list
- Field functional in Form Viewer

**Test Data:**
```json
{
  "prompt": "Add email field"
}
```

**Notes:**
- Test localStorage quota not exceeded
- Verify JSON serialization correct

---

### TC-F-004-08: JSON-LD Semantic Metadata

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify generated fields include JSON-LD semantic metadata for enhanced document parsing.

**Preconditions:**
- FormFieldSpec includes metadata property
- Field generator produces semantic annotations

**Test Steps:**
1. Generate field: "Add date field for birth date"
2. Inspect generated field object
3. Verify metadata property exists
4. Check JSON-LD structure

**Expected Results:**
- Field includes metadata object:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "Person",
    "semanticType": "birthDate"
  }
  ```
- Metadata helps document parser identify field type
- Common fields have standardized @type values
- Custom fields get generic type

**Test Data:**
N/A

**Notes:**
- Verify schema.org compliance
- Test metadata usage in form parser

---

## Edge Cases

### TC-F-004-E01: Generate Field with Special Characters

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Test field generation with prompts containing special characters.

**Test Steps:**
1. Enter prompt: "Add field for mother's maiden name"
2. Generate field
3. Verify apostrophe handled correctly

**Expected Results:**
- Label preserves apostrophe: "Mother's Maiden Name"
- ID removes special chars: "mothersMaidenName"
- No parsing errors

---

### TC-F-004-E02: Very Long Field Label

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Test handling of prompts resulting in very long labels.

**Test Steps:**
1. Enter prompt: "Add text field for detailed description of applicant's complete educational background and professional qualifications"
2. Generate field
3. Check label length

**Expected Results:**
- Label truncated or abbreviated if too long (>50 chars)
- OR: Full label preserved with ellipsis in UI
- ID remains reasonable length (<30 chars)
- Validation suggests shorter label

---

### TC-F-004-E03: Duplicate Field Request

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Handle request to generate field that already exists.

**Test Steps:**
1. Form already has "name" field
2. Request: "Add text field for name"
3. Generate field
4. Check for duplicate detection

**Expected Results:**
- Warning: "A field with ID 'name' already exists"
- User can choose to:
  - Cancel
  - Generate with different ID
  - Replace existing field
- No accidental duplication

---

### TC-F-004-E04: Empty or Whitespace Prompt

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Validate input when prompt is empty or contains only whitespace.

**Test Steps:**
1. Leave prompt textarea empty
2. Click Generate button
3. OR enter only spaces/newlines

**Expected Results:**
- Validation error: "Please enter a field description"
- Generate button disabled for empty input
- No API call made
- User guided to provide input

---

## Error Handling Tests

### TC-F-004-ERR01: Backend Service Unavailable

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test frontend handling when backend field generator endpoint is unreachable.

**Test Steps:**
1. Stop backend server
2. Attempt to generate field
3. Observe error handling
4. Restart server and retry

**Expected Results:**
- Error detected and caught
- User message: "Unable to connect to field generator service. Please try again later."
- No application crash
- Retry button or guidance provided
- Error logged for debugging

---

### TC-F-004-ERR02: Gemini API Error

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Handle errors from Gemini API during field generation.

**Test Steps:**
1. Trigger Gemini API error (invalid API key, rate limit, etc.)
2. Attempt field generation
3. Verify error handling

**Expected Results:**
- Error caught in backend
- User-friendly message returned: "Field generation temporarily unavailable"
- Backend logs detailed error
- User can retry
- No partial/corrupted field created

---

### TC-F-004-ERR03: Invalid Field Specification Returned

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test validation when AI returns invalid or malformed field specification.

**Test Steps:**
1. Mock or inject invalid field spec (missing type, invalid type, etc.)
2. Attempt to add field
3. Verify validation catches errors

**Expected Results:**
- Frontend validation catches invalid spec
- Error: "Generated field is invalid. Please try again."
- No invalid field added to formFields
- Detailed validation error logged

---

## Performance Tests

### TC-F-004-PERF01: Field Generation Response Time

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Measure field generation performance to ensure acceptable user experience.

**Test Steps:**
1. Submit field generation request
2. Start timer
3. Wait for preview display
4. Record time
5. Repeat 10 times with various prompts

**Expected Results:**
- Average generation time < 3 seconds
- 95th percentile < 5 seconds
- Loading indicator shown during generation
- User experience feels responsive

---

### TC-F-004-PERF02: Multiple Rapid Generations

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Test system behavior when user generates multiple fields in quick succession.

**Test Steps:**
1. Generate 5 fields rapidly (one after another)
2. Monitor response times and success rate
3. Check for rate limiting or throttling

**Expected Results:**
- All requests complete successfully
- No significant performance degradation
- Rate limiting handled gracefully if implemented
- UI remains responsive

---

## Usability Tests

### TC-F-004-UI01: Kolibri Component Integration

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Verify Kolibri UI components used in AI Fields tab are correctly integrated and styled.

**Test Steps:**
1. Navigate to AI Fields tab
2. Inspect textarea component
3. Check button components
4. Verify consistent styling

**Expected Results:**
- Kolibri textarea component renders correctly
- Consistent with rest of admin panel design
- Accessible (keyboard navigation, screen reader support)
- Responsive on different screen sizes

---

### TC-F-004-UI02: Field Preview Display

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Verify field preview is clear, informative, and matches actual form rendering.

**Test Steps:**
1. Generate various field types
2. Review preview display for each
3. Compare with actual form rendering

**Expected Results:**
- Preview accurately represents final field
- All properties clearly displayed
- Visual distinction between field types
- Edit controls intuitive

---

## Automated Test Implementation

### Backend Unit Tests (Python/pytest)

**File:** `backend/tests/test_field_generator.py`

```python
import pytest
from backend.services.field_generator import parse_field_request

def test_generate_text_field():
    prompt = "Add text field for passport number"
    result = parse_field_request(prompt)

    assert result["type"] == "text"
    assert "Passport" in result["label"]
    assert "passport" in result["id"].lower()
    assert result["required"] == False

def test_generate_required_date_field():
    prompt = "Add required date field for visa expiry"
    result = parse_field_request(prompt)

    assert result["type"] == "date"
    assert result["required"] == True
    assert "visa" in result["id"].lower()

def test_generate_select_field_with_options():
    prompt = "Add dropdown for marital status: single, married, divorced"
    result = parse_field_request(prompt)

    assert result["type"] == "select"
    assert len(result["options"]) == 3
    assert "single" in result["options"]
    assert "married" in result["options"]

def test_json_ld_metadata():
    prompt = "Add date field for birth date"
    result = parse_field_request(prompt)

    assert "metadata" in result
    assert "@context" in result["metadata"]
    assert "@type" in result["metadata"]
```

### Frontend Integration Tests (Playwright)

**File:** `tests/e2e/ai-field-generator.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('Generate field via AI', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Open admin panel
  await page.click('[data-testid="admin-panel-toggle"]');

  // Navigate to AI Fields tab
  await page.click('text=AI Fields');

  // Enter prompt
  await page.fill('[data-testid="field-prompt"]', 'Add text field for email address');

  // Generate
  await page.click('text=Generate Field');

  // Wait for preview
  await page.waitForSelector('[data-testid="field-preview"]', { timeout: 5000 });

  // Verify preview content
  const label = await page.textContent('[data-testid="preview-label"]');
  expect(label).toContain('Email');

  const type = await page.textContent('[data-testid="preview-type"]');
  expect(type).toBe('text');

  // Add to form
  await page.click('text=Add to Form');

  // Verify added
  await page.click('text=Forms');
  const fields = await page.$$('[data-testid="form-field-item"]');
  expect(fields.length).toBeGreaterThan(0);
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 8 | 5 | 3 | 0 |
| Unit | 2 | 0 | 1 | 1 |
| E2E | 1 | 1 | 0 | 0 |
| Edge Cases | 4 | 0 | 1 | 2 |
| Error Handling | 3 | 2 | 1 | 0 |
| Performance | 2 | 0 | 1 | 1 |
| Usability | 2 | 0 | 2 | 0 |
| **Total** | **22** | **8** | **9** | **4** |

---

## Test Execution Checklist

- [ ] AI Fields tab implemented in AdminConfigPanel
- [ ] Backend field generator endpoint functional
- [ ] Kolibri components integrated
- [ ] Field preview interface complete
- [ ] LocalStorage persistence working
- [ ] JSON-LD metadata generation implemented
- [ ] Multilingual support tested
- [ ] Error handling comprehensive
- [ ] Performance benchmarks met
- [ ] Usability validated with real users
