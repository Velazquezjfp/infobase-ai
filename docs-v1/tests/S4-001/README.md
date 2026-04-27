# Test Cases for S4-001: Drag-and-Drop File Upload

## Overview
This directory contains comprehensive test cases for requirement S4-001 (Drag-and-Drop File Upload functionality).

## Test Categories

### Backend API Tests (Python/pytest)
Automated integration tests for the file upload API endpoints:
- TC-S4-001-02: Valid file upload (5 MB)
- TC-S4-001-03: Oversized file rejection (20 MB)
- TC-S4-001-04: Multiple file upload
- TC-S4-001-07: Network error handling
- TC-S4-001-08: File appears in uploads folder
- TC-S4-001-09: Filename sanitization
- TC-S4-001-10: Duplicate filename handling

### UI/Frontend Tests (Manual/Playwright)
Tests requiring UI automation or manual verification:
- TC-S4-001-01: Drag hover indicator
- TC-S4-001-05: Progress tracking
- TC-S4-001-06: Success toast notification

## Prerequisites

### Backend Setup
1. Backend server must be running at http://localhost:8000
2. File upload endpoint /api/files/upload must be implemented
3. Required backend dependencies:
   - FastAPI
   - python-multipart
   - File service implementation

### Test Environment Setup
1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure uploads folder structure exists:
   ```bash
   mkdir -p public/documents/ACTE-2024-001/uploads
   ```

3. Verify backend health:
   ```bash
   curl http://localhost:8000/health
   ```

## Running Tests

### Run All Backend Tests
```bash
cd /home/ayanm/projects/info-base/infobase-ai/docs/tests/S4-001
pytest -v
```

### Run Specific Test
```bash
pytest TC-S4-001-02-valid-file-upload.py -v
```

### Run Tests with Coverage
```bash
pytest --cov=backend/api/files --cov=backend/services/file_service -v
```

### Skip Manual Tests
```bash
pytest -v -m "not manual"
```

## Test Results Location
Test execution results are documented in:
```
docs/tests/S4-001/test-results.json
```

## Expected Behavior

### File Size Validation
- Files under 15 MB: Accepted and uploaded
- Files 15 MB or over: Rejected with 413 status code

### File Storage
- Files saved to: `public/documents/{caseId}/uploads/{filename}`
- Uploads folder created automatically if it doesn't exist

### Security
- Filenames sanitized to prevent path traversal
- Files confined to case-specific directories
- Malicious filenames rejected or sanitized

### Error Handling
- Network errors: Connection error raised, UI shows error toast
- Oversized files: 413 status with clear error message
- Invalid filenames: Sanitized or rejected

## Notes
- Manual/UI tests (TC-S4-001-01, 05, 06) require Playwright automation or manual execution
- All Python tests use temporary files that are cleaned up automatically
- Tests verify both API responses and filesystem state
