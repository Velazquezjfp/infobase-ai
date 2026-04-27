# F-002: Document Context Management System (Case-Instance Scoped)

## Test Cases

### TC-F-002-01: Load Case-Instance Context

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify that case-instance-level context can be loaded correctly from the case-specific directory and contains all required information. Each case (ACTE) has its own context directory ensuring complete isolation.

**Preconditions:**
- Backend context manager service implemented
- Case context file exists at backend/data/contexts/cases/ACTE-2024-001/case.json
- File contains valid JSON structure with caseId field

**Test Steps:**
1. Call `context_manager.load_case_context("ACTE-2024-001")`
2. Verify return value is not null
3. Check for required fields: caseId, caseType, name, description, regulations, requiredDocuments, validationRules, commonIssues
4. Validate schema version is "1.0"
5. Validate caseId matches: "ACTE-2024-001"
6. Count number of regulations, documents, and rules

**Expected Results:**
- Context loaded successfully without errors
- All required fields present
- Schema version: "1.0"
- Case ID: "ACTE-2024-001"
- Case Type: "integration_course"
- Name: "German Integration Course Application"
- Regulations array contains 5+ items
- RequiredDocuments array contains 10+ items
- ValidationRules array contains 8+ items

**Test Data:**
- Case ID: "ACTE-2024-001"
- Expected file: `backend/data/contexts/cases/ACTE-2024-001/case.json`

**Notes:**
- Verify JSON structure matches schema defined in D-001
- Check that regulations include §43 AufenthG reference
- Context is case-specific, not shared across cases

---

### TC-F-002-02: Load Case-Specific Folder Context

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test loading folder-specific context for the Personal Data folder within a specific case directory, verifying it contains appropriate validation rules for that case instance.

**Preconditions:**
- Context manager service available
- personal-data.json exists in backend/data/contexts/cases/ACTE-2024-001/folders/
- Valid JSON structure

**Test Steps:**
1. Call `context_manager.load_folder_context("ACTE-2024-001", "personal-data")`
2. Verify successful load
3. Check for required fields: folderId, folderName, purpose, expectedDocuments, validationCriteria
4. Validate expectedDocuments array
5. Count validation rules (should be 3+)

**Expected Results:**
- Folder context loaded successfully from case-specific directory
- Folder name: "Personal Data"
- Purpose field describes identity verification
- ExpectedDocuments includes: "birth_certificate", "passport", "national_id"
- ValidationCriteria includes at least 3 rules:
  - name_consistency
  - valid_dates
  - certified_translations

**Test Data:**
- Case ID: "ACTE-2024-001"
- Folder ID: "personal-data"
- Expected file: `backend/data/contexts/cases/ACTE-2024-001/folders/personal-data.json`

**Notes:**
- Folder context is case-specific, not shared
- Test with all 6 folder types within same case
- Different cases can have different folder contexts

---

### TC-F-002-03: Switch Between Cases - Context Reload

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that switching between cases properly reloads context from the new case's directory and that AI responses reflect the new case's context.

**Preconditions:**
- Multiple cases exist: ACTE-2024-001 (Integration Course), ACTE-2024-002 (Asylum Application)
- Context directories exist for both cases
- Context manager handles case switching

**Test Steps:**
1. Load case ACTE-2024-001
2. Verify context loaded from `cases/ACTE-2024-001/case.json`
3. Send AI query: "What type of case is this?"
4. Verify response mentions "Integration Course"
5. Switch to case ACTE-2024-002
6. Verify context reloaded from `cases/ACTE-2024-002/case.json`
7. Send same AI query: "What type of case is this?"
8. Verify response mentions "Asylum Application"

**Expected Results:**
- Context switches cleanly between cases
- ACTE-2024-001 context includes Integration Course regulations
- ACTE-2024-002 context includes Asylum Application regulations
- AI responses reflect active case's context
- No context contamination between cases
- Document tree updates to show only active case's documents

**Test Data:**
```json
{
  "type": "chat",
  "content": "What type of case is this?",
  "caseId": "ACTE-2024-001"
}
```
Then switch:
```json
{
  "type": "chat",
  "content": "What type of case is this?",
  "caseId": "ACTE-2024-002"
}
```

**Notes:**
- Critical test for case isolation
- Verify complete context reload, not partial update

---

### TC-F-002-04: Context-Aware Birth Certificate Validation

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Validate that the AI agent uses case-specific context information when analyzing a birth certificate in the Personal Data folder, specifically mentioning relevant validation fields for that case.

**Preconditions:**
- WebSocket connection established to ws://localhost:8000/ws/chat/ACTE-2024-001
- Birth certificate document selected from ACTE-2024-001
- Document in "personal-data" folder
- Case and folder context loaded from ACTE-2024-001 directory

