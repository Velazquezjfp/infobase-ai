# BAMF AI Case Management System - Test Coverage Matrix

## Executive Summary

This document provides a comprehensive overview of test coverage for Sprint 1 of the BAMF AI Case Management System with **Case-Instance Scoping Architecture**. The test suite includes 201+ total test cases across functional, non-functional, and data requirements, with additional tests for case isolation and case switching.

### Case-Instance Scoping Architecture

The system has been updated to use **case-instance scoping**, where each case (ACTE) has its own isolated:
- Context directory: `backend/data/contexts/cases/{caseId}/`
- Document directory: `public/documents/{caseId}/{folderId}/`
- WebSocket endpoint: `ws://localhost:8000/ws/chat/{caseId}`
- Form data storage

**Key Testing Focus Areas:**
- ✅ Case switching: Verify context and documents reload correctly
- ✅ Case isolation: Verify cases cannot access each other's data (security critical)
- ✅ New case creation: Verify creation from templates
- ✅ Path construction: All paths include {caseId} component

### Coverage Overview

| Category | Requirements | Test Cases | High Priority | Medium Priority | Low Priority |
|----------|-------------|------------|---------------|-----------------|--------------|
| **Functional** | 6 | 106+ | 50+ | 47 | 12 |
| **Non-Functional** | 3 | 49 | 20 | 23 | 6 |
| **Data** | 3 | 46+ | 30+ | 17 | 2 |
| **TOTAL** | **12** | **201+** | **100+** | **87** | **20** |

**Note:** Test counts increased to include case switching, case isolation, and template creation tests.

### Priority Distribution

- **High Priority (Critical)**: 100+ tests (49%) - includes critical case isolation tests
- **Medium Priority (Important)**: 87 tests (42%)
- **Low Priority (Nice-to-have)**: 20 tests (10%)

---

## Functional Requirements Test Coverage

### F-001: Document Assistant Agent - Backend WebSocket Service

**Test File**: `docs/tests/functional/F-001-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 4 | 4 | 0 | 0 | WebSocket communication, AI responses |
| Unit | 2 | 1 | 1 | 0 | Connection cleanup, error handling |
| Performance | 1 | 0 | 1 | 0 | Response time benchmarks |
| Edge Cases | 3 | 0 | 2 | 1 | Empty messages, large documents |
| Error Handling | 3 | 1 | 2 | 0 | API errors, network failures |
| **Subtotal** | **13** | **6** | **6** | **1** | |

**Critical Tests**:
- TC-F-001-01: Basic WebSocket connection and response (< 3s)
- TC-F-001-02: Document summarization with context
- TC-F-001-04: Form field auto-fill via FormUpdateMessage
- TC-F-001-06: Missing API key error handling

---

### F-002: Document Context Management System

**Test File**: `docs/tests/functional/F-002-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Unit | 4 | 2 | 2 | 0 | Context loading, merging |
| Integration | 5 | 3 | 2 | 0 | Context-aware validation |
| Edge Cases | 3 | 0 | 2 | 1 | Missing files, format handling |
| Error Handling | 3 | 2 | 1 | 0 | File errors, JSON parsing |
| Performance | 2 | 0 | 1 | 1 | Load times, caching |
| I18N | 2 | 0 | 2 | 0 | German/English support |
| **Subtotal** | **19** | **7** | **10** | **2** | |

**Critical Tests**:
- TC-F-002-01: Load case-level context (integration_course.json)
- TC-F-002-03: Context-aware birth certificate validation
- TC-F-002-04: Goethe Institut certificate recognition

---

### F-003: Form Auto-Fill from Document Content

