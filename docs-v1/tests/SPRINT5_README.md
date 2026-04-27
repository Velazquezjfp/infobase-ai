# Sprint 5 Test Suite

## Overview

This directory contains comprehensive test cases for all Sprint 5 requirements. Sprint 5 introduces advanced AI-powered form management with SHACL validation, multi-language support, improved document processing workflows, and enhanced file management.

**Generated**: 2026-01-09T16:30:00Z
**Total Requirements**: 13
**Total Test Cases**: 174
**Test Framework**: Python + Playwright (for UI tests) + API tests

---

## Test Structure

Each requirement has its own directory under `docs/tests/S5-XXX/` containing:
- Individual test case files (`TC-S5-XXX-01.py`, `TC-S5-XXX-02.py`, etc.)
- `test-results.json` - Test execution tracking file

---

## Requirements Coverage

### S5-001: Natural Language Form Field Modification with SHACL Validation
- **Directory**: `/docs/tests/S5-001/`
- **Test Cases**: 12
- **Type**: Playwright (UI tests)
- **Coverage**: Natural language form modification, SHACL shape generation, validation patterns

**Key Features Tested**:
- Natural language processing for form field creation
- Automatic SHACL PropertyShape generation
- Real-time SHACL shape synchronization
- Client-side validation with pattern matching
- Field operations (add, remove, modify)

---

### S5-002: AI Form Fill with Suggested Values and UX Module
- **Directory**: `/docs/tests/S5-002/`
- **Test Cases**: 12
- **Type**: Playwright (UI tests)
- **Coverage**: AI-powered form filling, suggestion UX, value comparison

**Key Features Tested**:
- Intelligent form field value suggestions
- Inline suggestion display with accept/reject actions
- Confidence score presentation
- Multiple simultaneous suggestions
- Suggestion state management

---

### S5-003: Semantic Search with Multi-Language Support
- **Directory**: `/docs/tests/S5-003/`
- **Test Cases**: 14
- **Type**: Playwright (UI tests)
- **Coverage**: Semantic search, multi-language matching, text highlighting

**Key Features Tested**:
- Semantic search powered by Gemini AI
- Multi-language query-document matching
- Text highlighting and navigation
- PDF text extraction and search
- Cross-language semantic understanding

---

### S5-004: Multi-Format Translation Service
- **Directory**: `/docs/tests/S5-004/`
- **Test Cases**: 14
- **Type**: API tests
- **Coverage**: Document translation (text, images, PDFs), render creation

**Key Features Tested**:
- Text document translation
- Image text overlay translation
- PDF layout-preserving translation
- Multiple language support
- Translation render management

---

### S5-005: Case Validation Agent
- **Directory**: `/docs/tests/S5-005/`
- **Test Cases**: 14
- **Type**: API tests
- **Coverage**: Case validation, document matching, requirement checking

**Key Features Tested**:
- AI-powered case validation
- Multi-language document name matching
- Required vs optional document tracking
- Folder-scoped validation
- Validation report generation

---

### S5-006: Document Renders Management System
- **Directory**: `/docs/tests/S5-006/`
- **Test Cases**: 14
- **Type**: Playwright (UI tests)
- **Coverage**: Render management, UI interactions, metadata tracking

**Key Features Tested**:
- Document render creation and display
- Collapsible render containers
- Render type icons and badges
- Render deletion functionality
- Metadata persistence

---

### S5-007: Container-Compatible File Persistence
- **Directory**: `/docs/tests/S5-007/`
- **Test Cases**: 12
- **Type**: API tests
- **Coverage**: File persistence, manifest management, container compatibility

**Key Features Tested**:
- Document registry and manifest
- Startup document tree rebuild
- File system synchronization
- Orphaned file detection
- Container restart persistence

---

### S5-008: Email File Support (.eml)
- **Directory**: `/docs/tests/S5-008/`
- **Test Cases**: 14
- **Type**: Playwright (UI tests)
- **Coverage**: Email parsing, display, translation

**Key Features Tested**:
- .eml file upload and parsing
- Email metadata extraction
- Email body rendering (HTML and plain text)
- Email translation
- Attachment handling

---

### S5-009: Improved Chat Information Presentation
- **Directory**: `/docs/tests/S5-009/`
- **Test Cases**: 14
- **Type**: Playwright (UI tests)
- **Coverage**: Message formatting, markdown rendering, HTML sanitization

**Key Features Tested**:
- Markdown rendering support
- HTML sanitization
- Code block syntax highlighting
- Message aggregation
- Link rendering with security

---

### S5-010: Optional Persistent Chat History
- **Directory**: `/docs/tests/S5-010/`
- **Test Cases**: 12
- **Type**: API tests
- **Coverage**: Conversation history, context management, token budget

**Key Features Tested**:
- In-memory conversation history
- Context window management
- Token budget tracking
- Feature flag support
- History clearing

---

### S5-011: Cascading Context with Document Tree View
- **Directory**: `/docs/tests/S5-011/`
- **Test Cases**: 14
- **Type**: API tests
- **Coverage**: Document tree generation, AI context awareness

**Key Features Tested**:
- Document tree view generation
- Hierarchical folder structure display
- AI prompt context inclusion
- Auto-refresh on document changes
- Tree-based document queries

---

### S5-012: Document Type Capabilities and Command Availability
- **Directory**: `/docs/tests/S5-012/`
- **Test Cases**: 14
- **Type**: Playwright (UI tests)
- **Coverage**: Document type restrictions, capability validation

**Key Features Tested**:
- Document capability matrix
- Dynamic toolbar button states
- Capability validation middleware
- Disabled button tooltips
- AI awareness of restrictions

