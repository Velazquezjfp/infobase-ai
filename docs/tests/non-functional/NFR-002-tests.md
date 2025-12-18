# NFR-002: Modular Backend Architecture

## Test Cases

### TC-NFR-002-01: No Circular Dependencies

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify that the backend codebase has no circular import dependencies, ensuring clean module structure.

**Preconditions:**
- Backend project structure created
- All Python modules implemented
- Import statements finalized

**Test Steps:**
1. Run Python import analysis tool (e.g., `pydeps` or custom script)
2. Check for circular dependency errors
3. Manually attempt to import each module independently
4. Verify import order doesn't matter

**Expected Results:**
- Zero circular dependencies detected
- All modules importable independently
- Clean dependency graph
- API layer imports services, not vice versa
- Services import tools, not vice versa
- Data layer has no imports from other layers

**Test Data:**
N/A

**Notes:**
- Use command: `pydeps backend --show-cycles`
- Or: `python -m py_compile backend/**/*.py`

---

### TC-NFR-002-02: Service Initialization Without External Calls

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Test that service classes can be instantiated with mock dependencies without making external API calls.

**Preconditions:**
- Service classes implemented with dependency injection
- Mock objects available for dependencies

**Test Steps:**
1. Create mock API key: "mock_api_key_123"
2. Instantiate GeminiService with mock key
3. Verify no network calls made during __init__
4. Repeat for ContextManager and FieldGenerator services
5. Check no file I/O during initialization

**Expected Results:**
- All services instantiate successfully with mocks
- No HTTP requests during initialization
- No file reads during initialization
- Initialization completes in < 100ms
- Services ready for testing in isolation

**Test Data:**
```python
mock_api_key = "mock_api_key_123"
service = GeminiService(api_key=mock_api_key)
```

**Notes:**
- Enables unit testing without real dependencies
- Validates dependency injection pattern

---

### TC-NFR-002-03: Code Quality - Pylint Score

**Type:** Static Analysis
**Priority:** High
**Status:** Pending

**Description:**
Run pylint on the backend codebase and verify code quality score meets threshold.

**Preconditions:**
- Pylint installed: `pip install pylint`
- .pylintrc configuration file present (if custom rules)

**Test Steps:**
1. Run: `pylint backend/`
2. Review output for errors, warnings, conventions
3. Calculate overall score
4. Address critical issues (errors, major warnings)
5. Re-run until score meets threshold

**Expected Results:**
- Pylint score: ≥ 8.0/10
- Zero errors (E-level)
- Minimal warnings (W-level)
- Reasonable convention compliance
- All critical issues resolved

**Test Data:**
N/A

**Notes:**
- Configure pylint to ignore acceptable patterns
- Focus on critical issues first
- Score 8.0 indicates good code quality

---

### TC-NFR-002-04: Type Checking - Mypy Validation

**Type:** Static Analysis
**Priority:** High
**Status:** Pending

**Description:**
Run mypy type checker to verify type hints are correct and consistent throughout the backend.

**Preconditions:**
- Mypy installed: `pip install mypy`
- Type hints added to all function signatures
- mypy.ini configuration if needed

**Test Steps:**
1. Run: `mypy backend/`
2. Review type errors
3. Fix type hint inconsistencies
4. Add missing type hints
5. Re-run until zero errors
6. Verify --strict mode compatibility (optional)

**Expected Results:**
- Zero type errors
- All functions have type hints for parameters and return values
- Type consistency across codebase
- No `Any` types except where necessary
- Clean mypy output

**Test Data:**
N/A

**Notes:**
- Type hints improve code maintainability
- Catches potential bugs at development time
- Command: `mypy --strict backend/` for strictest checking

---

### TC-NFR-002-05: Docstring Completeness

**Type:** Documentation
**Priority:** Medium
**Status:** Pending

**Description:**
Verify all public functions and classes have complete docstrings with Args, Returns, and Raises sections.

**Preconditions:**
- Backend code complete
- Documentation standards defined (Google or NumPy style)

