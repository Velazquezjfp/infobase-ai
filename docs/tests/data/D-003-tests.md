# D-003: Sample Document Text Content (Case-Instance Scoped)

## Test Cases

### TC-D-003-01: Birth Certificate Content in Case Directory

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify Birth_Certificate.txt contains required information and is properly formatted for German birth certificate. Documents are stored in case-specific directories for complete isolation.

**Preconditions:**
- Birth_Certificate.txt created in public/documents/ACTE-2024-001/personal-data/
- File accessible via HTTP with case-specific path
- Document stored per-case for isolation

**Test Steps:**
1. Load Birth_Certificate.txt from `/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
2. Verify file loads successfully from case-specific path
3. Check content contains:
   - Name: Ahmad Ali (or specified name)
   - Date: 15.05.1990 (or birthdate)
   - German keywords: "Geburtsurkunde", "Geboren", "Geburtsort"
4. Verify realistic formatting (not just comma-separated values)
5. Check character count (300-2000 range per spec)

**Expected Results:**
- File loads without 404 error from case-specific path
- Content includes "Ahmad Ali"
- Content includes "15.05.1990"
- Content includes "Kabul" (place of birth)
- German text present (Geburtsurkunde, Geboren, etc.)
- Character count: 300-800 characters (realistic length)
- Text formatted like actual certificate (not just data dump)

**Test Data:**
File: `public/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
Case ID: ACTE-2024-001
Folder ID: personal-data
Expected name: Ahmad Ali
Expected date: 15.05.1990
Expected location: Kabul, Afghanistan

**Notes:**
- German birth certificates follow specific format
- Should look realistic for AI testing
- Include typical sections: personal data, issuing authority, stamp/seal text
- Document isolated to specific case directory

---

### TC-D-003-02: Case Switching - Document Isolation

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that documents are isolated per case - switching cases shows different documents, and attempting to access another case's documents fails.

**Preconditions:**
- Multiple cases exist: ACTE-2024-001, ACTE-2024-002
- Each case has documents in their respective directories
- Document loader enforces case boundaries

**Test Steps:**
1. Load documents from ACTE-2024-001
2. Verify documents accessible from `/documents/ACTE-2024-001/`
3. Switch to ACTE-2024-002
4. Verify ACTE-2024-001 documents NOT accessible
5. Verify ACTE-2024-002 documents accessible
6. Attempt to load document from wrong case path
7. Verify 404 or access denied

**Expected Results:**
- ACTE-2024-001 documents only accessible when that case active
- ACTE-2024-002 documents only accessible when that case active
- Cross-case document access prevented
- 404 error when attempting unauthorized access
- Complete case isolation maintained

**Test Data:**
- Case 1: ACTE-2024-001
- Case 2: ACTE-2024-002
- Attempt unauthorized path: `/documents/ACTE-2024-002/personal-data/Birth_Certificate.txt` while ACTE-2024-001 active

**Notes:**
- Critical security test
- Ensures data privacy between cases

---

### TC-D-003-03: Passport Information in Case Directory

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify Passport_Scan.txt contains passport details matching birth certificate identity, stored in case-specific directory.

**Preconditions:**
- Passport_Scan.txt exists in public/documents/ACTE-2024-001/personal-data/
- Content should match person in birth certificate

**Test Steps:**
1. Load Passport_Scan.txt from case-specific path
2. Verify contains passport number: P123456789
3. Check issue date: 20.05.2020
4. Check expiry date: 20.05.2028
5. Verify name matches birth certificate: AHMAD ALI (passport format: uppercase)
6. Check character count within range

**Expected Results:**
- Passport number: P123456789 present
- Issue date: 20.05.2020
- Expiry date: 20.05.2028 (8 years validity)
- Name: AHMAD ALI (uppercase passport format)
- Dates valid (issue before expiry)
- Character count: 400-600 characters
- Formatted like passport text extraction

**Test Data:**
File: `public/documents/ACTE-2024-001/personal-data/Passport_Scan.txt`
Case ID: ACTE-2024-001
Folder ID: personal-data

