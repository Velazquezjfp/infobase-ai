# F-006: Replace Mock Documents with Text Files (Case-Instance Scoped)

## Test Cases

### TC-F-006-01: Load and Display Birth Certificate from Case Directory

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that clicking on Birth_Certificate.txt in the case tree loads the text content from the case-specific directory and displays it in the DocumentViewer. Documents are stored per-case ensuring complete isolation.

**Preconditions:**
- Birth_Certificate.txt file exists in public/documents/ACTE-2024-001/personal-data/
- File contains realistic German birth certificate text
- documentLoader utility implemented with case-aware path construction
- DocumentViewer updated to display text content

**Test Steps:**
1. Navigate to case ACTE-2024-001
2. Expand Personal Data folder in Case Tree Explorer
3. Click on "Birth_Certificate.txt" document
4. Wait for content to load from case-specific path
5. Check DocumentViewer display
6. Verify path used: `/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`

**Expected Results:**
- Document content loads within 2 seconds
- DocumentViewer shows text content in readable format
- Content includes expected fields: Name, Geburtsdatum, Geburtsort
- Text formatting preserved (line breaks, spacing)
- No "loading..." placeholder after load complete
- Scroll available for long content
- Document loaded from correct case-specific path

**Test Data:**
- File: `/public/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
- Expected content contains: "Ahmad Ali", "15.05.1990", "Kabul"
- Case ID: "ACTE-2024-001"
- Folder ID: "personal-data"

**Notes:**
- Verify UTF-8 encoding for German characters
- Test with realistic document formatting
- Critical test for case-instance isolation

---

### TC-F-006-02: Switch Cases - Document Tree Updates

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that switching between cases updates the document tree to show only the active case's documents, and previously loaded document content is cleared.

**Preconditions:**
- Multiple cases exist: ACTE-2024-001, ACTE-2024-002
- Each case has documents in their respective directories
- Case switching implemented in frontend

**Test Steps:**
1. Load case ACTE-2024-001
2. Verify document tree shows documents from `/documents/ACTE-2024-001/`
3. Select and load a document (e.g., Birth_Certificate.txt)
4. Verify document content displays
5. Switch to case ACTE-2024-002
6. Verify document tree updates to show documents from `/documents/ACTE-2024-002/`
7. Verify DocumentViewer clears previous document
8. Verify ACTE-2024-001 documents NO LONGER visible in tree

**Expected Results:**
- Document tree shows only ACTE-2024-001 documents initially
- After switch, document tree shows only ACTE-2024-002 documents
- ACTE-2024-001 documents not accessible after switch
- Previously loaded document content cleared
- No mix of documents from different cases
- Complete case isolation maintained

**Test Data:**
- Case 1: "ACTE-2024-001"
- Case 2: "ACTE-2024-002"

**Notes:**
- Critical test for case isolation
- Ensures user cannot accidentally access wrong case's documents

---

### TC-F-006-03: Prevent Access to Different Case's Documents

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that attempting to access a document from a different case's directory results in 404 or access denied, maintaining case isolation.

**Preconditions:**
- ACTE-2024-001 is active case
- ACTE-2024-002 directory exists with documents
- Document loader enforces case boundaries

**Test Steps:**
1. Load case ACTE-2024-001
2. Attempt to directly load document from ACTE-2024-002:
   - Try path: `/documents/ACTE-2024-002/personal-data/Birth_Certificate.txt`
3. Verify request fails or is blocked
4. Check error handling

**Expected Results:**
- Access denied or 404 error returned
- Document from ACTE-2024-002 NOT loaded
- Error message: "Document not found" or "Access denied"
- Security: No path traversal or case boundary breach
- User cannot manually construct URL to access other case's documents

**Test Data:**
- Active case: "ACTE-2024-001"
- Attempt to access: "/documents/ACTE-2024-002/personal-data/Birth_Certificate.txt"

**Notes:**
- Security-critical test
- Prevents unauthorized access to other cases
- Validates case isolation at document level

---

### TC-F-006-04: Create New Case - Empty Document Directory

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that creating a new case creates an empty document directory structure ready for document uploads.

**Preconditions:**
- New case creation functionality implemented
- Filesystem write permissions available

**Test Steps:**
1. Create new case: ACTE-2024-004
2. Verify document directory created at `/documents/ACTE-2024-004/`
3. Verify folder subdirectories created (personal-data, certificates, etc.)
4. Load case ACTE-2024-004
5. Verify document tree shows empty folders
6. Verify ready for document uploads

**Expected Results:**
- Directory created: `public/documents/ACTE-2024-004/`
- Subdirectories created for each folder type
- Document tree loads successfully (empty)
- No errors loading empty case
- Case isolated and ready for use

**Test Data:**
- New case ID: "ACTE-2024-004"

**Notes:**
- Tests new case initialization
- Document structure mirrors context structure

---

### TC-F-006-05: AI Chat Receives Case-Specific Document Content

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that when a document is selected from a case-specific directory, the AI receives the full text content with proper case context.

**Preconditions:**
- Document loaded from ACTE-2024-001 directory
- WebSocket connection to AI backend active: ws://localhost:8000/ws/chat/ACTE-2024-001
- Document content passed in chat requests with case and folder IDs

**Test Steps:**
1. Select Birth_Certificate.txt document from ACTE-2024-001/personal-data/
2. Wait for content to load from case-specific path
3. Open AI Chat interface
4. Send message: "Summarize this"
5. Check WebSocket message payload includes caseId and folderId
6. Verify AI response references document content with case context

**Expected Results:**
- WebSocket message includes full document content
- Message structure includes caseId and folderId:
  ```json
  {
    "type": "chat",
    "content": "Summarize this",
    "documentContent": "[full Birth_Certificate.txt content]",
    "caseId": "ACTE-2024-001",
    "folderId": "personal-data"
  }
  ```
- AI response accurately summarizes document
- Summary includes key details from the document
- AI uses case-specific context from ACTE-2024-001
- No truncation of document content

**Test Data:**
- File: `/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
- Case ID: "ACTE-2024-001"
- Folder ID: "personal-data"

