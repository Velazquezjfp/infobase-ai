# D-001: Hierarchical Context Data Schema (Case-Instance Scoped)

## Test Cases

### TC-D-001-01: Case-Instance Context Schema Validation

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify that case-instance context files conform to the specified schema with all required top-level keys present. Each case has its own context directory for complete isolation.

**Preconditions:**
- Case context file exists at backend/data/contexts/cases/ACTE-2024-001/case.json
- File contains valid JSON with case-specific information

**Test Steps:**
1. Load cases/ACTE-2024-001/case.json
2. Parse JSON content
3. Verify schemaVersion field exists and equals "1.0"
4. Check for required top-level keys:
   - caseId (NEW - specific to this instance)
   - caseType
   - name
   - description
   - regulations
   - requiredDocuments
   - validationRules
   - commonIssues
5. Verify data types of each field
6. Verify caseId matches directory name

**Expected Results:**
- schemaVersion: "1.0"
- All 8 required keys present (including caseId)
- Key types:
  - caseId: string ("ACTE-2024-001")
  - caseType: string ("integration_course")
  - name: string
  - description: string
  - regulations: array
  - requiredDocuments: array
  - validationRules: array
  - commonIssues: array
- File size < 100KB
- Valid JSON structure
- caseId matches directory structure

**Test Data:**
File: `backend/data/contexts/cases/ACTE-2024-001/case.json`
Expected caseId: "ACTE-2024-001"
Expected caseType: "integration_course"

**Notes:**
- Schema version enables future migrations
- File size limit ensures performance
- caseId field critical for case isolation

---

### TC-D-001-02: Regulations Array Structure

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Validate that each regulation in the regulations array has the required fields: id, title, and summary.

**Preconditions:**
- integration_course.json loaded successfully
- regulations array exists

**Test Steps:**
1. Access regulations array from context
2. Verify array length ≥ 5 (requirement specifies 5+ regulations)
3. For each regulation object, check:
   - Has "id" field (string)
   - Has "title" field (string)
   - Has "summary" field (string)
4. Verify at least one regulation references §43 AufenthG
5. Check for duplicates (unique IDs)

**Expected Results:**
- Regulations array contains 5+ items
- Each regulation has id, title, summary
- Example regulation structure:
  ```json
  {
    "id": "§43_AufenthG",
    "title": "Integration course entitlement",
    "summary": "Defines who is entitled to participate in integration courses..."
  }
  ```
- No duplicate regulation IDs
- All summaries non-empty (> 20 characters)

**Test Data:**
Expected regulation IDs include: §43_AufenthG, §44_AufenthG, etc.

**Notes:**
- German legal references (§ symbol) should be preserved
- Summaries should be informative, not just titles

---

### TC-D-001-03: Case-Specific Folder Context Schema

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify case-specific folder context files contain expected document types in expectedDocuments array. Folder contexts are stored per-case for modularity.

**Preconditions:**
- personal-data.json exists at backend/data/contexts/cases/ACTE-2024-001/folders/
- Valid JSON structure
- File is case-specific

**Test Steps:**
1. Load cases/ACTE-2024-001/folders/personal-data.json
2. Verify required keys: folderId, folderName, purpose, expectedDocuments, validationCriteria
3. Check expectedDocuments array
4. Verify includes: "birth_certificate", "passport", "national_id"
5. Validate validationCriteria array length

**Expected Results:**
- folderId: "personal-data"
- folderName: "Personal Data"
- purpose: describes identity verification
- expectedDocuments includes at minimum:
  - "birth_certificate"
  - "passport"
  - "national_id"
- validationCriteria array has 3+ items
- All criteria are objects with meaningful content

**Test Data:**
File: `backend/data/contexts/cases/ACTE-2024-001/folders/personal-data.json`
Case ID: "ACTE-2024-001"

**Notes:**
- expectedDocuments should match actual document types in case directory
- validationCriteria guides AI agent behavior for this specific case
- Different cases can have different folder contexts

---

### TC-D-001-04: Certificates Folder Validation Criteria

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test that certificates.json includes CEFR level validation and recognized institutions.

**Preconditions:**
- certificates.json file exists and is valid JSON

**Test Steps:**
1. Load certificates.json
2. Access validationCriteria array
3. Search for "cefr_level_valid" criterion
4. Search for "recognized_institution" criterion
5. Verify criterion objects have descriptive content