**Notes:**
- Passport typically uppercase for name
- Should include nationality, passport type
- Format like OCR text extraction from passport scan
- Document isolated to case directory

---

### TC-D-003-03: Language Certificate A1 Level Verification

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test Language_Certificate_A1.txt content and verify AI correctly identifies the CEFR level.

**Preconditions:**
- Language_Certificate_A1.txt created
- AI chat integration functional

**Test Steps:**
1. Load Language_Certificate_A1.txt
2. Verify content mentions "A1" level
3. Verify mentions "Goethe-Institut" or similar recognized institution
4. Verify student name: Ahmad Ali
5. Verify issue date: 15.06.2023
6. Send to AI: "What level is this certificate?"
7. Verify AI response mentions "A1"

**Expected Results:**
- File contains "A1" or "Niveau A1"
- Institution: Goethe-Institut (or telc, TestDaF, etc.)
- Student name: Ahmad Ali
- Issue date: 15.06.2023
- AI correctly identifies: "This is an A1 level certificate"
- Character count: 600-1000 characters

**Test Data:**
File: `public/documents/Language_Certificate_A1.txt`
Expected level: A1 (beginner)
Expected institution: Goethe-Institut

**Notes:**
- CEFR level A1 is beginner level German
- Goethe-Institut is recognized standard
- Certificate should look professional and complete

---

### TC-D-003-04: Form Auto-Fill from Birth Certificate

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
End-to-end test of loading birth certificate and using it for form auto-fill.

**Preconditions:**
- Birth_Certificate.txt contains extractable data
- Form auto-fill feature implemented
- Personal Data form available

**Test Steps:**
1. Load Birth_Certificate.txt in document viewer
2. Send AI command: "/fillForm"
3. Wait for FormUpdateMessage
4. Verify extracted fields:
   - name: "Ahmad Ali"
   - birthDate: "1990-05-15" (ISO format converted from German)
5. Check other extractable fields

**Expected Results:**
- Name extracted correctly: "Ahmad Ali"
- Birth date extracted and converted: "1990-05-15"
- Place of birth extracted if present: "Kabul"
- Nationality extracted if present: "Afghanistan"
- Data clean and usable (no extra formatting)
- No extraction errors

**Test Data:**
Document: Birth_Certificate.txt
Form: Personal Data form

**Notes:**
- Tests real-world document-to-form workflow
- Date format conversion important (German → ISO)

---

### TC-D-003-05: UTF-8 Encoding Validation

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify all text files properly preserve UTF-8 encoding for German special characters.

**Preconditions:**
- All 6 document files created
- Files saved with UTF-8 encoding

**Test Steps:**
1. Load each document file
2. Search for German special characters:
   - ä (a-umlaut)
   - ö (o-umlaut)
   - ü (u-umlaut)
   - ß (eszett/sharp s)
3. Verify characters display correctly (not replaced with ?)
4. Test in browser and backend
5. Check file encoding metadata

**Expected Results:**
- All files encoded as UTF-8
- German characters preserved: ä, ö, ü, ß
- No character replacement or corruption
- Characters display correctly in:
  - DocumentViewer (frontend)
  - AI chat responses
  - Console logs
- No encoding errors when loading

**Test Data:**
Test strings to find:
- "für" (for)
- "Geburtsurkunde" (birth certificate)
- "Müller" (common surname)
- "Größe" (height/size)
- "Straße" (street)

**Notes:**
- Critical for German language support
- Files must be saved with UTF-8 encoding in editor
- Check Content-Type header when serving: text/plain;charset=UTF-8

---

### TC-D-003-06: File Size Validation

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify all document files are within specified size range (300-2000 characters).

**Preconditions:**
- All 6 document files created

**Test Steps:**
1. Check file size for each document:
   - Birth_Certificate.txt
   - Passport_Scan.txt
   - Language_Certificate_A1.txt
   - Integration_Application.txt
   - School_Transcripts.txt
   - Confirmation_Email.txt