**Notes:**
- Monitor WebSocket messages in browser DevTools
- Verify content transmission complete
- Verify case context used in AI response

---

### TC-F-006-06: Large Document Load (5000+ Characters)

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Verify that large documents (5000+ characters) load completely without truncation or performance issues.

**Preconditions:**
- Large text file prepared (5000+ characters)
- documentLoader handles large files
- No artificial size limits

**Test Steps:**
1. Create or select document with 5000+ characters
2. Click on document in tree
3. Start timer
4. Wait for full content load
5. Verify complete content displayed
6. Check for truncation

**Expected Results:**
- Full content loads within 3 seconds
- No truncation or "..." ellipsis
- Complete character count matches file size
- Scrolling smooth and responsive
- Memory usage reasonable
- DocumentViewer handles large text efficiently

**Test Data:**
- Test file: 5000+ character integration application document

**Notes:**
- Test with documents up to 10,000 characters
- Monitor browser memory usage

---

### TC-F-006-07: German Umlauts and Special Characters

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Ensure proper UTF-8 encoding handling for German special characters (ä, ö, ü, ß) in document text.

**Preconditions:**
- Documents contain German text with umlauts
- Files saved with UTF-8 encoding
- Fetch API preserves encoding

**Test Steps:**
1. Load document with German text: "Geburtsurkunde für Ahmad Ali aus Köln"
2. Display in DocumentViewer
3. Verify characters render correctly
4. Send document to AI chat
5. Verify AI receives correct characters

**Expected Results:**
- All umlauts display correctly: ä, ö, ü, ß
- No character replacement with ? or �
- Text remains readable and properly formatted
- AI receives and processes umlauts correctly
- Copy/paste preserves characters

**Test Data:**
- Test string: "Müller, Geburtsdatum, für, Größe, Straße"

**Notes:**
- Verify Content-Type: text/plain;charset=UTF-8
- Test in different browsers

---

### TC-F-006-08: No Race Condition on Rapid Document Clicks

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test that rapidly clicking between documents doesn't cause race conditions or display stale content.

**Preconditions:**
- Multiple documents available in case
- Document loading asynchronous