**Test Steps:**
1. Review each Python file in services/, tools/, api/
2. Check every public function has docstring
3. Verify docstring includes:
   - Description
   - Args section (if parameters)
   - Returns section (if not None)
   - Raises section (if exceptions raised)
4. Use pydocstyle or manual review

**Expected Results:**
- 100% of public functions documented
- Docstrings follow consistent style (Google style recommended)
- All parameters described
- Return values described
- Exceptions documented
- Examples provided for complex functions

**Test Data:**
Example expected format:
```python
def generate_response(prompt: str, context: str) -> str:
    """Generate AI response using Gemini API.

    Args:
        prompt: User's input prompt
        context: Additional context for the AI

    Returns:
        Generated response text from Gemini

    Raises:
        APIError: If Gemini API request fails
        ValueError: If prompt is empty
    """
```

**Notes:**
- Run: `pydocstyle backend/` for automated checking
- Manual review for quality

---

### TC-NFR-002-06: Dependency Version Pinning

**Type:** Configuration
**Priority:** High
**Status:** Pending

**Description:**
Verify all dependencies in requirements.txt are pinned to specific versions for reproducible builds.

**Preconditions:**
- requirements.txt created
- All dependencies identified

**Test Steps:**
1. Open backend/requirements.txt
2. Check each dependency line
3. Verify version pinning format: `package==version`
4. No loose version specifiers (>=, ~=, *)
5. Verify compatible versions

**Expected Results:**
- All dependencies pinned: `fastapi==0.104.1`
- No unpinned dependencies: ~~`fastapi`~~
- No loose pins: ~~`fastapi>=0.100`~~
- Versions tested and compatible
- No conflicting version requirements

**Test Data:**
Expected requirements.txt format:
```
fastapi==0.104.1
websockets==12.0
google-generativeai==0.3.1
python-dotenv==1.0.0
uvicorn==0.24.0
pydantic==2.5.0
```

**Notes:**
- Pinning ensures reproducible deployments
- Update pins when upgrading dependencies
- Test after any version changes

---

## Architecture Tests

### TC-NFR-002-ARCH01: Layer Separation Validation

**Type:** Architecture
**Priority:** High
**Status:** Pending

**Description:**
Verify clean separation between architecture layers: API, Service, Tools, Data.

**Test Steps:**
1. Review import statements in each layer
2. Check API layer only imports from Service layer
3. Verify Service layer only imports from Tools and Data
4. Confirm Tools layer is stateless with no layer imports
5. Validate Data layer has no code dependencies

**Expected Results:**
- API → Service imports only (allowed)
- Service → Tools, Data imports only (allowed)
- Tools → No layer imports (stateless functions)
- Data → No code imports (just data files)
- No backward imports (Service → API, etc.)
- Clear dependency direction: API → Service → Tools → Data

**Test Data:**
N/A

**Notes:**
- Use dependency visualization tool
- Document architecture rules

---

### TC-NFR-002-ARCH02: Single Responsibility Principle

**Type:** Code Review
**Priority:** Medium
**Status:** Pending

**Description:**
Review each module to ensure it has a single, well-defined responsibility.

**Test Steps:**
1. List all modules and their stated purpose
2. Review each module's functions
3. Check if module does one thing well
4. Identify any modules doing multiple unrelated things
5. Recommend refactoring if needed

**Expected Results:**
- GeminiService: Only Gemini API interaction
- ContextManager: Only context loading and merging
- FieldGenerator: Only field generation logic
- FormParser: Only form data extraction
- Each module focused and cohesive
- No "God classes" doing everything

**Test Data:**
N/A

**Notes:**
- SRP improves testability and maintainability
- Subjective but important principle

---

### TC-NFR-002-ARCH03: Dependency Injection Pattern

**Type:** Architecture
**Priority:** Medium
**Status:** Pending

**Description:**
Verify services use dependency injection for testability and flexibility.

**Test Steps:**
1. Review service class constructors
2. Check if dependencies passed as parameters
3. Verify no hard-coded dependencies
4. Test services with mock dependencies
5. Confirm interfaces or abstract base classes where appropriate

