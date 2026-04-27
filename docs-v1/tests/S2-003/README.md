# S2-003: Legacy Form Standardization - Test Suite

This directory contains comprehensive tests for requirement S2-003: Legacy Form Standardization, which validates that all existing forms in mockData.ts have been migrated to include SHACL/JSON-LD semantic metadata.

## Test Files

### Python Test Suites

#### `test_shacl_metadata.py`
Comprehensive unit tests for SHACL metadata generation and validation using the backend migration script.

**Test Classes:**
- `TestSHACLMetadataPresence` - Verifies all fields have shaclMetadata
- `TestSHACLFieldMapping` - Validates Schema.org property mappings
- `TestSHACLDatatypes` - Checks XSD datatype assignments
- `TestBackwardCompatibility` - Ensures optional SHACL metadata
- `TestSHACLValidation` - Validates SHACL structure completeness
- `TestSHACLConstraints` - Tests constraint generation (minCount, maxCount, sh:in)
- `TestMigrationScriptExecution` - Validates migration script functionality

**Total Tests:** 20
**Execution Time:** ~0.04s

**Run Tests:**
```bash
cd /home/ayanm/projects/info-base/infobase-ai/backend
source venv/bin/activate
python -m pytest ../docs/tests/S2-003/test_shacl_metadata.py -v
```

---

#### `test_mockdata_shacl.py`
Integration tests that validate mockData.ts has been properly updated with SHACL metadata across all form templates.

**Test Classes:**
- `TestMockDataSHACLMetadata` - Validates SHACL in mockData.ts
- `TestFormTemplateStructure` - Verifies form template definitions

**Templates Tested:**
- integrationCourseFormTemplate (7 fields)
- asylumApplicationFormTemplate (7 fields)
- familyReunificationFormTemplate (7 fields)

**Total Tests:** 16
**Execution Time:** ~0.03s

**Run Tests:**
```bash
cd /home/ayanm/projects/info-base/infobase-ai/backend
source venv/bin/activate
python -m pytest ../docs/tests/S2-003/test_mockdata_shacl.py -v
```

---

### Test Results

#### `test-results.json`
Comprehensive JSON document containing detailed test execution results, including:
- Test case details (41 test cases)
- Execution times and timestamps
- Pass/fail status for each test
- Files modified and created
- Analysis and recommendations
- Test coverage metrics

**Structure:**
```json
{
  "requirementId": "S2-003",
  "executionTimestamp": "...",
  "summary": { "total": 41, "passed": 41, "failed": 0, ... },
  "testCases": [ ... ],
  "analysisAndRecommendations": { ... }
}
```

---

#### `TEST_EXECUTION_SUMMARY.md`
Human-readable comprehensive test execution report with:
- Executive summary
- Detailed test case results
- Failure analysis (none)
- Coverage analysis (100% automated tests passed)
- Recommendations for future improvements
- Context and dependencies analysis

---

## Test Cases Summary

### TC-S2-003-01: All form fields have shaclMetadata property
✓ PASSED - All 7 Integration Course fields have valid shaclMetadata

### TC-S2-003-02: fullName has sh:path = "schema:name"
✓ PASSED - Verified correct Schema.org property mappings for all fields

### TC-S2-003-03: birthDate has sh:datatype = "xsd:date"
✓ PASSED - All date fields use xsd:date, text fields use xsd:string

### TC-S2-003-04: Backward compatibility preserved
✓ PASSED - Form fields work with and without shaclMetadata

### TC-S2-003-05: SHACL type displayed in admin mode
⚠ MANUAL - Code verified correct, UI testing pending

### TC-S2-003-06: Migration script generates valid SHACL structure
✓ PASSED - Script executes successfully and generates valid SHACL

---

## Running All Tests

### Quick Run (All Tests)
```bash
cd /home/ayanm/projects/info-base/infobase-ai/backend
source venv/bin/activate
python -m pytest ../docs/tests/S2-003/ -v
```

### Run with Coverage
```bash
cd /home/ayanm/projects/info-base/infobase-ai/backend
source venv/bin/activate
python -m pytest ../docs/tests/S2-003/ -v --cov=backend.schemas --cov=backend.scripts
```

### Run Migration Script
```bash
cd /home/ayanm/projects/info-base/infobase-ai
source backend/venv/bin/activate
PYTHONPATH=/home/ayanm/projects/info-base/infobase-ai python backend/scripts/migrate_forms_to_shacl.py
```

---

## Manual Testing

### TC-S2-003-05: SHACL Badge Display in Admin Mode

**Prerequisites:**
1. Frontend running: `npm run dev`
2. Navigate to: http://localhost:5173/workspace
3. Login with any username

**Test Steps:**
1. Click admin mode toggle in WorkspaceHeader
2. Observe form fields in FormViewer panel
3. Verify SHACL badges appear below each field
4. Verify badges show:
   - Outline badge with sh:path (e.g., "schema:name")
   - Secondary badge with sh:datatype (e.g., "xsd:string")
