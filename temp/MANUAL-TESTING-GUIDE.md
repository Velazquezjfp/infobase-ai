# F-006 Manual Testing Guide

## Prerequisites
- Development server running: `npm run dev`
- Browser open at `http://localhost:5173`
- User logged in

---

## Test 1: Load Document and View Content

**Steps:**
1. Navigate to workspace
2. In Case Tree Explorer, expand "Personal Data" folder
3. Click on "Birth_Certificate.txt"
4. Wait for loading spinner (should be brief)

**Expected Results:**
- ✅ Loading spinner appears briefly on document icon
- ✅ Toast notification: "Document loaded - Birth_Certificate.txt loaded successfully"
- ✅ DocumentViewer shows text content with German characters
- ✅ Content includes: "Ahmad Ali", "15.05.1990", "Kabul"
- ✅ German umlauts (ä, ö, ü, ß) display correctly
- ✅ Text is scrollable if content exceeds viewport

**Screenshot Points:**
- Document tree with txt icons
- Loading spinner during load
- Text content displayed with proper formatting
- German umlauts rendered correctly

---

## Test 2: Load Different Documents

**Steps:**
1. Click on "Passport_Scan.txt" in Personal Data folder
2. Wait for load
3. Click on "Language_Certificate_A1.txt" in Certificates folder
4. Click on "School_Transcripts.txt" in Additional Evidence folder

**Expected Results:**
- ✅ Each document loads successfully
- ✅ Content switches immediately after load
- ✅ Different content for each document
- ✅ No errors in browser console

---

## Test 3: Error Handling - Missing File

**Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click on a document
4. While loading, disable network (offline mode)
5. Click on another document

**Expected Results:**
- ✅ Error toast appears: "Error loading document"
- ✅ Error message describes the issue
- ✅ Document viewer shows previous content or empty state
- ✅ No application crash
- ✅ Console shows error log

---

## Test 4: Case Isolation (If ACTE-2024-002 Available)

**Steps:**
1. Load Birth_Certificate.txt in ACTE-2024-001
2. Verify content displays
3. Click on case switcher in header
4. Select ACTE-2024-002
5. Observe document tree and viewer

**Expected Results:**
- ✅ Document viewer clears when switching cases
- ✅ View mode resets to "form"
- ✅ ACTE-2024-001 documents not visible in tree
- ✅ ACTE-2024-002 documents visible (if exist)
- ✅ No mixing of documents between cases

---

## Test 5: UTF-8 German Characters

**Steps:**
1. Load Birth_Certificate.txt
2. Look for German text sections
3. Check these specific characters:
   - ä (a with umlaut)
   - ö (o with umlaut)
   - ü (u with umlaut)
   - ß (eszett/sharp s)
   - Ä, Ö, Ü (uppercase)

**Expected Results:**
- ✅ All umlauts display correctly (not as ? or �)
- ✅ Text: "Geschlecht / Gender: männlich / male" renders properly
- ✅ Text: "Staatsangehörigkeit" renders properly
- ✅ Select and copy text preserves characters

---

## Test 6: Large Document Loading

**Steps:**
1. Click on School_Transcripts.txt (4.7 KB - largest file)
2. Observe loading time
3. Check if full content displays
4. Scroll through document

**Expected Results:**
- ✅ Loads within 1 second
- ✅ Full 4.7 KB content displays
- ✅ No truncation or "..."
- ✅ Smooth scrolling
- ✅ No browser lag or freeze

---

## Test 7: Multiple Rapid Clicks

**Steps:**
1. Rapidly click between different documents (5-6 clicks in 2 seconds)
2. Wait for loading to stabilize
3. Check which document is displayed

**Expected Results:**
- ✅ Final document shown matches last clicked document
- ✅ No stale content from previous clicks
- ✅ Only one loading spinner at a time
- ✅ No JavaScript errors in console

---

## Test 8: Document Metadata View