**Expected Results:**
- Services accept dependencies in __init__
- No hard-coded API keys or file paths
- Configuration injected, not imported
- Easy to substitute mocks for testing
- Clear dependency contracts

**Test Data:**
```python
# Good example:
class GeminiService:
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout

# Bad example (hard-coded):
class GeminiService:
    def __init__(self):
        self.api_key = "AIza..."  # Hard-coded!
```

**Notes:**
- DI enables testing and flexibility
- FastAPI has built-in DI support

---

## Code Organization Tests

### TC-NFR-002-ORG01: Directory Structure Compliance

**Type:** Configuration
**Priority:** High
**Status:** Pending

**Description:**
Verify backend project follows specified directory structure.

**Test Steps:**
1. Check directory tree matches specification
2. Verify required subdirectories exist
3. Confirm files in correct locations
4. Check for no misplaced files

**Expected Results:**
- Directory structure:
  ```
  backend/
  ├── api/
  │   ├── __init__.py
  │   ├── admin.py
  │   └── chat.py
  ├── services/
  │   ├── __init__.py
  │   ├── gemini_service.py
  │   ├── context_manager.py
  │   └── field_generator.py
  ├── tools/
  │   ├── __init__.py
  │   ├── form_parser.py
  │   └── document_processor.py
  ├── data/
  │   └── contexts/
  │       ├── case_types/
  │       └── folders/
  ├── tests/
  ├── main.py
  └── requirements.txt
  ```
- All __init__.py files present
- No files in wrong directories

**Test Data:**
N/A

**Notes:**
- Use tree command: `tree backend/`
- Consistent structure aids navigation

---

### TC-NFR-002-ORG02: Naming Conventions

**Type:** Code Review
**Priority:** Medium
**Status:** Pending

**Description:**
Verify consistent naming conventions following PEP 8.

**Test Steps:**
1. Review all file names (snake_case.py)
2. Check class names (PascalCase)
3. Verify function names (snake_case)
4. Check constants (UPPER_CASE)
5. Review variable names (snake_case)

**Expected Results:**
- Files: snake_case.py (gemini_service.py ✓)
- Classes: PascalCase (GeminiService ✓)
- Functions: snake_case (generate_response ✓)
- Constants: UPPER_CASE (API_TIMEOUT ✓)
- Private: _leading_underscore (_internal_method ✓)
- Consistent throughout codebase

**Test Data:**
N/A

**Notes:**
- PEP 8 is Python standard
- Consistency improves readability

---

## Testing Infrastructure

### TC-NFR-002-TEST01: Unit Test Coverage Setup

**Type:** Configuration
**Priority:** Medium
**Status:** Pending

**Description:**
Verify unit testing infrastructure is set up with pytest and coverage tools.

**Test Steps:**
1. Check pytest installed and configured
2. Verify pytest.ini or pyproject.toml configuration
3. Install coverage.py
4. Configure coverage settings
5. Run sample test to verify setup

**Expected Results:**
- pytest installed: `pytest --version`
- Configuration file present
- Coverage tool available: `coverage --version`
- Tests discoverable: `pytest --collect-only`
- Sample test runs successfully

**Test Data:**
N/A

**Notes:**
- Foundation for test-driven development
- Coverage targets: >80% for services, >90% for tools

---

### TC-NFR-002-TEST02: Fixture and Mock Setup

**Type:** Testing
**Priority:** Medium
**Status:** Pending

**Description:**
Verify common test fixtures and mocks are available for testing.

**Test Steps:**
1. Check conftest.py exists in tests/
2. Review common fixtures (test client, mock services)
3. Verify mock data available
4. Test fixture usage in sample test

**Expected Results:**
- conftest.py with common fixtures
- Mock Gemini client available
- Test case data fixtures
- Reusable across test files
- Well-documented fixtures

**Test Data:**
Example conftest.py:
```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_gemini_service():
    # Mock implementation
    pass
```

**Notes:**
- Fixtures reduce test code duplication
- Consistent test environment

---

## Documentation Tests

### TC-NFR-002-DOC01: README Completeness

**Type:** Documentation
**Priority:** Medium
**Status:** Pending

**Description:**
Verify backend README.md contains essential information for developers.