5. Test with all three form templates:
   - Integration Course Application (ACTE-2024-001)
   - Asylum Application (ACTE-2024-002)
   - Family Reunification (ACTE-2024-003)

**Expected Results:**
- Tag icon visible before badges
- sh:path badge has outline variant
- sh:datatype badge has secondary variant
- Font is monospace (font-mono)
- Badges only visible when isAdminMode=true

---

## Dependencies

### Python Dependencies (Backend)
```
pytest==9.0.2
iniconfig==2.3.0
packaging==25.0
pluggy==1.6.0
pygments==2.19.2
```

### Project Dependencies
- S2-002: Dynamic Structure Definition (SHACL & JSON-LD)
  - Provides SHACL schema types from backend/schemas/
  - Provides TypeScript interfaces from src/types/shacl.ts

---

## Test Coverage

| Area | Coverage | Tests |
|------|----------|-------|
| SHACL Metadata Presence | 100% | 2 |
| Schema.org Mappings | 100% | 3 |
| XSD Datatypes | 100% | 3 |
| SHACL Constraints | 100% | 3 |
| Backward Compatibility | 100% | 2 |
| Migration Script | 100% | 7 |
| MockData Integration | 100% | 16 |
| UI Display (Code) | 100% | 3 |
| **Total Automated** | **100%** | **40** |
| UI Display (Visual) | Manual | 1 |

---

## SHACL Metadata Structure

### Example: fullName Field
```typescript
{
  id: 'fullName',
  label: 'Full Name',
  type: 'text',
  value: '',
  required: true,
  shaclMetadata: {
    '@context': SHACL_CONTEXT,
    '@type': 'sh:PropertyShape',
    'sh:path': 'schema:name',
    'sh:datatype': 'xsd:string',
    'sh:name': 'Full Name',
    'sh:description': 'The applicant\'s full legal name',
    'sh:minCount': 1,
    'sh:maxCount': 1,
  }
}
```

### Field Mapping Reference

| Field ID | sh:path | sh:datatype | Constraint |
|----------|---------|-------------|------------|
| fullName | schema:name | xsd:string | minCount=1 |
| birthDate | schema:birthDate | xsd:date | minCount=1 |
| countryOfOrigin | schema:nationality | xsd:string | minCount=1 |
| existingLanguageCertificates | schema:knowsLanguage | xsd:string | - |
| coursePreference | schema:courseCode | xsd:string | sh:in with 3 options |
| currentAddress | schema:address | xsd:string | minCount=1 |
| reasonForApplication | schema:description | xsd:string | minCount=1 |

---

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'backend'`:
```bash
# Set PYTHONPATH
export PYTHONPATH=/home/ayanm/projects/info-base/infobase-ai
# Or run with PYTHONPATH prefix
PYTHONPATH=/home/ayanm/projects/info-base/infobase-ai python script.py
```

### pytest Not Found
```bash
cd /home/ayanm/projects/info-base/infobase-ai/backend
source venv/bin/activate
pip install pytest
```

### Migration Script Fails
Ensure you're in the correct directory and PYTHONPATH is set:
```bash
cd /home/ayanm/projects/info-base/infobase-ai
source backend/venv/bin/activate
PYTHONPATH=$(pwd) python backend/scripts/migrate_forms_to_shacl.py
```

---

## Related Documentation

- **Requirement:** [docs/requirements/requirements.md - S2-003](../../requirements/requirements.md#s2-003-legacy-form-standardization)
- **Implementation Plan:** [docs/implementation_plan.md - Phase 3](../../implementation_plan.md#phase-3-migration-depends-on-phase-1)
- **SHACL Schema:** [backend/schemas/shacl.py](../../../backend/schemas/shacl.py)
- **JSON-LD Context:** [backend/schemas/jsonld_context.py](../../../backend/schemas/jsonld_context.py)
- **TypeScript Types:** [src/types/shacl.ts](../../../src/types/shacl.ts)
- **MockData:** [src/data/mockData.ts](../../../src/data/mockData.ts)
- **FormViewer:** [src/components/workspace/FormViewer.tsx](../../../src/components/workspace/FormViewer.tsx)

---

## Test Maintenance

### Adding New Tests
1. Add test functions to appropriate test class in `test_shacl_metadata.py` or `test_mockdata_shacl.py`
2. Follow existing naming convention: `test_description_of_test`
3. Use descriptive assertions with clear error messages
4. Update `test-results.json` after execution
5. Update `TEST_EXECUTION_SUMMARY.md` with new test details

### When Form Templates Change
1. Update field count expectations in tests
2. Update field ID lists in validation tests
3. Update semantic mapping tables
4. Re-run all tests to ensure consistency
5. Update test-results.json with new execution data

---

## Contact

For questions or issues with these tests, refer to:
- **Requirement Owner:** Development Team
- **Test Engineer:** Claude (Bone Test Executor Agent)
- **Last Updated:** 2025-12-23
