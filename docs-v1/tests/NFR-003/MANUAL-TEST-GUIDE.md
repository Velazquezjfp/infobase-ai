# NFR-003: LocalStorage Manual Test Guide

## Overview

This guide provides step-by-step instructions for manually testing the localStorage functionality that cannot be fully automated. These tests verify real browser behavior, user interactions, and visual feedback.

## Prerequisites

- Application running: `npm run dev`
- Browser with DevTools open (F12)
- Clean localStorage state (clear before testing)

## Test Environment Setup

### Clear localStorage before testing

```javascript
// Run in browser console:
for (let key in localStorage) {
  if (key.startsWith('bamf_')) {
    localStorage.removeItem(key);
  }
}
console.log('BAMF storage cleared');
```

---

## Manual Test Cases

### TC-NFR-003-M01: Visual Test Suite (test-localstorage.html)

**Type:** Manual Browser
**Priority:** High
**Estimated Time:** 5 minutes

**Steps:**

1. Open `temp/test-localstorage.html` in browser
2. Click "Run All Tests" button
3. Observe test results displayed on page
4. Verify test summary shows:
   - Total Tests: 7
   - All tests passing (green checkmarks)
   - Success Rate: 100%

**Expected Results:**

- All 7 tests pass
- Storage info displays correctly
- No errors in console

**Actual Results:** (Fill after execution)
- [ ] All tests passed
- [ ] Storage info accurate
- [ ] No console errors

---

### TC-NFR-003-M02: Form Fields Persistence Across Page Refresh

**Type:** Manual Integration
**Priority:** High
**Estimated Time:** 3 minutes

**Steps:**

1. Start application: `npm run dev`
2. Login as any user
3. Navigate to Admin Config Panel (toggle admin mode)
4. Add 3 new form fields:
   - Field 1: Text field "middleName" label "Middle Name"
   - Field 2: Date field "visaExpiry" label "Visa Expiry Date"
   - Field 3: Select field "educationLevel" label "Education Level" with options: ["High School", "Bachelor", "Master", "PhD"]
5. Close admin panel
6. Open browser DevTools → Application tab → Local Storage
7. Verify key `bamf_form_fields` exists
8. Check JSON content includes new fields
9. Refresh page (F5)
10. Login again and check Form Viewer
11. Verify all 3 new fields are present

**Expected Results:**

- Fields immediately saved to localStorage
- JSON structure valid in DevTools
- After refresh, all fields restored
- Field properties preserved (type, label, options)
- No data loss

**Actual Results:** (Fill after execution)
- [ ] Fields saved immediately
- [ ] JSON valid
- [ ] Fields restored after refresh
- [ ] Properties preserved

---

### TC-NFR-003-M03: Case Form Data Isolation

**Type:** Manual Integration
**Priority:** High
**Estimated Time:** 4 minutes

**Steps:**

1. Open application, login
2. On Case ACTE-2024-001, fill form:
   - Full Name: "Ahmad Ali"
   - Birth Date: "1990-05-15"
   - Country: "Afghanistan"
3. Switch to Case ACTE-2024-002 (use search)
4. Fill form with different data:
   - Full Name: "Maria Schmidt"
   - Birth Date: "1985-03-20"
   - Country: "Germany"
5. Open DevTools → Local Storage
6. Inspect `bamf_case_form_data`
7. Verify both cases have separate data
8. Switch back to ACTE-2024-001
9. Verify original data ("Ahmad Ali") still there

**Expected Results:**

- Each case maintains separate form data
- Switching cases loads correct data
- No cross-contamination between cases
- Data persists across case switches

**Actual Results:** (Fill after execution)
- [ ] Separate data maintained
- [ ] Correct data loaded on switch
- [ ] No cross-contamination
- [ ] Data persists

---

### TC-NFR-003-M04: Storage Quota Warning

**Type:** Manual Edge Case
**Priority:** Medium
**Estimated Time:** 2 minutes

**Note:** This test artificially fills localStorage to trigger warnings.