**Test Steps:**
1. Check backend/README.md exists
2. Verify sections present:
   - Project description
   - Installation instructions
   - Running the server
   - Environment variables
   - Testing instructions
   - Architecture overview
   - API documentation link

**Expected Results:**
- README.md present and complete
- Clear setup instructions
- Environment variables documented
- Examples provided
- Links to detailed docs

**Test Data:**
N/A

**Notes:**
- Essential for onboarding developers
- Keep synchronized with code changes

---

### TC-NFR-002-DOC02: API Documentation

**Type:** Documentation
**Priority:** High
**Status:** Pending

**Description:**
Verify API endpoints are documented (OpenAPI/Swagger).

**Test Steps:**
1. Start backend server
2. Navigate to http://localhost:8000/docs
3. Verify Swagger UI loads
4. Check all endpoints documented
5. Test "Try it out" functionality

**Expected Results:**
- Swagger UI accessible at /docs
- All endpoints listed
- Request/response schemas shown
- Descriptions for each endpoint
- Working interactive testing

**Test Data:**
N/A

**Notes:**
- FastAPI auto-generates from code
- Add descriptions using docstrings

---

## Performance and Scalability

### TC-NFR-002-PERF01: Import Time Optimization

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Measure Python module import times to ensure fast server startup.

**Test Steps:**
1. Measure backend startup time
2. Profile import times: `python -X importtime main.py`
3. Identify slow imports
4. Optimize if needed

**Expected Results:**
- Backend startup < 3 seconds
- No single import > 1 second
- Lazy imports for optional features
- Fast development iteration

**Test Data:**
N/A

**Notes:**
- Fast startup improves development experience
- Consider lazy imports for heavy libraries

---

## Automated Test Implementation

### Architecture Tests (Python)

**File:** `backend/tests/test_architecture.py`

```python
import pytest
import ast
import os
from pathlib import Path

def get_imports(file_path):
    """Extract imports from a Python file"""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def test_no_api_imports_in_tools():
    """Tools layer should not import from API layer"""
    tools_dir = Path("backend/tools")
    for py_file in tools_dir.glob("*.py"):
        imports = get_imports(py_file)
        api_imports = [imp for imp in imports if imp.startswith("backend.api")]
        assert len(api_imports) == 0, f"{py_file} imports from API layer: {api_imports}"

def test_no_service_imports_in_tools():
    """Tools layer should not import from Service layer"""
    tools_dir = Path("backend/tools")
    for py_file in tools_dir.glob("*.py"):
        imports = get_imports(py_file)
        service_imports = [imp for imp in imports if imp.startswith("backend.services")]
        assert len(service_imports) == 0, f"{py_file} imports from Service layer: {service_imports}"

def test_requirements_pinned():
    """All requirements should be pinned to specific versions"""
    with open("backend/requirements.txt") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            assert "==" in line, f"Dependency not pinned: {line}"

def test_all_services_have_docstrings():
    """All service classes should have docstrings"""
    services_dir = Path("backend/services")
    for py_file in services_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        with open(py_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                assert docstring, f"Class {node.name} in {py_file} missing docstring"
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Unit | 2 | 2 | 0 | 0 |
| Static Analysis | 2 | 2 | 0 | 0 |
| Documentation | 3 | 1 | 2 | 0 |
| Architecture | 3 | 1 | 2 | 0 |
| Code Organization | 2 | 1 | 1 | 0 |
| Testing Infrastructure | 2 | 0 | 2 | 0 |
| Documentation | 2 | 1 | 1 | 0 |
| Performance | 1 | 0 | 0 | 1 |
| **Total** | **17** | **8** | **8** | **1** |

---

## Test Execution Checklist

- [ ] Backend project structure created
- [ ] All modules implemented
- [ ] Pylint configured and run
- [ ] Mypy type checking passed
- [ ] Docstrings complete
- [ ] requirements.txt pinned
- [ ] Architecture rules documented
- [ ] Test infrastructure set up
- [ ] README documentation complete
- [ ] API documentation (Swagger) accessible
- [ ] Code review completed
- [ ] Architecture validated