**Test Steps:**
1. Select birth certificate document in Personal Data folder of ACTE-2024-001
2. Send chat message: "Validate this document"
3. Include document content from case-specific path
4. Wait for AI response
5. Analyze response for context-aware validation

**Expected Results:**
- Response mentions "date of birth" validation
- Response mentions "nationality" validation
- Response references Personal Data folder requirements from ACTE-2024-001 context
- If document missing required fields, agent identifies them
- Agent follows validation criteria from cases/ACTE-2024-001/folders/personal-data.json

**Test Data:**
```json
{
  "type": "chat",
  "content": "Validate this document",
  "documentContent": "Birth Certificate: Ahmad Ali, Born: 15.05.1990, Place: Kabul",
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data"
}
```

**Notes:**
- Manual verification of response quality required
- Compare response with and without case-specific context
- Verify context loaded from correct case directory

---

### TC-F-002-05: Create New Case from Template

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that creating a new case dynamically copies the template context structure to create a case-specific context directory with all necessary files.

**Preconditions:**
- Template context exists at backend/data/contexts/templates/integration_course/
- Context manager implements create_case_from_template method
- Filesystem write permissions available

**Test Steps:**
1. Call `context_manager.create_case_from_template("ACTE-2024-004", "integration_course")`
2. Verify new directory created at `backend/data/contexts/cases/ACTE-2024-004/`
3. Check case.json file exists with caseId="ACTE-2024-004"
4. Verify folders subdirectory created
5. Check all 6 folder context files copied
6. Load context for new case and verify it works

**Expected Results:**
- New case directory created: `cases/ACTE-2024-004/`
- case.json exists with correct caseId
- Folders subdirectory contains 6 JSON files
- All context files are valid JSON
- New case context loadable and functional
- Case isolated from template and other cases

**Test Data:**
- New case ID: "ACTE-2024-004"
- Case type: "integration_course"
- Template path: `backend/data/contexts/templates/integration_course/`

**Notes:**
- Template should not be modified during copy
- Each new case gets independent context
- Test case creation for different case types

---

### TC-F-002-06: Goethe Institut Certificate Recognition

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that the AI agent recognizes Goethe Institut as a valid language certificate issuer based on case-specific Certificates folder context.

**Preconditions:**
- Language certificate document available in ACTE-2024-001
- Document placed in "certificates" folder
- Certificates context loaded from cases/ACTE-2024-001/folders/certificates.json

**Test Steps:**
1. Load Language_Certificate_A1.txt in Certificates folder of ACTE-2024-001
2. Send message: "Is this certificate valid?"
3. Include document content showing Goethe Institut as issuer
4. Verify response acknowledges Goethe Institut validity

**Expected Results:**
- Agent recognizes Goethe Institut as valid issuer
- Response mentions CEFR level validation (A1)
- Agent checks certificate is within validity period
- Response references cases/ACTE-2024-001/folders/certificates.json validation criteria

**Test Data:**
```json
{
  "type": "chat",
  "content": "Is this certificate valid?",
  "documentContent": "Goethe-Institut Certificate\nLevel: A1\nIssued: 15.06.2023",
  "caseId": "ACTE-2024-001",
  "folderId": "certificates"
}
```

**Notes:**
- Test with both recognized and unrecognized institutions
- Verify CEFR level validation (A1-C2)
- Context loaded from case-specific folder

---

### TC-F-002-07: Wrong Folder Suggestion

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify the AI agent can identify when a document is placed in the wrong folder and suggest the correct location based on case-specific folder context.

**Preconditions:**
- Multiple folder contexts loaded for ACTE-2024-001
- Language certificate uploaded to wrong folder (e.g., Personal Data)
- Folder contexts include expected document types

**Test Steps:**
1. Upload language certificate to "personal-data" folder of ACTE-2024-001
2. Ask AI: "Is this document in the right place?"
3. Include document content showing it's a certificate
4. Wait for agent suggestion

**Expected Results:**
- Agent identifies document type mismatch
- Agent suggests correct folder: "certificates"
- Response explains why document should be moved
- Agent references folder-specific expected documents from case context

**Test Data:**
```json
{
  "type": "chat",
  "content": "Is this document in the right place?",
  "documentContent": "Goethe-Institut A1 Certificate",
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data"
}
```

**Notes:**
- Test with multiple document types in wrong folders
- Verify suggestion accuracy using case-specific folder contexts

---

### TC-F-002-08: Graceful Fallback for Non-Existent Case Context

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Ensure the system handles requests for non-existent case contexts gracefully with appropriate error handling or fallback behavior.

**Preconditions:**
- Context manager service running
- Request made for non-existent case

**Test Steps:**
1. Request context for invalid case ID: "ACTE-9999-999"
2. Verify appropriate error handling
3. Check that error message is user-friendly
4. Verify no case isolation breach (no fallback to other case data)
5. Send chat message with invalid case ID