**Expected Results:**
- validationCriteria includes "cefr_level_valid" rule
- Rule references CEFR levels: A1, A2, B1, B2, C1, C2
- validationCriteria includes "recognized_institution"
- Recognized institutions might include: Goethe Institut, TestDaF, telc
- Criteria provide actionable validation guidance

**Test Data:**
File: `backend/data/contexts/folders/certificates.json`

**Notes:**
- CEFR: Common European Framework of Reference for Languages
- Only recognized institutions should be accepted

---

### TC-D-001-05: Case-Instance JSON Syntax Validation

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Parse all case-instance context files with JSON validator to ensure no syntax errors. Validate structure for multiple cases to ensure consistency.

**Preconditions:**
- Case directories created for multiple cases (ACTE-2024-001, ACTE-2024-002, etc.)
- Each case has 1 case.json + 6 folder context files

**Test Steps:**
1. List all case directories in backend/data/contexts/cases/
2. For each case directory:
   - Parse case.json
   - Parse all 6 folder JSON files
   - Catch any parsing errors
   - Record result
3. Verify all files parse successfully
4. Verify template files also valid

**Expected Results:**
- All context files parse without errors
- No syntax issues: missing commas, unclosed brackets, trailing commas
- UTF-8 encoding preserved (German characters)
- Consistent formatting (optional but nice: 2-space indentation)
- Each case has complete set of context files

**Test Data:**
Files to validate for ACTE-2024-001:
1. cases/ACTE-2024-001/case.json
2. cases/ACTE-2024-001/folders/personal-data.json
3. cases/ACTE-2024-001/folders/certificates.json
4. cases/ACTE-2024-001/folders/integration-docs.json
5. cases/ACTE-2024-001/folders/applications.json
6. cases/ACTE-2024-001/folders/emails.json
7. cases/ACTE-2024-001/folders/evidence.json

