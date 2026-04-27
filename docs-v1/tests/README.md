# BAMF AI Case Management System - Test Documentation

## Overview

This directory contains comprehensive test documentation for Sprint 1 of the BAMF AI Case Management System. The test suite covers functional requirements, non-functional requirements, and data requirements with a focus on quality, maintainability, and thorough coverage.

## Test Strategy

### Test Types

1. **Unit Tests**: Test individual components and functions in isolation
2. **Integration Tests**: Test interactions between components and services
3. **End-to-End (E2E) Tests**: Test complete user workflows from UI to backend
4. **Performance Tests**: Validate response times and system performance under load
5. **Manual Tests**: Human validation of UI/UX and complex scenarios

### Test Categories

Each requirement includes tests for:
- **Happy Path**: Normal operation with valid inputs
- **Edge Cases**: Boundary conditions, empty states, unusual but valid scenarios
- **Error Handling**: Invalid inputs, missing data, network failures, API errors
- **Integration**: Cross-component interactions and data flow
- **Performance**: Response times, load handling where applicable
- **Internationalization**: German/English language support

### Test Priority Levels

- **High**: Critical functionality, must pass before deployment
- **Medium**: Important features, should pass before release
- **Low**: Nice-to-have validations, can be deferred if needed

## Directory Structure

```
docs/tests/
├── README.md                           # This file
├── test-matrix.md                      # Test coverage matrix and summary
├── functional/                         # Functional requirement tests
│   ├── F-001-tests.md                 # Document Assistant Agent tests
│   ├── F-002-tests.md                 # Document Context Management tests
│   ├── F-003-tests.md                 # Form Auto-Fill tests
│   ├── F-004-tests.md                 # AI-Powered Field Generator tests
│   ├── F-005-tests.md                 # Case-Level Form Management tests
│   └── F-006-tests.md                 # Replace Mock Documents tests
├── non-functional/                     # Non-functional requirement tests
│   ├── NFR-001-tests.md               # Performance tests
│   ├── NFR-002-tests.md               # Architecture tests
│   └── NFR-003-tests.md               # Storage tests
└── data/                               # Data requirement tests
    ├── D-001-tests.md                 # Context Schema tests
    ├── D-002-tests.md                 # Form Schema tests
    └── D-003-tests.md                 # Sample Document tests
```

## Test Execution

### Automated Tests

Run automated tests using:

```bash
# Backend Python tests
cd backend
python -m pytest tests/

# Frontend TypeScript tests
npm run test

# End-to-end Playwright tests
npm run test:e2e
```

### Manual Tests

Manual test procedures are documented in each requirement's test file. Follow the step-by-step instructions and verify expected results.

## Test Environment

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Google Gemini API key configured in `.env`
- Playwright browsers installed (`npx playwright install`)

### Test Data

Sample documents and configuration files are located in:
- `/public/documents/{caseId}/{folderId}/` - Case-specific sample text files (e.g., `/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`)
- `/backend/data/contexts/cases/{caseId}/` - Case-specific context configuration JSON files
- `/backend/data/contexts/templates/{caseType}/` - Templates for creating new cases
- `/src/data/mockData.ts` - Mock data for frontend testing

### Case-Instance Scoping Architecture

**Key Changes:**
- **Context Files**: Each case has its own context directory at `backend/data/contexts/cases/{caseId}/`
  - Example: `cases/ACTE-2024-001/case.json`
  - Folder contexts: `cases/{caseId}/folders/{folderId}.json`

- **Documents**: Each case has its own document directory at `public/documents/{caseId}/{folderId}/`
  - Example: `documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`

- **WebSocket**: Case-specific endpoints: `ws://localhost:8000/ws/chat/{caseId}`

- **Case Isolation**:
  - Complete data isolation between cases
  - Cannot access documents or context from other cases
  - Each case maintains independent form data

- **New Case Creation**:
  - New cases created from templates at `backend/data/contexts/templates/{caseType}/`
  - Document templates at `public/documents/templates/`

**Testing Focus:**
- Case switching: Verify context and documents reload correctly
- Case isolation: Verify cases cannot access each other's data
- New case creation: Verify templates work correctly

### Test Configuration

Test configuration files:
- `jest.config.js` - Jest configuration for frontend unit tests
- `playwright.config.ts` - Playwright E2E test configuration
- `pytest.ini` - Python test configuration
- `.env.test` - Test environment variables

## Test Reporting

### Coverage Goals

- **Unit Test Coverage**: Minimum 80% code coverage
- **Integration Test Coverage**: All critical paths covered
- **E2E Test Coverage**: All user workflows tested
- **API Test Coverage**: All endpoints tested with happy path and error cases

### Test Reports

Test execution generates reports in:
- `coverage/` - Code coverage reports
- `test-results/` - Playwright test results
- `pytest-report.html` - Python test report

## Test Maintenance

### Adding New Tests

1. Identify the requirement ID (F-XXX, NFR-XXX, or D-XXX)
2. Add test cases to the appropriate test file
3. Implement automated test code if applicable
4. Update test-matrix.md with new test counts

### Test Review Process

1. All new features must include test cases
2. Test cases reviewed during code review
3. Failed tests block deployment
4. Test results tracked in sprint retrospectives

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Clear Naming**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Follow AAA pattern for test structure
4. **Test Data**: Use realistic test data that reflects production scenarios
5. **Error Messages**: Assert on specific error messages, not just error presence
6. **Cleanup**: Always clean up test data and restore state after tests
7. **Documentation**: Keep test documentation in sync with test implementation

## Known Issues and Limitations

### POC Phase Limitations

- No database persistence testing (using localStorage and filesystem)
- No concurrent user testing (single user assumed)
- No production-scale performance testing
- Limited internationalization testing (German and English only)

### Future Test Enhancements

- Load testing with multiple concurrent users
- Security testing (authentication, authorization)
- Accessibility testing (WCAG compliance)
- Browser compatibility testing (currently Chrome/Chromium only)
- Mobile responsive testing

## Contact

For questions about testing strategy or test execution, contact the development team.

## References

- Project Requirements: `docs/requirements/requirements.md`
- Implementation Plan: `docs/implementation_plan.md`
- API Documentation: `docs/api/`
- Architecture Documentation: `docs/architecture/`