**Expected Results:**
- Error caught and logged appropriately
- Error message: "Case context not found for: ACTE-9999-999"
- No fallback to other cases' data (maintains isolation)
- AI agent cannot access non-existent case
- User notified case doesn't exist
- Application remains stable

**Test Data:**
- Invalid case ID: "ACTE-9999-999"

**Notes:**
- Critical for case isolation security
- Must not expose internal paths or other cases
- Different behavior from folder fallback (no fallback allowed for case)

---

### TC-F-002-09: Case Isolation Verification

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that cases are completely isolated - accessing content from one case while another is active should be prevented.

**Preconditions:**
- Multiple cases exist with context: ACTE-2024-001, ACTE-2024-002
- Document tree loaded for ACTE-2024-001

**Test Steps:**
1. Load case ACTE-2024-001
2. Attempt to access document from ACTE-2024-002 directory
3. Verify access denied or 404
4. Attempt to load ACTE-2024-002 context while ACTE-2024-001 active
5. Verify proper context switching required

**Expected Results:**
- Cannot access ACTE-2024-002 documents while ACTE-2024-001 active
- Cannot access ACTE-2024-002 context without explicit switch
- Document tree shows only ACTE-2024-001 documents
- Context manager enforces case boundaries
- No data leakage between cases

**Test Data:**
- Active case: "ACTE-2024-001"
- Attempt to access from: "ACTE-2024-002"

**Notes:**
- Critical security test for multi-case system
- Ensures data privacy between cases

---

## Edge Cases

### TC-F-002-E01: Context Hierarchy Merging

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test the merge_contexts function to ensure proper hierarchy: case context + folder context + document context.

**Test Steps:**
1. Load case context for integration course
2. Load folder context for Personal Data
3. Add document-specific context (e.g., birth certificate details)
4. Call merge_contexts(case_ctx, folder_ctx, doc_ctx)
5. Verify merged context contains all information
6. Check for proper precedence (document > folder > case)

**Expected Results:**
- Merged context string contains information from all three levels
- Document context takes precedence for conflicting information
- Context formatted appropriately for Gemini prompt
- No information loss during merge

---

### TC-F-002-E02: Multiple Folder Context Switching

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test context switching when user navigates between folders during a conversation.

**Test Steps:**
1. Start conversation in Personal Data folder
2. Ask about birth certificate requirements
3. Switch to Certificates folder
4. Ask about language certificate requirements
5. Verify agent uses correct context for each

**Expected Results:**
- Agent responses reflect current folder context
- No context contamination between folders
- Context switches cleanly without residual information

---

### TC-F-002-E03: Context File with Special Characters

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Verify proper handling of context files containing special characters and multilingual content.

**Test Steps:**
1. Create context file with German umlauts (ä, ö, ü, ß)
2. Load context using context manager
3. Verify characters preserved correctly
4. Send to AI agent and check response

**Expected Results:**
- UTF-8 encoding preserved throughout
- Special characters display correctly
- No encoding corruption

---

## Error Handling Tests

### TC-F-002-ERR01: Missing Context File

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test behavior when context file is missing from filesystem.

**Test Steps:**
1. Temporarily rename or remove integration_course.json
2. Attempt to load case context
3. Verify error handling
4. Check logs for appropriate error message

**Expected Results:**
- FileNotFoundError caught gracefully
- Empty or default context returned
- Error logged with file path
- Application continues running
- User receives notification if context unavailable

---

### TC-F-002-ERR02: Malformed JSON Context

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Handle corrupted or invalid JSON in context files.

**Test Steps:**
1. Create context file with invalid JSON syntax
2. Attempt to load context
3. Verify JSONDecodeError handling
4. Check error logging

**Expected Results:**
- JSONDecodeError caught
- Empty context returned with error flag
- Detailed error logged (line number if possible)
- No application crash

---

### TC-F-002-ERR03: Context File Missing Required Fields

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test validation when context file has missing required fields.

**Test Steps:**
1. Create context file missing "regulations" field
2. Load context
3. Verify validation catches missing field
4. Check for appropriate warning

**Expected Results:**
- Validation warning logged
- Context loaded with partial data
- Missing fields treated as empty arrays/objects
- Agent still functional with reduced context

---

## Performance Tests

### TC-F-002-PERF01: Context Loading Time

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Measure time to load and merge all context levels.

**Test Steps:**
1. Cold start: Load case + folder + document context
2. Measure total load time
3. Repeat 10 times to get average
4. Verify caching if implemented

**Expected Results:**
- Initial load time < 500ms
- Subsequent loads < 100ms (if cached)
- Total context size reasonable for API calls

---

### TC-F-002-PERF02: Context Size Impact on Response Time

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Measure impact of context size on AI response time.

**Test Steps:**
1. Send request with minimal context (case only)
2. Send identical request with full context (case + folder + document)
3. Compare response times
4. Verify context size doesn't cause timeout