**Test Steps:**
1. Click Birth_Certificate.txt
2. Immediately click Passport_Scan.txt (before first load completes)
3. Immediately click Language_Certificate_A1.txt
4. Wait for loading to complete
5. Verify displayed content matches last clicked document

**Expected Results:**
- Correct document content displayed (Language_Certificate_A1.txt)
- No stale content from earlier clicks
- Previous requests cancelled or ignored
- Loading indicator shows during load
- No JavaScript errors
- selectedDocument state consistent

**Test Data:**
- 3 different documents for rapid clicking

**Notes:**
- Use AbortController to cancel previous fetch requests
- Verify request cancellation logic

---

### TC-F-006-09: Page Refresh with Document Selected

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify that refreshing the page with a document selected properly reloads the document content.

**Preconditions:**
- Document selection state persisted (if implemented)
- OR: Fresh state after refresh acceptable

**Test Steps:**
1. Select Birth_Certificate.txt
2. Wait for content to load
3. Refresh browser page (F5 or Ctrl+R)
4. Check document state after refresh

**Expected Results:**
- If persistence implemented:
  - Same document re-selected
  - Content reloaded automatically
- If no persistence:
  - No document selected (clean state)
  - No errors on page load
- Application initializes correctly
- User can select document again

**Test Data:**
N/A

**Notes:**
- POC phase: Clean state after refresh acceptable
- Document persistence feature for future sprint

---

### TC-F-006-10: Missing Document File (404 Error)

**Type:** Error Handling
**Priority:** High
**Status:** Pending

**Description:**
Test graceful error handling when document file is missing or unreachable (404 error).

**Preconditions:**
- Document reference in mockData points to non-existent file
- Error handling implemented in documentLoader

**Test Steps:**
1. Click on document with invalid file path
2. Attempt to load content
3. Observe error handling
4. Check user notification

**Expected Results:**
- Fetch 404 error caught gracefully
- Error message displayed: "Failed to load document content"
- OR: "Document file not found"
- Error logged to console with details
- Application remains stable
- User can try other documents
- No blank screen or crash

**Test Data:**
- Invalid file path: `/public/documents/NonExistent.txt`

**Notes:**
- Test various error scenarios: 404, 500, network failure
- Verify user-friendly error messages

---

## Edge Cases

### TC-F-006-E01: Empty Document File

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Handle scenario where document file exists but is empty (0 bytes).

**Test Steps:**
1. Create empty text file
2. Reference in document metadata
3. Click to load
4. Check display

**Expected Results:**
- No error thrown
- Message displayed: "Document is empty" or similar
- OR: Blank document viewer with no content
- User informed appropriately

---

### TC-F-006-E02: Document with Only Whitespace

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Test handling of document containing only spaces, tabs, or newlines.

**Test Steps:**
1. Create document with whitespace only
2. Load document
3. Verify handling

**Expected Results:**
- Document loads without error
- Whitespace preserved or trimmed (consistent behavior)
- OR: Treated as empty document
- No confusion for user

---

### TC-F-006-E03: Document with Special MIME Type

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Test loading documents with different text MIME types.

**Test Steps:**
1. Serve document with text/plain
2. Serve document with text/html
3. Verify correct handling

**Expected Results:**
- text/plain loaded and displayed as-is
- text/html tags not rendered (shown as text)
- No XSS vulnerabilities
- Consistent text display

---

### TC-F-006-E04: Very Long Single Line

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Handle document with extremely long single line (1000+ characters no breaks).

**Test Steps:**
1. Create document with 1000+ char single line
2. Load and display
3. Check UI rendering

**Expected Results:**
- Text wraps appropriately
- Horizontal scroll if needed
- No UI breakage
- Performance acceptable

---

## Performance Tests

### TC-F-006-PERF01: Document Load Time Benchmark

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Measure and benchmark document loading times for various file sizes.

**Test Steps:**
1. Prepare documents: 500 chars, 1000 chars, 2000 chars, 5000 chars
2. Load each document and measure time
3. Repeat 10 times each
4. Calculate averages

