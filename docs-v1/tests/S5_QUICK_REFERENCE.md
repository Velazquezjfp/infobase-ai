# Sprint 5 Tests - Quick Reference Guide

## Quick Commands

### Run All Sprint 5 Tests
```bash
python -m pytest docs/tests/S5-*/TC-*.py -v
```

### Run Specific Requirement Tests
```bash
# Example: S5-001
python -m pytest docs/tests/S5-001/ -v

# Example: S5-005
python -m pytest docs/tests/S5-005/ -v
```

### Run Single Test
```bash
python docs/tests/S5-001/TC-S5-001-01.py
```

### Check Test Status
```bash
# View test results for S5-001
cat docs/tests/S5-001/test-results.json | jq '.summary'

# View all S5 test summaries
for dir in docs/tests/S5-*; do
  echo "=== $(basename $dir) ==="
  jq '.summary' $dir/test-results.json
done
```

---

## Requirements at a Glance

| ID | Title | Tests | Type |
|---|---|---|---|
| **S5-001** | Natural Language Form Field Modification | 12 | UI |
| **S5-002** | AI Form Fill with Suggestions | 12 | UI |
| **S5-003** | Semantic Search Multi-Language | 14 | UI |
| **S5-004** | Multi-Format Translation | 14 | API |
| **S5-005** | Case Validation Agent | 14 | API |
| **S5-006** | Document Renders Management | 14 | UI |
| **S5-007** | Container-Compatible Persistence | 12 | API |
| **S5-008** | Email File Support (.eml) | 14 | UI |
| **S5-009** | Improved Chat Presentation | 14 | UI |
| **S5-010** | Persistent Chat History | 12 | API |
| **S5-011** | Cascading Context Tree View | 14 | API |
| **S5-012** | Document Type Capabilities | 14 | UI |
| **S5-013** | Enhanced Acte Context Research | 14 | API |

---

## Test Types

### UI Tests (Playwright)
Requirements: S5-001, S5-002, S5-003, S5-006, S5-008, S5-009, S5-012
Total: 94 tests

Run all UI tests:
```bash
python -m pytest docs/tests/S5-001/ docs/tests/S5-002/ docs/tests/S5-003/ docs/tests/S5-006/ docs/tests/S5-008/ docs/tests/S5-009/ docs/tests/S5-012/ -v
```

### API Tests
Requirements: S5-004, S5-005, S5-007, S5-010, S5-011, S5-013
Total: 80 tests

Run all API tests:
```bash
python -m pytest docs/tests/S5-004/ docs/tests/S5-005/ docs/tests/S5-007/ docs/tests/S5-010/ docs/tests/S5-011/ docs/tests/S5-013/ -v
```

---

## File Locations

**Test Files**: `/docs/tests/S5-XXX/TC-S5-XXX-YY.py`
**Test Results**: `/docs/tests/S5-XXX/test-results.json`
**Documentation**:
- `/docs/tests/SPRINT5_README.md` (detailed guide)
- `/SPRINT5_TEST_GENERATION_SUMMARY.md` (file inventory)
- `/docs/tests/S5_QUICK_REFERENCE.md` (this file)

**Requirements**: `/docs/requirements/sprint5_requirements.md`

---

## Key Features by Requirement

### S5-001: SHACL Validation
- Natural language form modification
- SHACL shape generation with schema.org
- Real-time validation patterns
- Email, phone, name, date field types

### S5-002: Form Fill Suggestions
- AI-powered value suggestions
- Inline suggestion UX with icons
- Confidence scores
- Accept/reject actions

### S5-003: Semantic Search
- Multi-language search (German ↔ English)
- Text highlighting
- Navigation between matches
- PDF text extraction

### S5-004: Translation Service
- Text document translation
- Image text overlay
- PDF layout-preserving translation
- Multi-format support

### S5-005: Validation Agent
- AI case validation
- Document name matching (multi-language)
- Required vs optional documents
- Validation reports

### S5-006: Render Management
- Multiple document renders (original, translated, anonymized)
- Collapsible render containers
- Render deletion
- Metadata tracking

### S5-007: File Persistence
- Document manifest
- Startup reconciliation
- Container compatibility
- File system sync

### S5-008: Email Support
- .eml file parsing
- Email metadata display
- HTML/plain text rendering
- Email translation

### S5-009: Chat Formatting
- Markdown rendering
- HTML sanitization
- Code syntax highlighting
- No message fragmentation

### S5-010: Chat History
- Optional conversation memory
- Context window management
- Token budget tracking
- Feature flag support

### S5-011: Context Tree View
- Document tree generation
- AI context awareness
- Auto-refresh on changes
- Hierarchical display

### S5-012: Document Capabilities
- Type-based command restrictions
- Dynamic toolbar states
- Capability validation
- Clear error messages

### S5-013: Enhanced Context
- Comprehensive context schema
- Regulation references
- Required documents with specs
- Common issues and solutions

---

## Implementation Priority

**High Priority** (Core functionality):
1. S5-007 - File Persistence (foundation)
2. S5-006 - Render Management (core feature)
3. S5-003 - Semantic Search (user value)
4. S5-005 - Validation Agent (user value)

**Medium Priority** (Enhanced features):
5. S5-001 - Form Field Modification
6. S5-004 - Translation Service
7. S5-008 - Email Support
8. S5-012 - Document Capabilities

**Lower Priority** (Nice to have):
9. S5-002 - Form Fill Suggestions
10. S5-009 - Chat Formatting
11. S5-011 - Context Tree View
12. S5-010 - Chat History (optional)
13. S5-013 - Enhanced Context (ongoing)

---

## Next Steps

1. Review test files and requirements
2. Set up test environment (databases, mocks)
3. Implement test logic (replace TODOs)
4. Execute tests
5. Update test-results.json files
6. Fix failures
7. Integrate into CI/CD

---

**Quick Access**:
- Full Documentation: `/docs/tests/SPRINT5_README.md`
- File Inventory: `/SPRINT5_TEST_GENERATION_SUMMARY.md`
- Requirements: `/docs/requirements/sprint5_requirements.md`