**Expected Results:**
- Response time difference < 1 second
- Full context doesn't exceed Gemini token limits
- Quality improvement justifies latency cost

---

## Internationalization Tests

### TC-F-002-I18N01: German Language Context

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test agent understanding when context includes German regulations and terminology.

**Test Steps:**
1. Load context with German regulation texts
2. Send query in German about requirements
3. Verify agent responds appropriately in German
4. Check understanding of legal terms

**Expected Results:**
- Agent understands German legal terminology
- Response maintains appropriate language
- Regulation references accurate

---

### TC-F-002-I18N02: Mixed Language Document and Context

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify handling when document is in German but user asks in English, with mixed-language context.

**Test Steps:**
1. Load German birth certificate
2. Context includes both German and English terms
3. User asks in English: "What information is in this document?"
4. Verify appropriate response

**Expected Results:**
- Agent understands document despite language mismatch
- Response in English as requested
- Key information extracted correctly

---

## Automated Test Implementation

### Backend Unit Tests (Python/pytest)

**File:** `backend/tests/test_context_manager.py`

```python
import pytest
from backend.services.context_manager import ContextManager

@pytest.fixture
def context_manager():
    return ContextManager(base_path="backend/data/contexts")

def test_load_case_instance_context(context_manager):
    """Test loading case-specific context from cases/{caseId}/case.json"""
    context = context_manager.load_case_context("ACTE-2024-001")
    assert context is not None
    assert "caseId" in context
    assert context["caseId"] == "ACTE-2024-001"
    assert "caseType" in context
    assert context["caseType"] == "integration_course"
    assert "name" in context
    assert context["name"] == "German Integration Course Application"
    assert len(context["regulations"]) >= 5

def test_load_case_specific_folder_context(context_manager):
    """Test loading folder context from cases/{caseId}/folders/{folderId}.json"""
    context = context_manager.load_folder_context("ACTE-2024-001", "personal-data")
    assert context is not None
    assert "folderId" in context
    assert context["folderId"] == "personal-data"
    assert "folderName" in context
    assert "Personal Data" in context["folderName"]
    assert len(context["validationCriteria"]) >= 3

def test_case_switching(context_manager):
    """Test that context switches correctly between different cases"""
    context1 = context_manager.load_case_context("ACTE-2024-001")
    context2 = context_manager.load_case_context("ACTE-2024-002")

    assert context1["caseId"] == "ACTE-2024-001"
    assert context2["caseId"] == "ACTE-2024-002"
    assert context1["caseType"] != context2["caseType"]  # Different case types

def test_create_case_from_template(context_manager):
    """Test creating new case directory from template"""
    new_case_id = "ACTE-2024-004"
    context_manager.create_case_from_template(new_case_id, "integration_course")

    # Verify case directory created
    import os
    case_path = f"backend/data/contexts/cases/{new_case_id}"
    assert os.path.exists(case_path)
    assert os.path.exists(f"{case_path}/case.json")
    assert os.path.exists(f"{case_path}/folders")

def test_case_isolation(context_manager):
    """Test that cases are isolated - cannot access other case's context"""
    context = context_manager.load_case_context("ACTE-2024-001")

    # Attempt to access ACTE-2024-002 folder context while ACTE-2024-001 active
    with pytest.raises(Exception):
        # This should fail or return empty if not explicitly switched
        context_manager.load_folder_context("ACTE-2024-002", "personal-data")

def test_merge_contexts(context_manager):
    """Test merging case, folder, and document contexts"""
    case_ctx = context_manager.load_case_context("ACTE-2024-001")
    folder_ctx = context_manager.load_folder_context("ACTE-2024-001", "personal-data")
    doc_ctx = "Birth certificate for Ahmad Ali"

    merged = context_manager.merge_contexts(case_ctx, folder_ctx, doc_ctx)
    assert "Integration Course" in merged
    assert "Personal Data" in merged
    assert "Ahmad Ali" in merged
    assert "ACTE-2024-001" in merged  # Case ID should be in merged context
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Unit | 4 | 2 | 2 | 0 |
| Integration | 5 | 3 | 2 | 0 |
| Edge Cases | 3 | 0 | 2 | 1 |
| Error Handling | 3 | 2 | 1 | 0 |
| Performance | 2 | 0 | 1 | 1 |
| I18N | 2 | 0 | 2 | 0 |
| **Total** | **19** | **7** | **10** | **2** |

---

## Test Execution Checklist

- [ ] All context JSON files created and validated
- [ ] Context manager service implemented
- [ ] Test context files with valid and invalid data prepared
- [ ] Manual verification procedures documented
- [ ] Performance benchmarks recorded
- [ ] Internationalization test cases executed
- [ ] Error scenarios tested and handled
- [ ] Test results documented