**Expected Results:**
- 500 chars: < 200ms average
- 1000 chars: < 300ms average
- 2000 chars: < 500ms average
- 5000 chars: < 1000ms average
- Consistent performance across loads

**Test Data:**
- Small: 500 chars
- Medium: 2000 chars
- Large: 5000 chars

---

### TC-F-006-PERF02: Multiple Sequential Loads

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test performance when loading multiple documents in sequence.

**Test Steps:**
1. Load 10 documents one after another
2. Measure total time
3. Check for memory leaks
4. Monitor performance degradation

**Expected Results:**
- Each load completes in < 1 second
- No significant slowdown over time
- Memory usage stable (no leaks)
- Browser responsive throughout

---

## Integration Tests

### TC-F-006-INT01: Document Path Mapping

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify correct mapping between document metadata and actual file paths.

**Test Steps:**
1. Review mockData document definitions
2. Check filePath property for each document
3. Verify each file exists at specified path
4. Test loading each document

**Expected Results:**
- All documents in mockData have filePath property
- FilePath format: `/documents/Filename.txt`
- All referenced files exist in public/documents/
- No broken links or missing files
- Consistent path structure

**Test Data:**
- All documents in mockData.ts

---

### TC-F-006-INT02: DocumentViewer Content Display

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that DocumentViewer correctly displays loaded text content with proper formatting.

**Test Steps:**
1. Load document with formatted text (paragraphs, lists)
2. Check DocumentViewer rendering
3. Verify text formatting preserved
4. Test scrolling and readability

**Expected Results:**
- Text displayed in pre-formatted or styled container
- Line breaks preserved
- Indentation preserved
- Monospace or readable font
- Adequate padding and spacing
- Scrollbar for long content

**Test Data:**
N/A

---

### TC-F-006-INT03: AI Chat Document Context

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
End-to-end test of document loading and AI chat with document context.

**Test Steps:**
1. Load Birth_Certificate.txt
2. Verify content displays
3. Send AI message: "What is the date of birth?"
4. Verify AI extracts correct information
5. Check response accuracy

**Expected Results:**
- AI receives full document content
- AI correctly identifies date: "15.05.1990"
- Response references document content
- Context maintained throughout conversation

**Test Data:**
- Document: Birth_Certificate.txt
- Expected answer: "15.05.1990" or "May 15, 1990"

---

## Automated Test Implementation

### Frontend Unit Tests (Jest)

**File:** `src/lib/__tests__/documentLoader.test.ts`

```typescript
import { loadDocumentContent } from '../documentLoader';

// Mock fetch
global.fetch = jest.fn();

describe('documentLoader - Case-Instance Scoped', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads document content from case-specific path', async () => {
    const mockContent = 'Birth Certificate: Ahmad Ali';
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(mockContent)
    });

    const content = await loadDocumentContent('ACTE-2024-001', 'personal-data', 'Birth_Certificate.txt');

    expect(content).toBe(mockContent);
    expect(fetch).toHaveBeenCalledWith('/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt');
  });

  it('handles 404 error gracefully for case-specific path', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404
    });

    await expect(loadDocumentContent('ACTE-2024-001', 'personal-data', 'Missing.txt'))
      .rejects.toThrow('Failed to load document');
  });

  it('prevents cross-case document access', async () => {
    // Attempt to load document from different case
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404
    });

    // When ACTE-2024-001 is active, cannot access ACTE-2024-002 documents
    await expect(loadDocumentContent('ACTE-2024-002', 'personal-data', 'Birth_Certificate.txt'))
      .rejects.toThrow('Failed to load document');
  });

  it('handles network errors', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    await expect(loadDocumentContent('ACTE-2024-001', 'personal-data', 'Test.txt'))
      .rejects.toThrow('Network error');
  });

  it('preserves UTF-8 characters in case-specific documents', async () => {
    const germanText = 'Geburtsurkunde für Müller aus Köln';
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(germanText)
    });

    const content = await loadDocumentContent('ACTE-2024-001', 'personal-data', 'German.txt');

    expect(content).toBe(germanText);
    expect(content).toContain('ü');
    expect(content).toContain('ö');
    expect(fetch).toHaveBeenCalledWith('/documents/ACTE-2024-001/personal-data/German.txt');
  });

  it('constructs correct path for different cases', async () => {
    const mockContent = 'Test content';
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(mockContent)
    });

    await loadDocumentContent('ACTE-2024-002', 'certificates', 'Certificate.txt');

    expect(fetch).toHaveBeenCalledWith('/documents/ACTE-2024-002/certificates/Certificate.txt');
  });
});
```