**Steps:**

1. Open browser console
2. Run this script to fill storage:

```javascript
// Fill localStorage to ~4.6MB (approaching limit)
const largeData = 'x'.repeat(500000); // 500KB per field
for (let i = 0; i < 9; i++) {
  localStorage.setItem(`bamf_large_test_${i}`, largeData);
}
console.log('Storage filled to', ((localStorage.length * 500000 * 2) / (1024 * 1024)).toFixed(2), 'MB');
```

3. In the app, try to add a new form field
4. Observe toast notification for warning

**Expected Results:**

- Warning toast appears: "Storage usage is high (XX%)"
- Save still succeeds (under critical threshold)
- User warned to clear data

**Actual Results:** (Fill after execution)
- [ ] Warning toast displayed
- [ ] Save succeeded
- [ ] User notified

**Cleanup:**

```javascript
for (let i = 0; i < 9; i++) {
  localStorage.removeItem(`bamf_large_test_${i}`);
}
```

---

### TC-NFR-003-M05: Malformed JSON Recovery

**Type:** Manual Integration
**Priority:** High
**Estimated Time:** 2 minutes

**Steps:**

1. Open browser console
2. Manually corrupt localStorage:

```javascript
localStorage.setItem('bamf_form_fields', '{this is: invalid json}');
console.log('Corrupted data inserted');
```

3. Refresh page
4. Observe console for error messages
5. Check if app loads with default form fields
6. Verify app remains functional

**Expected Results:**

- Console shows error: "Malformed JSON in localStorage..."
- Console shows: "Clearing corrupted data..."
- App loads with default initialFormFields
- User can continue working normally
- Corrupted key auto-removed from localStorage

**Actual Results:** (Fill after execution)
- [ ] Error logged
- [ ] Corrupted data cleared
- [ ] Defaults loaded
- [ ] App functional

---

### TC-NFR-003-M06: Multi-Tab Behavior (No Real-Time Sync)

**Type:** Manual Integration
**Priority:** Low
**Estimated Time:** 3 minutes

**Steps:**

1. Open application in Tab 1
2. Open application in Tab 2 (new tab, same URL)
3. In Tab 1: Add new form field "testField"
4. Wait 5 seconds
5. In Tab 2: Check if "testField" appears (it should NOT)
6. In Tab 2: Refresh page (F5)
7. Check if "testField" appears now (it SHOULD)

**Expected Results:**

- Tab 2 does NOT see changes from Tab 1 automatically
- After refresh, Tab 2 loads latest from localStorage
- Last write wins (POC limitation documented)
- No errors or conflicts

**Actual Results:** (Fill after execution)
- [ ] No automatic sync
- [ ] Refresh loads latest
- [ ] Last write wins
- [ ] No errors

**Note:** This is a known POC limitation. Real-time sync would require storage event listeners (future enhancement).

---

### TC-NFR-003-M07: Export/Import Backup

**Type:** Manual Integration
**Priority:** Medium
**Estimated Time:** 3 minutes

**Steps:**

1. In browser console, check current BAMF data:

```javascript
// View all BAMF keys
for (let key in localStorage) {
  if (key.startsWith('bamf_')) {
    console.log(key, ':', localStorage.getItem(key).substring(0, 100));
  }
}
```

2. Test export (from app or console):

```javascript
// Export all BAMF data
const backup = {};
for (let key in localStorage) {
  if (key.startsWith('bamf_')) {
    backup[key] = localStorage.getItem(key);
  }
}
const exported = JSON.stringify(backup, null, 2);
console.log('Backup created:', exported.substring(0, 200));
// Copy to clipboard
copy(exported);
```

3. Clear BAMF storage:

```javascript
for (let key in localStorage) {
  if (key.startsWith('bamf_')) {
    localStorage.removeItem(key);
  }
}
console.log('Storage cleared');
```

4. Verify app shows defaults after refresh

5. Import backup:

```javascript
// Paste your exported data here
const imported = `{paste your backup JSON here}`;
const data = JSON.parse(imported);
for (let key in data) {
  localStorage.setItem(key, data[key]);
}
console.log('Backup restored');
```

6. Refresh page and verify data restored

**Expected Results:**

- Export creates valid JSON backup
- Clear removes all BAMF data
- App works with defaults after clear
- Import restores all data
- After import + refresh, all data back

**Actual Results:** (Fill after execution)
- [ ] Export successful
- [ ] Clear successful
- [ ] Defaults work
- [ ] Import successful
- [ ] Data restored

---

### TC-NFR-003-M08: Console Diagnostic Test

**Type:** Manual Diagnostic
**Priority:** Medium
**Estimated Time:** 2 minutes

**Steps:**

1. Open application in browser
2. Login and interact with forms (fill some data)
3. Open browser console
4. Copy contents of `temp/test-console.js`
5. Paste into console and press Enter
6. Review the diagnostic output

**Expected Output:**

```
=== TEST 1: Check BAMF localStorage Keys ===
Found 2 BAMF keys: [ 'bamf_form_fields', 'bamf_case_form_data' ]

=== TEST 2: View Form Fields ===
Form fields count: 7
Form fields: [Array of FormField objects]

=== TEST 3: View Case Form Data ===
Cases with form data: 3
Case IDs: [ 'ACTE-2024-001', 'ACTE-2024-002', 'ACTE-2024-003' ]

=== TEST 4: Storage Usage ===
Total Storage: XX.XX KB (X.XX MB)
BAMF Storage: XX.XX KB
Usage: X.X% of ~5MB limit
✅ Storage usage is healthy

=== TEST 5: Data Integrity Check ===
✅ Form fields structure valid
✅ Case form data structure valid
✅ All data integrity checks passed!
```

**Expected Results:**

- All BAMF keys listed
- Form fields and case data displayed
- Storage usage calculated correctly
- All integrity checks pass
- No corruption errors

**Actual Results:** (Fill after execution)
- [ ] Keys listed
- [ ] Data displayed
- [ ] Usage calculated
- [ ] Integrity checks pass

---

## Test Execution Checklist

After completing all manual tests, verify:

- [ ] All automated tests passed (8/8)
- [ ] Visual test suite passed (7/7)
- [ ] Form fields persist across refresh
- [ ] Case form data isolated per case
- [ ] Storage quota warnings work
- [ ] Malformed JSON handled gracefully
- [ ] Multi-tab behavior documented
- [ ] Export/import functionality works
- [ ] Console diagnostics show healthy state

## Known Limitations (POC Phase)

1. **No Real-Time Sync:** Changes in one browser tab do not automatically appear in other tabs
2. **No Backend Storage:** All data stored in browser localStorage only
3. **5MB Limit:** Browser localStorage typical limit of 5-10MB
4. **No Encryption:** Data stored in plain text (not sensitive for POC)

## Troubleshooting

### Issue: Tests fail due to localStorage unavailable

**Solution:**
- Check if browser is in private/incognito mode
- Ensure JavaScript is enabled
- Try different browser (Chrome, Firefox, Edge)

### Issue: Quota exceeded errors

**Solution:**
```javascript
// Clear all BAMF storage
for (let key in localStorage) {
  if (key.startsWith('bamf_')) {
    localStorage.removeItem(key);
  }
}
```

### Issue: Corrupted data in localStorage

**Solution:**
```javascript
// Force clear corrupted key
localStorage.removeItem('bamf_form_fields');
localStorage.removeItem('bamf_case_form_data');
// Refresh page to load defaults
location.reload();
```

## Reporting Results

After completing manual tests, document results in:
- `docs/tests/NFR-003/test-results.json` (automated tests already captured)
- `docs/tests/NFR-003/manual-test-results.md` (create for manual tests)

Include:
- Test ID and name
- Pass/Fail status
- Observed behavior
- Screenshots if relevant
- Any deviations from expected results