**Test File**: `docs/tests/functional/F-003-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 7 | 5 | 2 | 0 | Data extraction, field population |
| Unit | 3 | 1 | 2 | 0 | Field validation, type handling |
| Edge Cases | 5 | 0 | 3 | 1 | Empty docs, special characters |
| Error Handling | 3 | 1 | 2 | 0 | Parser failures, API errors |
| Performance | 2 | 1 | 1 | 0 | Extraction speed (< 5s) |
| Confidence | 2 | 0 | 2 | 0 | Confidence scoring |
| **Subtotal** | **22** | **8** | **12** | **1** | |

**Critical Tests**:
- TC-F-003-01: Extract simple name field
- TC-F-003-02: Extract and format date field (German → ISO)
- TC-F-003-04: Extract from German document
- TC-F-003-06: Select field option matching
- TC-F-003-PERF01: 2000-char document, 7 fields in 5 seconds

---

### F-004: AI-Powered Form Field Generator - Admin Interface

**Test File**: `docs/tests/functional/F-004-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 8 | 5 | 3 | 0 | Field generation from NL prompts |
| Unit | 2 | 0 | 1 | 1 | Validation, metadata |
| E2E | 1 | 1 | 0 | 0 | Full workflow |
| Edge Cases | 4 | 0 | 1 | 2 | Special chars, long labels |
| Error Handling | 3 | 2 | 1 | 0 | Service unavailable, invalid specs |
| Performance | 2 | 0 | 1 | 1 | Generation speed |
| Usability | 2 | 0 | 2 | 0 | Kolibri components, preview |
| **Subtotal** | **22** | **8** | **9** | **4** | |

**Critical Tests**:
- TC-F-004-01: Generate simple text field
- TC-F-004-03: Generate select field with options
- TC-F-004-07: Field persistence to localStorage
- TC-F-004-08: JSON-LD semantic metadata

---

### F-005: Case-Level Form Management

**Test File**: `docs/tests/functional/F-005-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 7 | 6 | 1 | 0 | Case form display, case switching |
| E2E | 1 | 1 | 0 | 0 | Admin edit workflow |
| Unit | 2 | 2 | 0 | 0 | Schema validation |
| Edge Cases | 2 | 0 | 1 | 1 | Missing form data, large forms |
| Error Handling | 2 | 0 | 2 | 0 | Concurrent updates, invalid case |
| Performance | 1 | 0 | 1 | 0 | Form load time |
| Data Integrity | 2 | 2 | 0 | 0 | ID uniqueness, schema compliance |
| **Subtotal** | **17** | **11** | **5** | **1** | |

**Critical Tests**:
- TC-F-005-01: Display case form with title and 7 fields
- TC-F-005-02: Form persists across folder navigation
- TC-F-005-04: Form data changes when switching cases
- TC-F-005-06: Form auto-fill from any folder

---

### F-006: Replace Mock Documents with Text Files

**Test File**: `docs/tests/functional/F-006-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 7 | 5 | 2 | 0 | File loading, display, AI integration |
| Performance | 2 | 1 | 1 | 0 | Load times for various sizes |
| Error Handling | 1 | 1 | 0 | 0 | Missing files (404) |
| Edge Cases | 4 | 0 | 1 | 3 | Empty files, special chars |
| Unit | 3 | 0 | 1 | 2 | Format handling, MIME types |
| **Subtotal** | **17** | **7** | **5** | **5** | |

**Critical Tests**:
- TC-F-006-01: Load and display birth certificate content
- TC-F-006-02: AI chat receives document content
- TC-F-006-03: Large document load (5000+ chars)
- TC-F-006-04: German umlauts and special characters

---

## Non-Functional Requirements Test Coverage

### NFR-001: Real-Time AI Response Performance

**Test File**: `docs/tests/non-functional/NFR-001-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Performance | 6 | 5 | 1 | 0 | Response times, streaming |
| Edge Cases | 3 | 0 | 2 | 1 | Large docs, cold start |
| Load Testing | 2 | 0 | 2 | 0 | Sequential requests, bursts |
| Network | 2 | 0 | 1 | 1 | Slow networks, high latency |
| Optimization | 2 | 0 | 1 | 1 | Connection pooling |
| Timeout | 2 | 1 | 1 | 0 | Timeout configuration |
| Monitoring | 1 | 0 | 1 | 0 | Metrics logging |
| **Subtotal** | **18** | **6** | **9** | **3** | |

**Performance Benchmarks**:
- First token (simple query): ≤ 2 seconds
- First token (with 500-char doc): ≤ 2 seconds
- Full summary (1000 words): ≤ 10 seconds
- Form auto-fill (2000 chars, 7 fields): ≤ 5 seconds
- Typing indicator: < 100ms
- Streaming updates: every 500ms
- Sequential degradation: ≤ 10%

---

### NFR-002: Modular Backend Architecture

**Test File**: `docs/tests/non-functional/NFR-002-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Unit | 2 | 2 | 0 | 0 | Dependencies, initialization |
| Static Analysis | 2 | 2 | 0 | 0 | Pylint, Mypy |
| Documentation | 3 | 1 | 2 | 0 | Docstrings, README, API docs |
| Architecture | 3 | 1 | 2 | 0 | Layer separation, SRP, DI |
| Code Organization | 2 | 1 | 1 | 0 | Directory structure, naming |
| Testing Infrastructure | 2 | 0 | 2 | 0 | Pytest, fixtures |
| Performance | 1 | 0 | 0 | 1 | Import times |
| **Subtotal** | **17** | **8** | **8** | **1** | |