2. Count characters (not bytes)
3. Verify each within 300-2000 range
4. Check total size reasonable

**Expected Results:**
- Birth_Certificate.txt: 500-800 chars
- Passport_Scan.txt: 400-600 chars
- Language_Certificate_A1.txt: 600-1000 chars
- Integration_Application.txt: 1000-1500 chars
- School_Transcripts.txt: 1200-2000 chars
- Confirmation_Email.txt: 300-500 chars
- All within specified range
- None too short (< 300) or too long (> 2000)

**Test Data:**
Target range: 300-2000 characters per file

**Notes:**
- Realistic size for sample documents
- Large enough for AI to extract data
- Small enough for quick loading

---

### TC-D-003-07: Document German Umlauts Rendering

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Visual test that German umlauts display correctly in DocumentViewer interface.

**Preconditions:**
- Documents loaded in application
- DocumentViewer component rendering text

**Test Steps:**
1. Open application
2. Navigate to Birth_Certificate.txt
3. View in DocumentViewer
4. Visually inspect German characters:
   - ä should appear as ä (not a, ?, or �)
   - ö should appear as ö
   - ü should appear as ü
   - ß should appear as ß
5. Repeat for other documents with German text
6. Test in different browsers

**Expected Results:**
- All umlauts render correctly
- No character corruption visible
- Font supports German characters
- Consistent across all documents
- Works in Chrome, Firefox, Safari
- Copy/paste preserves characters

**Test Data:**
Look for: Geburtsurkunde, für, Größe, Straße, Müller

**Notes:**
- Visual quality check
- Test in target browsers
- Font choice may affect display

---

## Content Quality Tests

### TC-D-003-QUAL01: Realistic Formatting

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Review document formatting for realism and usability in AI testing.

**Test Steps:**
1. Read each document file
2. Assess formatting realism:
   - Does it look like actual document text?
   - Are sections/labels clear?
   - Is data presented logically?
3. Compare with real document examples
4. Test with AI extraction

**Expected Results:**
- Documents formatted realistically
- Not just comma-separated data
- Include section headers/labels
- Natural language where appropriate
- AI can understand and extract data
- Useful for testing

**Notes:**
- Balance realism with simplicity
- No need for perfect formatting, but should be believable

---

### TC-D-003-QUAL02: Data Consistency Across Documents

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify data consistency across related documents (same person).

**Test Steps:**
1. Review personal data in each document:
   - Birth certificate name
   - Passport name
   - Language certificate name
   - Application name
2. Check for consistency
3. Verify dates make sense
4. Check nationality consistent

**Expected Results:**
- Name consistent across documents: Ahmad Ali
- Birth date consistent: 15.05.1990
- Nationality consistent: Afghanistan
- Dates logical (passport issued after birth, certificate recent, etc.)
- No contradictions between documents
- Story cohesive

**Test Data:**
Common data points:
- Name: Ahmad Ali
- Birth date: 15.05.1990
- Nationality: Afghanistan
- Current location: Germany

**Notes:**
- Consistency important for realistic test case
- Minor variations OK (name format differences)
- Must not contradict

---

### TC-D-003-QUAL03: German-English Language Mix

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Verify appropriate mix of German and English reflects real-world scenario.

**Test Steps:**
1. Review language in each document
2. Check if language choice makes sense:
   - German documents: birth certificate, certificates
   - English: might appear in some forms or emails
   - Mixed: realistic for integration context
3. Verify AI handles both languages

**Expected Results:**
- Official German documents in German (birth certificate, certificates)
- Some documents may be bilingual
- Email might be German or English
- Mix reflects real BAMF integration case scenario
- AI understands both languages
- No confusion from language mix

**Notes:**
- Integration course applicants often have mix of languages
- German documents need translation, but sample docs can include both

---

## AI Extraction Tests

### TC-D-003-AI01: Name Extraction Accuracy

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test AI's ability to accurately extract names from various document formats.