### Integration Tests (Playwright)

**File:** `tests/e2e/document-loading.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('Load and display document text', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Click on Birth Certificate
  await page.click('text=Birth_Certificate.txt');

  // Wait for content to load
  await page.waitForSelector('[data-testid="document-content"]', { timeout: 3000 });

  // Verify content displayed
  const content = await page.textContent('[data-testid="document-content"]');
  expect(content).toContain('Ahmad Ali');
  expect(content).toContain('15.05.1990');
});

test('AI chat with document content', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Load document
  await page.click('text=Birth_Certificate.txt');
  await page.waitForSelector('[data-testid="document-content"]');

  // Open AI chat
  await page.click('[data-testid="ai-chat-toggle"]');

  // Send message
  await page.fill('[data-testid="chat-input"]', 'Summarize this document');
  await page.click('[data-testid="chat-send"]');

  // Wait for AI response
  await page.waitForSelector('[data-testid="ai-response"]', { timeout: 10000 });

  // Verify response references document
  const response = await page.textContent('[data-testid="ai-response"]');
  expect(response).toBeTruthy();
  expect(response.length).toBeGreaterThan(20);
});

test('Handle missing document file', async ({ page }) => {
  // Mock document with invalid path
  await page.goto('http://localhost:5173');

  // Inject document with bad path
  await page.evaluate(() => {
    // Mock document selection with bad path
  });

  // Expect error message
  await page.click('text=Missing_Document.txt');
  await expect(page.locator('text=Failed to load')).toBeVisible({ timeout: 3000 });
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 7 | 5 | 2 | 0 |
| Performance | 2 | 1 | 1 | 0 |
| Error Handling | 1 | 1 | 0 | 0 |
| Edge Cases | 4 | 0 | 1 | 3 |
| Unit | 3 | 0 | 1 | 2 |
| **Total** | **17** | **7** | **5** | **5** |

---

## Test Data Files

### Required Text Files in public/documents/

1. **Birth_Certificate.txt** (500-800 chars)
   - German birth certificate format
   - Contains: Name, Geburtsdatum, Geburtsort, Staatsangehörigkeit
   - Sample: Ahmad Ali, 15.05.1990, Kabul, Afghanistan

2. **Passport_Scan.txt** (400-600 chars)
   - Passport information
   - Contains: Passport number, issue/expiry dates, personal data
   - Sample: P123456789, 20.05.2020 - 20.05.2028

3. **Language_Certificate_A1.txt** (600-1000 chars)
   - Goethe Institut A1 certificate
   - Contains: Institution name, level, student name, dates
   - Sample: Goethe-Institut, Niveau A1, Ahmad Ali, 15.06.2023

4. **Integration_Application.txt** (1000-1500 chars)
   - Partially filled application form
   - Contains: Name, address, course preference
   - Sample: Intensive Course application

5. **School_Transcripts.txt** (1200-2000 chars)
   - Education history
   - Contains: University name, degree, grades, dates
   - Sample: Kabul University records

6. **Confirmation_Email.txt** (300-500 chars)
   - Email from BAMF
   - Contains: From, Subject, Date, confirmation message
   - Sample: Application received confirmation

---

## Test Execution Checklist

- [ ] All 6 text files created in public/documents/
- [ ] Files contain realistic, properly formatted content
- [ ] Files saved with UTF-8 encoding
- [ ] documentLoader utility implemented
- [ ] DocumentViewer updated to display text
- [ ] mockData documents updated with filePath property
- [ ] Error handling for missing files implemented
- [ ] Performance acceptable for all document sizes
- [ ] German characters display correctly
- [ ] AI chat integration working
- [ ] All test cases executed and documented