**Quality Targets**:
- Pylint score: ≥ 8.0/10
- Mypy type errors: 0
- Docstring coverage: 100% public functions
- Dependency pinning: All packages
- Zero circular dependencies

---

### NFR-003: Local Storage Without Database

**Test File**: `docs/tests/non-functional/NFR-003-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Integration | 4 | 3 | 1 | 0 | Persistence, loading |
| Unit | 2 | 2 | 0 | 0 | Error handling |
| Edge Cases | 4 | 0 | 2 | 2 | Quotas, malformed data |
| Data Integrity | 2 | 0 | 2 | 0 | Key naming, migration |
| Backend Storage | 2 | 1 | 1 | 0 | Context files, permissions |
| **Subtotal** | **14** | **6** | **6** | **2** | |

**Storage Strategy**:
- Frontend: localStorage (5MB limit)
- Backend: Filesystem JSON files
- Keys: bamf_form_fields, bamf_case_form_data, bamf_admin_config
- No database dependencies
- Stateless chat sessions

---

## Data Requirements Test Coverage

### D-001: Hierarchical Context Data Schema

**Test File**: `docs/tests/data/D-001-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Unit | 7 | 6 | 1 | 0 | Schema validation, structure |
| Schema Compliance | 3 | 2 | 1 | 0 | Required fields, arrays |
| Data Quality | 2 | 0 | 2 | 0 | German language, completeness |
| Consistency | 2 | 0 | 2 | 0 | Cross-file references |
| Performance | 1 | 0 | 1 | 0 | File size limits |
| **Subtotal** | **15** | **8** | **7** | **0** | |

**Context Files Required**:
- Case context: integration_course.json (1 file)
  - 5+ regulations
  - 10+ required documents
  - 8+ validation rules
- Folder contexts: 6 files (personal_data, certificates, integration_docs, applications, emails, evidence)
- Total: 7 JSON files
- Schema version: 1.0
- Max size: < 100KB per file

---

### D-002: Case-Type Form Schemas