**Test Steps:**
1. Test name extraction from:
   - Birth certificate (German format)
   - Passport (uppercase format)
   - Language certificate
   - Application form
2. Verify AI extracts correct name despite format differences
3. Check handling of:
   - Middle names (if present)
   - Name order (first/last)
   - Case variations

**Expected Results:**
- Name extracted accurately from all documents
- Handles different formats:
  - "Ahmad Ali" (birth certificate)
  - "AHMAD ALI" (passport uppercase)
  - "Ali, Ahmad" (reversed order if present)
- Consistent normalization
- No extra characters or corruption

---

### TC-D-003-AI02: Date Extraction and Conversion

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test AI extraction and conversion of dates from German format.

**Test Steps:**
1. Extract dates from documents:
   - Birth date: 15.05.1990 (German DD.MM.YYYY)
   - Passport dates: 20.05.2020
   - Certificate date: 15.06.2023
2. Verify AI converts to ISO format: YYYY-MM-DD
3. Test various date formats in documents

**Expected Results:**
- German format (DD.MM.YYYY) recognized
- Converted to ISO (YYYY-MM-DD)
- Examples:
  - 15.05.1990 → 1990-05-15
  - 20.05.2020 → 2020-05-20
- No date parsing errors
- Leap years handled correctly
- Invalid dates rejected

---

### TC-D-003-AI03: Contextual Information Extraction

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test AI's ability to extract contextual information beyond simple field extraction.

**Test Steps:**
1. Ask AI: "Where is this person from?"
2. Ask AI: "When did this person complete the A1 course?"
3. Ask AI: "What documents are missing for a complete application?"
4. Verify contextual understanding

**Expected Results:**
- AI understands context across documents
- Answers questions correctly:
  - "From Afghanistan" or "From Kabul, Afghanistan"
  - "June 15, 2023" or "15.06.2023"
  - Lists missing documents based on requirements
- Not just keyword matching
- Demonstrates document comprehension

---

## Automated Test Implementation

### Document Content Tests (TypeScript/Jest)

**File:** `tests/unit/documentContent.test.ts`

```typescript
describe('Sample Document Content - Case-Instance Scoped', () => {
  const caseId = 'ACTE-2024-001';

  it('Birth certificate contains required information from case directory', async () => {
    const response = await fetch(`/documents/${caseId}/personal-data/Birth_Certificate.txt`);
    const content = await response.text();

    expect(content).toContain('Ahmad Ali');
    expect(content).toContain('15.05.1990');
    expect(content).toContain('Kabul');
    expect(content.length).toBeGreaterThan(300);
    expect(content.length).toBeLessThan(2000);
  });

  it('Passport contains valid passport number from case directory', async () => {
    const response = await fetch(`/documents/${caseId}/personal-data/Passport_Scan.txt`);
    const content = await response.text();

    expect(content).toContain('P123456789');
    expect(content).toContain('AHMAD ALI');
    expect(content).toContain('20.05.2028');
  });

  it('Language certificate specifies A1 level from case directory', async () => {
    const response = await fetch(`/documents/${caseId}/certificates/Language_Certificate_A1.txt`);
    const content = await response.text();

    expect(content).toMatch(/A1|Niveau A1/i);
    expect(content).toContain('Goethe');
  });

  it('Case isolation - cannot access other case documents', async () => {
    // Attempt to access ACTE-2024-002 documents while ACTE-2024-001 active
    const response = await fetch('/documents/ACTE-2024-002/personal-data/Birth_Certificate.txt');

    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
  });

  it('All documents preserve UTF-8 encoding in case directories', async () => {
    const files = [
      `${caseId}/personal-data/Birth_Certificate.txt`,
      `${caseId}/certificates/Language_Certificate_A1.txt`,
      `${caseId}/applications/Integration_Application.txt`
    ];

    for (const file of files) {
      const response = await fetch(`/documents/${file}`);
      const content = await response.text();

      // Check that German characters are preserved
      const hasGermanChars = /[äöüßÄÖÜ]/.test(content);
      if (file.includes('Birth') || file.includes('Language')) {
        expect(hasGermanChars).toBe(true);
      }
    }
  });

  it('Data consistent across documents in same case', async () => {
    const birth = await (await fetch(`/documents/${caseId}/personal-data/Birth_Certificate.txt`)).text();
    const passport = await (await fetch(`/documents/${caseId}/personal-data/Passport_Scan.txt`)).text();
    const cert = await (await fetch(`/documents/${caseId}/certificates/Language_Certificate_A1.txt`)).text();

    // Name should appear in all (case variations OK)
    expect(birth.toLowerCase()).toContain('ahmad');
    expect(passport.toLowerCase()).toContain('ahmad');
    expect(cert.toLowerCase()).toContain('ahmad');

    // Birth date should appear in birth certificate
    expect(birth).toContain('15.05.1990');
  });

  it('Documents isolated per case - different cases have different documents', async () => {
    const case1Doc = await (await fetch('/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt')).text();
    const case2Doc = await (await fetch('/documents/ACTE-2024-002/personal-data/Birth_Certificate.txt')).text();

    // Documents should be different for different cases
    expect(case1Doc).not.toBe(case2Doc);
  });
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Unit | 6 | 4 | 2 | 0 |
| Integration | 4 | 3 | 1 | 0 |
| Manual/Quality | 3 | 1 | 2 | 0 |
| AI Extraction | 3 | 2 | 1 | 0 |
| **Total** | **16** | **10** | **6** | **0** |

---

## Sample Documents Checklist (Case-Instance Scoped)

### Directory Structure
```
public/documents/
├── ACTE-2024-001/          # German Integration Course case
│   ├── personal-data/
│   ├── certificates/
│   ├── integration-docs/
│   ├── applications/
│   ├── emails/
│   └── evidence/
├── ACTE-2024-002/          # Asylum Application case
│   └── ...
├── ACTE-2024-003/          # Family Reunification case
│   └── ...
└── templates/              # Templates for new cases
    └── integration_course/