**Steps:**
1. Load any document (e.g., Birth_Certificate.txt)
2. Right-click on document in tree
3. Select "View Metadata"

**Expected Results:**
- ✅ Metadata view shows document properties
- ✅ Document type: "txt"
- ✅ CaseId: "ACTE-2024-001"
- ✅ FolderId: "personal-data"
- ✅ Size: "1.8 KB"

---

## Test 9: Browser Console Check

**Steps:**
1. Open Browser DevTools (F12)
2. Go to Console tab
3. Load several documents
4. Check for errors or warnings

**Expected Results:**
- ✅ No TypeScript errors
- ✅ No React warnings
- ✅ Successful load logs: "Document loaded successfully"
- ✅ Network requests to correct paths: `/documents/ACTE-2024-001/...`

---

## Test 10: Network Tab Verification

**Steps:**
1. Open DevTools Network tab
2. Filter for "documents"
3. Click on Birth_Certificate.txt
4. Inspect the network request

**Expected Results:**
- ✅ Request URL: `http://localhost:5173/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
- ✅ Status: 200 OK
- ✅ Content-Type: `text/plain;charset=UTF-8`
- ✅ Response contains full document text
- ✅ No 404 errors

---

## Common Issues and Solutions

### Issue: Document not loading
**Solution:**
- Check file exists at correct path: `public/documents/ACTE-2024-001/...`
- Verify file permissions (should be readable)
- Check browser console for specific error

### Issue: Umlauts display as � or ?
**Solution:**
- Verify file encoding: `file -i filename.txt` should show `charset=utf-8`
- Check browser encoding settings (should be UTF-8)
- Verify HTML meta charset tag

### Issue: Loading spinner never disappears
**Solution:**
- Check network tab for failed requests
- Verify fetch API not blocked by CORS
- Check if promise is resolving

### Issue: Content not displaying
**Solution:**
- Verify `selectedDocument.content` is set
- Check DocumentViewer render conditions
- Inspect React DevTools for state

---

## Performance Benchmarks

| Document | Size | Expected Load Time | Acceptable Max |
|----------|------|-------------------|----------------|
| Birth_Certificate.txt | 1.8 KB | <200ms | 500ms |
| Passport_Scan.txt | 1.9 KB | <200ms | 500ms |
| Language_Certificate_A1.txt | 2.6 KB | <300ms | 700ms |
| Integration_Application.txt | 3.6 KB | <400ms | 1000ms |
| Confirmation_Email.txt | 2.9 KB | <300ms | 800ms |
| School_Transcripts.txt | 4.7 KB | <500ms | 1500ms |

**Measurement:**
- Open DevTools Network tab
- Note timestamp on request start and completion
- Load time = completion - start

---

## Browser Compatibility Checklist

Test in multiple browsers if possible:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

**Expected:** Should work identically in all modern browsers.

---

## Accessibility Check

- [ ] Document names readable by screen reader
- [ ] Loading states announced
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Focus indicators visible

---

## Pass/Fail Criteria

**PASS if:**
- ✅ All 10 tests complete successfully
- ✅ No console errors during testing
- ✅ German characters display correctly
- ✅ Load times within acceptable range
- ✅ Case isolation works

**FAIL if:**
- ❌ Documents don't load
- ❌ Frequent console errors
- ❌ Umlauts display incorrectly
- ❌ Application crashes
- ❌ Cross-case document access possible

---

## Reporting Results

After testing, document:
1. Test results (pass/fail for each test)
2. Screenshots of key features
3. Any issues encountered
4. Browser and OS used
5. Performance measurements

**Report to:** Development team with summary and screenshots

---

## Next Steps After Testing

If all tests pass:
- ✅ Mark F-006 as completed
- ✅ Ready for backend integration (F-001)
- ✅ Ready for form auto-fill (F-003)
- ✅ Can proceed to next requirement

If tests fail:
- ❌ Document specific failures
- ❌ Review implementation
- ❌ Fix issues and retest