---

### S5-013: Enhanced Acte Context Research
- **Directory**: `/docs/tests/S5-013/`
- **Test Cases**: 14
- **Type**: API tests
- **Coverage**: Context enrichment, regulation references, validation rules

**Key Features Tested**:
- Comprehensive context schema
- Required documents with specifications
- Regulation references
- Common issues and solutions
- Context versioning

---

## Running Tests

### Run All Sprint 5 Tests
```bash
# Run all tests
python -m pytest docs/tests/S5-*/TC-*.py

# Run with verbose output
python -m pytest -v docs/tests/S5-*/TC-*.py
```

### Run Tests for Specific Requirement
```bash
# Example: Run S5-001 tests
python -m pytest docs/tests/S5-001/TC-*.py

# Run specific test case
python docs/tests/S5-001/TC-S5-001-01.py
```

### Run Tests by Type
```bash
# Run only Playwright tests
python -m pytest docs/tests/S5-001/ docs/tests/S5-002/ docs/tests/S5-003/ docs/tests/S5-006/ docs/tests/S5-008/ docs/tests/S5-009/ docs/tests/S5-012/

# Run only API tests
python -m pytest docs/tests/S5-004/ docs/tests/S5-005/ docs/tests/S5-007/ docs/tests/S5-010/ docs/tests/S5-011/ docs/tests/S5-013/
```

---

## Test Status Tracking

Each requirement has a `test-results.json` file that tracks:
- Test execution status (not_run / passed / failed)
- Last execution timestamp
- Summary counts (total, passed, failed, not_run)

### View Test Status
```bash
# View S5-001 test results
cat docs/tests/S5-001/test-results.json | jq .

# View summary for all S5 requirements
for dir in docs/tests/S5-*; do
  echo "=== $(basename $dir) ==="
  jq '.summary' $dir/test-results.json
done
```

---

## Test Implementation Guidelines

### Playwright Tests
For requirements with UI components (S5-001, S5-002, S5-003, S5-006, S5-008, S5-009, S5-012):
1. Use MCP Playwright for browser automation
2. Navigate to the appropriate UI component
3. Perform user actions (clicks, inputs, etc.)
4. Verify UI state and visual elements
5. Check network requests and responses

### API Tests
For requirements with backend endpoints (S5-004, S5-005, S5-007, S5-010, S5-011, S5-013):
1. Send HTTP requests to backend endpoints
2. Verify response status codes
3. Validate response data structure
4. Check database state if applicable
5. Verify side effects

### Test Template
Each test file follows this structure:
```python
"""
Test Case: TC-S5-XXX-YY
Requirement: S5-XXX - Title
Description: Test case description
Generated: 2026-01-09T16:30:00Z
"""

def test_TC_S5_XXX_YY():
    """Test description"""
    # TODO: Implement test logic
    # Steps:
    # 1. Setup
    # 2. Execute
    # 3. Verify
    # 4. Cleanup
    pass

if __name__ == "__main__":
    try:
        test_TC_S5_XXX_YY()
        print("TC-S5-XXX-YY: PASSED")
    except AssertionError as e:
        print(f"TC-S5-XXX-YY: FAILED - {e}")
    except Exception as e:
        print(f"TC-S5-XXX-YY: ERROR - {e}")
```

---

## Test Dependencies

### Python Packages
```bash
pip install pytest playwright pytest-playwright requests
```

### Playwright Setup
```bash
# Install Playwright browsers
playwright install
```

### MCP Playwright
Ensure MCP Playwright server is configured in `.claude/settings.local.json`

---

## Test Coverage Matrix

| Requirement | UI Tests | API Tests | Total | Status |
|------------|----------|-----------|-------|--------|
| S5-001     | 12       | 0         | 12    | ⏳ Not Run |
| S5-002     | 12       | 0         | 12    | ⏳ Not Run |
| S5-003     | 14       | 0         | 14    | ⏳ Not Run |
| S5-004     | 0        | 14        | 14    | ⏳ Not Run |
| S5-005     | 0        | 14        | 14    | ⏳ Not Run |
| S5-006     | 14       | 0         | 14    | ⏳ Not Run |
| S5-007     | 0        | 12        | 12    | ⏳ Not Run |
| S5-008     | 14       | 0         | 14    | ⏳ Not Run |
| S5-009     | 14       | 0         | 14    | ⏳ Not Run |
| S5-010     | 0        | 12        | 12    | ⏳ Not Run |
| S5-011     | 0        | 14        | 14    | ⏳ Not Run |
| S5-012     | 14       | 0         | 14    | ⏳ Not Run |
| S5-013     | 0        | 14        | 14    | ⏳ Not Run |
| **TOTAL**  | **94**   | **80**    | **174** | ⏳ Not Run |

---

## Next Steps

1. **Implement Test Logic**: Replace TODO comments with actual test implementations
2. **Set Up Test Environment**: Configure test databases, mock services, etc.
3. **Execute Tests**: Run tests and update test-results.json files
4. **Fix Failures**: Address any failing tests
5. **CI/CD Integration**: Add tests to continuous integration pipeline

---

## Related Documentation

- **Requirements**: `/docs/requirements/sprint5_requirements.md`
- **Implementation Plan**: (To be created)
- **API Documentation**: (Refer to backend/api/ source files)

---

## Notes

- All test files include TODO comments with specific implementation guidance
- Test files reference specific source files and endpoints from the requirements
- Each test includes clear steps for implementation
- Test-results.json files are ready for status tracking
- Tests follow Python best practices and naming conventions

---

**Maintainer**: Bone Test Agent
**Last Updated**: 2026-01-09T16:30:00Z