```

### Documents for ACTE-2024-001

| Document | Size (chars) | Language | Key Content | Location | Created |
|----------|--------------|----------|-------------|----------|---------|
| Birth_Certificate.txt | 500-800 | German | Name, birthdate, birthplace | ACTE-2024-001/personal-data/ | [ ] |
| Passport_Scan.txt | 400-600 | English | Passport #, dates, name | ACTE-2024-001/personal-data/ | [ ] |
| Language_Certificate_A1.txt | 600-1000 | German/English | Level, institution, date | ACTE-2024-001/certificates/ | [ ] |
| Integration_Application.txt | 1000-1500 | German/English | Application details | ACTE-2024-001/applications/ | [ ] |
| School_Transcripts.txt | 1200-2000 | English/German | Education history | ACTE-2024-001/evidence/ | [ ] |
| Confirmation_Email.txt | 300-500 | German/English | Confirmation, date | ACTE-2024-001/emails/ | [ ] |

---

## Test Execution Checklist

### Case-Instance Structure
- [ ] Case directory structure created for ACTE-2024-001
- [ ] Folder subdirectories created for each document type
- [ ] All 6 document text files created in correct case-specific locations
- [ ] Files saved with UTF-8 encoding
- [ ] All files 300-2000 characters

### Content Quality
- [ ] Content realistic and formatted properly
- [ ] German special characters preserved
- [ ] Data consistent across documents (same person in same case)
- [ ] Names, dates, locations match within case

### Case Isolation
- [ ] Documents loadable via HTTP with case-specific paths
- [ ] Cross-case access prevented (404 for wrong case)
- [ ] Multiple cases have different document sets

### Integration
- [ ] AI can extract data successfully from case-specific documents
- [ ] Form auto-fill works with case-aware documents
- [ ] Visual rendering correct in DocumentViewer
- [ ] Context loaded from correct case directory

### Testing
- [ ] All languages handled properly
- [ ] Automated content tests passing with case paths
- [ ] Manual quality review completed
- [ ] Case switching tests verified