**Test File**: `docs/tests/data/D-002-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Unit | 6 | 5 | 1 | 0 | Form structure, options |
| Integration | 2 | 2 | 0 | 0 | Case data loading |
| E2E | 1 | 1 | 0 | 0 | Rendering in FormViewer |
| Field Validation | 3 | 0 | 3 | 0 | Date, select, textarea |
| Data Integrity | 3 | 1 | 2 | 0 | ID uniqueness, labels |
| **Subtotal** | **15** | **9** | **6** | **0** | |

**Form Schema Summary**:
- Integration Course Application: 7 fields (5 required, 2 optional)
- Same form template used for all cases of this type
- Form data stored per-case in sampleCaseFormData
- 1 select field (Course Preference with 3 options)
- 2 textarea fields (Current Address, Reason for Application)

---

### D-003: Sample Document Text Content

**Test File**: `docs/tests/data/D-003-tests.md`

| Test Type | Count | High | Medium | Low | Key Focus Areas |
|-----------|-------|------|--------|-----|-----------------|
| Unit | 6 | 4 | 2 | 0 | Content validation, encoding |
| Integration | 4 | 3 | 1 | 0 | AI extraction, form auto-fill |
| Manual/Quality | 3 | 1 | 2 | 0 | Realism, consistency |
| AI Extraction | 3 | 2 | 1 | 0 | Name, date, contextual extraction |
| **Subtotal** | **16** | **10** | **6** | **0** | |

**Sample Documents Required**:
1. Birth_Certificate.txt (500-800 chars) - German
2. Passport_Scan.txt (400-600 chars) - English
3. Language_Certificate_A1.txt (600-1000 chars) - German/English
4. Integration_Application.txt (1000-1500 chars) - German/English
5. School_Transcripts.txt (1200-2000 chars) - English/German
6. Confirmation_Email.txt (300-500 chars) - German/English

**Character**: Ahmad Ali, born 15.05.1990, Kabul, Afghanistan

---

## Test Type Distribution

### By Test Type

| Test Type | Count | Percentage | Primary Focus |
|-----------|-------|------------|---------------|
| Integration | 54 | 26% | Cross-component interaction |
| Unit | 50 | 24% | Individual component behavior |
| Edge Cases | 29 | 14% | Boundary conditions |
| Error Handling | 18 | 9% | Failure scenarios |
| Performance | 16 | 8% | Speed and efficiency |
| Manual/Quality | 12 | 6% | Human verification |
| E2E | 8 | 4% | Complete workflows |
| Static Analysis | 7 | 3% | Code quality |
| Other | 14 | 7% | Architecture, docs, etc. |
| **Total** | **208** | **100%** | |

### By Testing Phase

| Phase | Test Count | Requirements | When to Execute |
|-------|------------|--------------|-----------------|
| **Development** | 50 | All | During feature implementation |
| **Integration Testing** | 54 | All | After component completion |
| **System Testing** | 38 | All | Before sprint completion |
| **Acceptance Testing** | 30 | All | Sprint review preparation |
| **Performance Testing** | 16 | NFR-001 | After core features stable |
| **Continuous** | 20 | NFR-002, NFR-003 | Throughout development |

---

## Risk-Based Test Prioritization

### Critical Path Tests (Must Pass Before Release)

1. **WebSocket Communication** (F-001)
   - Connection establishment
   - Basic AI response
   - Form auto-fill message handling

2. **Context Loading** (F-002)
   - Case and folder context files load correctly
   - Context used appropriately by AI

3. **Form Auto-Fill** (F-003)
   - Data extraction from documents
   - Field population
   - Date format conversion

4. **Document Loading** (F-006)
   - Text files load and display
   - UTF-8 encoding preserved
   - Content passed to AI

5. **Performance Benchmarks** (NFR-001)
   - First token < 2s
   - Form fill < 5s
   - Summary < 10s

### High-Risk Areas Requiring Extra Testing

1. **Gemini API Integration** - External dependency, potential failures
2. **WebSocket Stability** - Connection management, error handling
3. **Date Format Handling** - German ↔ ISO conversion critical
4. **Character Encoding** - UTF-8 for German characters
5. **localStorage Limits** - Quota management and fallbacks

---

## Test Automation Strategy

### Automated Tests (Target: 65% of total)

| Tool | Test Types | Count | Priority |
|------|------------|-------|----------|
| **Pytest** (Backend) | Unit, Integration, API | ~50 | High |
| **Jest** (Frontend) | Unit, Component | ~40 | High |
| **Playwright** (E2E) | E2E, Integration | ~25 | High |
| **Static Analysis** | Pylint, Mypy, ESLint | ~10 | Medium |
| **Total Automated** | | **~125** | |

### Manual Tests (Target: 35% of total)

| Category | Count | When | Who |
|----------|-------|------|-----|
| Usability Testing | ~30 | Sprint review prep | Product Owner, Users |
| Exploratory Testing | ~20 | Throughout sprint | QA, Developers |
| Visual/UI Testing | ~15 | After UI changes | QA, UX |
| Documentation Review | ~10 | End of sprint | Tech Lead |
| Performance Validation | ~8 | Post-optimization | Tech Lead |
| **Total Manual** | **~83** | | |

---

## Test Execution Timeline (Sprint 1)

### Week 1: Foundation
- [ ] Set up test infrastructure (pytest, jest, playwright)
- [ ] Create test data (context files, sample documents)
- [ ] Write and run unit tests for services and utilities
- [ ] Target: 40 tests passing

### Week 2: Integration
- [ ] WebSocket integration tests (F-001)
- [ ] Context management tests (F-002)
- [ ] Document loading tests (F-006)
- [ ] Target: 80 tests passing

### Week 3: Features
- [ ] Form auto-fill tests (F-003)
- [ ] Field generator tests (F-004)
- [ ] Case-level forms tests (F-005)
- [ ] Target: 130 tests passing

### Week 4: Quality & Performance
- [ ] Performance benchmarking (NFR-001)
- [ ] Architecture validation (NFR-002)
- [ ] Storage tests (NFR-003)
- [ ] E2E tests
- [ ] Manual testing and bug fixes
- [ ] Target: 180+ tests passing (85%+)

### Week 5: Finalization
- [ ] Remaining edge cases and error scenarios
- [ ] Documentation review
- [ ] Acceptance testing
- [ ] Sprint review preparation
- [ ] Target: 200+ tests passing (95%+)

---

## Test Environment Requirements

### Development Environment
- Node.js 18+, Python 3.11+
- npm, pytest, playwright
- Google Gemini API key
- Modern browser (Chrome/Edge)

### Test Data
- 7 context JSON files
- 6 sample document text files
- Mock case data with 3 cases
- Case-level form schema (7 fields)

### External Dependencies
- Google Gemini API (with test API key)
- LocalStorage available
- WebSocket support in browser

---

## Success Criteria

### Minimum Acceptance Criteria (POC Release)
- [ ] 85% of high-priority tests passing (80 of 94)
- [ ] Zero critical bugs blocking core workflows
- [ ] All performance benchmarks met (NFR-001)
- [ ] Code quality targets met (Pylint ≥ 8.0, Mypy clean)
- [ ] Documentation complete (README, API docs)

### Ideal Acceptance Criteria (Quality Release)
- [ ] 95% of all tests passing (191 of 201)
- [ ] 100% of high-priority tests passing
- [ ] All edge cases handled gracefully
- [ ] Performance optimized
- [ ] User acceptance testing completed successfully

---

## Known Limitations & Future Test Enhancements

### POC Phase Limitations
- No concurrent user testing (single user assumption)
- No database testing (localStorage only)
- Limited internationalization testing (German/English only)
- No production-scale load testing
- No security/authentication testing

### Future Test Enhancements (Post-POC)
- Multi-user concurrent access tests
- Database persistence tests
- Full internationalization testing
- Security and authentication tests
- Accessibility (WCAG) compliance tests
- Cross-browser compatibility testing
- Mobile responsive testing
- Load testing with realistic user volumes
- Chaos engineering for resilience

---

## Test Metrics & Reporting

### Key Metrics to Track
- Test pass rate (target: 95%+)
- Code coverage (target: 80%+ for services, 90%+ for tools)
- Defect density (bugs per requirement)
- Test execution time
- Performance benchmark results
- Test automation percentage

### Reports to Generate
- Daily test execution summary
- Weekly progress report (tests passing trend)
- Sprint end test coverage report
- Performance benchmark results
- Known issues and risk register
- Test execution dashboard (if CI/CD implemented)

---

## Conclusion

The BAMF AI Case Management System Sprint 1 test suite provides comprehensive coverage across all 12 requirements with 201+ test cases, **enhanced with case-instance scoping architecture**. The distribution of 49% high-priority, 42% medium-priority, and 10% low-priority tests ensures focus on critical functionality including case isolation security.

### Case-Instance Architecture Impact

The case-instance scoping introduces critical new testing requirements:

**Security & Isolation (High Priority):**
- Case boundary enforcement - cannot access other case's documents/context
- WebSocket case-specific endpoints prevent cross-case contamination
- Template-based case creation maintains isolation

**Data Integrity:**
- Each case maintains independent context at `cases/{caseId}/`
- Documents isolated at `documents/{caseId}/{folderId}/`
- Form data stored per-case

**User Experience:**
- Case switching properly reloads all context and documents
- Document tree updates show only active case's files
- AI responses reflect active case's context

With a target of 85% test automation and systematic manual testing, the suite provides confidence in the POC's quality and readiness for stakeholder review. The risk-based prioritization ensures critical paths including **case isolation security** are thoroughly validated, while the structured execution timeline aligns testing with development progress.

**Test Coverage**: 12 requirements → 201+ test cases → Comprehensive quality assurance with case-instance isolation
**Risk Mitigation**: High-priority tests focus on critical workflows, external dependencies, and case isolation security
**Automation**: 125+ automated tests enable continuous validation and regression prevention
**Quality Gates**: Clear acceptance criteria ensure POC meets standards including case isolation before release
**Case Architecture**: Case-instance scoping ensures complete data isolation and security between cases

---

*Last Updated*: 2025-12-17
*Version*: 1.1 (Sprint 1 POC - Case-Instance Scoped)
*Owner*: Development & QA Team