Template files to validate:
- templates/integration_course/*.json
- templates/asylum_application/*.json (if exists)

**Notes:**
- Use JSON validator tool or script
- Command: `python -m json.tool file.json`
- Or: `jq . file.json` (if jq installed)
- Validate multiple cases for consistency

---

### TC-D-001-06: Context Size Performance Check

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Verify total context size for integration_course.json is under 100KB for performance.

**Preconditions:**
- integration_course.json file exists

**Test Steps:**
1. Check file size: `ls -lh integration_course.json`
2. Measure in bytes
3. Verify < 100KB (102,400 bytes)
4. Load file and measure parse time
5. Calculate memory footprint

**Expected Results:**
- File size < 100KB
- Parse time < 50ms
- Reasonable memory usage (< 1MB in memory)
- Fast enough for real-time loading during API calls

**Test Data:**
Target: < 100KB file size

**Notes:**
- Large contexts slow AI API calls
- Consider compression if exceeds limit
- Balance completeness with performance

---

### TC-D-001-07: Unique Folder IDs

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify that all 6 folder context files have unique folderId values with no duplicates.

**Preconditions:**
- All 6 folder context files exist

**Test Steps:**
1. Load all 6 folder context files
2. Extract folderId from each
3. Create list of IDs
4. Check for duplicates
5. Verify IDs match expected values

**Expected Results:**
- 6 unique folder IDs:
  1. "personal-data"
  2. "certificates"
  3. "integration-docs"
  4. "applications"
  5. "emails"
  6. "evidence"
- No duplicate IDs
- IDs match folder IDs used in frontend code
- Consistent naming convention (kebab-case)

**Test Data:**
Expected IDs: personal-data, certificates, integration-docs, applications, emails, evidence

**Notes:**
- Duplicate IDs would cause context lookup errors
- IDs must match frontend folder structure

---

## Schema Compliance Tests

### TC-D-001-SCHEMA01: Required Documents Structure

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Validate requiredDocuments array structure in integration_course.json.

**Test Steps:**
1. Access requiredDocuments array
2. Verify array length ≥ 10 (requirement)
3. Check each document object has:
   - documentType (string)
   - mandatory (boolean)
   - validationRules (array of strings)
4. Verify validation rules are descriptive

**Expected Results:**
- 10+ required documents defined
- Each has documentType, mandatory, validationRules
- Example:
  ```json
  {
    "documentType": "birth_certificate",
    "mandatory": true,
    "validationRules": ["must_be_certified", "max_age_6_months"]
  }
  ```
- Validation rules are actionable strings
- Mix of mandatory true/false documents

**Notes:**
- Guides document collection process
- Validation rules used by AI agent

---

### TC-D-001-SCHEMA02: Validation Rules Structure

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test validationRules array structure in case context.

**Test Steps:**
1. Access validationRules array
2. Verify array length ≥ 8 (requirement)
3. Check each rule has:
   - rule_id (string)
   - condition (string)
   - action (string)
4. Verify rules are complete and actionable

**Expected Results:**
- 8+ validation rules defined
- Each has rule_id, condition, action
- Example:
  ```json
  {
    "rule_id": "age_verification",
    "condition": "applicant must be 18+",
    "action": "verify birthDate indicates age >= 18"
  }
  ```
- Rules cover common validation scenarios
- Actions guide agent behavior

---

### TC-D-001-SCHEMA03: Common Issues Structure

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Validate commonIssues array provides helpful guidance.

**Test Steps:**
1. Access commonIssues array
2. Check each issue has:
   - issue (string) - description
   - severity (string) - warning/error/info
   - suggestion (string) - how to resolve
3. Verify issues are realistic and helpful

**Expected Results:**
- Multiple common issues documented
- Each has issue, severity, suggestion
- Example:
  ```json
  {
    "issue": "Missing translation",
    "severity": "warning",
    "suggestion": "All non-German documents must have certified German translation"
  }
  ```
- Severity levels: error, warning, info
- Suggestions are actionable

---

## Data Quality Tests

### TC-D-001-QUALITY01: German Language Content

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Review context files for correct German language content and terminology.

**Test Steps:**
1. Review context files containing German text
2. Check regulations for correct legal terminology
3. Verify umlauts preserved (ä, ö, ü, ß)
4. Check for spelling errors
5. Verify translations accurate (if bilingual)

**Expected Results:**
- German legal terms correct: §, Aufenthaltsgesetz, etc.
- Umlauts preserved and display correctly
- No spelling errors
- Professional language appropriate for BAMF context
- Consistent terminology throughout

**Notes:**
- Requires German language reviewer
- Legal accuracy important

---

### TC-D-001-QUALITY02: Content Completeness

**Type:** Manual
**Priority:** Medium
**Status:** Pending

**Description:**
Verify context content is complete, detailed, and useful for AI agent.

**Test Steps:**
1. Review integration_course.json completeness
2. Check if regulations are sufficiently detailed
3. Verify validation rules are specific
4. Assess if context enables AI to give good advice
5. Test with actual AI queries

**Expected Results:**
- Context provides meaningful guidance
- Not just placeholder text
- Sufficient detail for AI to understand domain
- Regulations explained, not just listed
- Validation rules actionable

**Notes:**
- Quality assessment somewhat subjective
- Test with real AI queries to validate usefulness

---

## Cross-File Consistency Tests

### TC-D-001-CONSIST01: Document Type Consistency

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify document types referenced in case context match those in folder contexts.

**Test Steps:**
1. Extract document types from integration_course requiredDocuments
2. Extract expected documents from all folder contexts
3. Compare and find mismatches
4. Check if all required docs have corresponding folder

**Expected Results:**
- Document types consistent across files
- Every required document has a designated folder
- No orphaned document types
- Naming consistent (snake_case)

**Notes:**
- Ensures context hierarchy is coherent
- Mismatches could confuse AI agent

---

### TC-D-001-CONSIST02: Folder Reference Integrity

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify folder IDs in context files match folder IDs in frontend code.

**Test Steps:**
1. List folder IDs from context files
2. List folder IDs from frontend mockData.ts
3. Compare for consistency
4. Check case studies for folder references

**Expected Results:**
- Folder IDs match between backend and frontend
- No missing folders
- Consistent naming convention
- Frontend can find context for every folder

**Notes:**
- Critical for proper context loading
- Mismatch breaks context hierarchy

---

## Automated Test Implementation

### JSON Schema Validation (Python)

**File:** `backend/tests/test_context_schemas.py`

```python
import pytest
import json
from pathlib import Path

CONTEXTS_DIR = Path("backend/data/contexts")

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_case_instance_schema():
    """Test case-instance context schema compliance"""
    context = load_json(CONTEXTS_DIR / "cases/ACTE-2024-001/case.json")

    # Required keys
    assert "schemaVersion" in context
    assert context["schemaVersion"] == "1.0"

    assert "caseId" in context  # NEW: Case-specific ID
    assert context["caseId"] == "ACTE-2024-001"  # Matches directory
    assert "caseType" in context
    assert context["caseType"] == "integration_course"
    assert "name" in context
    assert "description" in context
    assert "regulations" in context
    assert "requiredDocuments" in context
    assert "validationRules" in context
    assert "commonIssues" in context

    # Array lengths
    assert len(context["regulations"]) >= 5
    assert len(context["requiredDocuments"]) >= 10
    assert len(context["validationRules"]) >= 8

def test_case_specific_folder_contexts():
    """Test all folder contexts within a case have required fields"""
    case_id = "ACTE-2024-001"
    folder_files = [
        "personal-data.json",
        "certificates.json",
        "integration-docs.json",
        "applications.json",
        "emails.json",
        "evidence.json"
    ]

    folder_ids = set()

    for filename in folder_files:
        context = load_json(CONTEXTS_DIR / f"cases/{case_id}/folders/{filename}")

        assert "folderId" in context
        assert "folderName" in context
        assert "purpose" in context
        assert "expectedDocuments" in context
        assert "validationCriteria" in context

        # Check for duplicate IDs within this case
        assert context["folderId"] not in folder_ids
        folder_ids.add(context["folderId"])

    # Verify we got 6 unique IDs
    assert len(folder_ids) == 6

def test_multiple_cases_isolation():
    """Test that multiple cases have separate, isolated contexts"""
    context1 = load_json(CONTEXTS_DIR / "cases/ACTE-2024-001/case.json")
    context2 = load_json(CONTEXTS_DIR / "cases/ACTE-2024-002/case.json")

    # Different case IDs
    assert context1["caseId"] == "ACTE-2024-001"
    assert context2["caseId"] == "ACTE-2024-002"

    # Can have different case types
    assert "caseType" in context1
    assert "caseType" in context2
    # Optionally assert they're different if testing different types

def test_regulation_structure():
    """Test regulation objects have required fields"""
    context = load_json(CONTEXTS_DIR / "cases/ACTE-2024-001/case.json")

    for regulation in context["regulations"]:
        assert "id" in regulation
        assert "title" in regulation
        assert "summary" in regulation
        assert len(regulation["summary"]) > 20  # Not empty/trivial

def test_case_template_structure():
    """Test template context has correct structure for case creation"""
    template = load_json(CONTEXTS_DIR / "templates/integration_course/case.json")

    # Template should not have caseId yet (added during creation)
    assert "caseType" in template
    assert template["caseType"] == "integration_course"
    assert "name" in template
    assert "regulations" in template

def test_file_sizes():
    """Test context files are under size limits"""
    case_file = CONTEXTS_DIR / "cases/ACTE-2024-001/case.json"
    size = case_file.stat().st_size

    assert size < 100 * 1024, f"Case context too large: {size} bytes"

def test_json_validity():
    """Test all JSON files are valid"""
    all_files = list(CONTEXTS_DIR.rglob("*.json"))

    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {file_path}: {e}")

def test_utf8_encoding():
    """Test German characters preserved"""
    context = load_json(CONTEXTS_DIR / "case_types/integration_course.json")
    json_str = json.dumps(context, ensure_ascii=False)

    # Check if German characters present and preserved
    # This would fail if encoding issues exist
    assert "§" in json_str or "Aufenthalt" in json_str or "ä" in json_str or "ü" in json_str
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Unit | 7 | 6 | 1 | 0 |
| Schema Compliance | 3 | 2 | 1 | 0 |
| Data Quality | 2 | 0 | 2 | 0 |
| Consistency | 2 | 0 | 2 | 0 |
| Performance | 1 | 0 | 1 | 0 |
| **Total** | **15** | **8** | **7** | **0** |

---

## Test Execution Checklist

- [ ] All 7 context JSON files created
- [ ] Files contain required data as per schema
- [ ] JSON syntax validated
- [ ] Schema version set to "1.0"
- [ ] Regulations array complete (5+ items)
- [ ] Required documents defined (10+ items)
- [ ] Validation rules specified (8+ items)
- [ ] Folder contexts complete (all 6)
- [ ] Folder IDs unique and consistent
- [ ] File sizes under limits (<100KB)
- [ ] German text and special characters preserved
- [ ] Content quality reviewed
- [ ] Cross-file consistency verified
- [ ] Automated tests passing
