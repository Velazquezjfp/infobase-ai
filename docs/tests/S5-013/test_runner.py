"""
Test Runner for S5-013 Enhanced Acte Context Research
Executes all test cases and generates test-results.json
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager

# Test case definitions
SCHEMA_V2_CONTEXTS = [
    ("ACTE-2024-001", "Integration Course Case"),
    ("templates/integration_course", "Integration Course Template"),
    ("templates/asylum_application", "Asylum Application Template"),
    ("templates/family_reunification", "Family Reunification Template"),
]


def load_case_context(context_manager, case_id):
    """Load case context, handling both cases and templates"""
    if case_id.startswith("templates/"):
        # Template path
        template_name = case_id.split("/")[1]
        case_path = context_manager.templates_path / template_name / "case.json"
    else:
        # Case path
        case_path = context_manager.cases_path / case_id / "case.json"

    with open(case_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_01_required_documents():
    """TC-S5-013-01: Verify requiredDocuments array has 10+ entries"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)

            assert 'requiredDocuments' in context
            required_docs = context['requiredDocuments']
            assert isinstance(required_docs, list)
            doc_count = len(required_docs)
            assert doc_count >= 10, f"Expected ≥10 documents, got {doc_count}"

            test_results.append({
                'testId': f'TC-S5-013-01-{case_id}',
                'testName': f'Required Documents Count - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: {doc_count} documents")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-01-{case_id}',
                'testName': f'Required Documents Count - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_02_criticality_fields():
    """TC-S5-013-02: Verify criticality fields"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)
            required_docs = context.get('requiredDocuments', [])

            critical_count = 0
            optional_count = 0

            for idx, doc in enumerate(required_docs):
                doc_name = doc.get('name', f'Document {idx}')
                assert 'criticality' in doc, f"Document '{doc_name}' missing 'criticality' field"
                criticality = doc['criticality']
                assert criticality in ['critical', 'optional'], \
                    f"Document '{doc_name}' has invalid criticality: '{criticality}'"

                if criticality == 'critical':
                    critical_count += 1
                else:
                    optional_count += 1

            test_results.append({
                'testId': f'TC-S5-013-02-{case_id}',
                'testName': f'Document Criticality - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: {critical_count} critical, {optional_count} optional")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-02-{case_id}',
                'testName': f'Document Criticality - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_03_regulations_array():
    """TC-S5-013-03: Verify regulations array"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)

            assert 'regulations' in context
            regulations = context['regulations']
            assert isinstance(regulations, list)
            reg_count = len(regulations)
            assert reg_count >= 5, f"Expected ≥5 regulations, got {reg_count}"

            # Verify each regulation has required fields
            for idx, reg_data in enumerate(regulations):
                required_fields = ['id', 'title', 'url', 'summary']
                for field in required_fields:
                    assert field in reg_data and reg_data[field], \
                        f"Regulation {idx} missing or empty '{field}' field"

            test_results.append({
                'testId': f'TC-S5-013-03-{case_id}',
                'testName': f'Regulations Array - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: {reg_count} regulations")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-03-{case_id}',
                'testName': f'Regulations Array - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_04_regulation_fields():
    """TC-S5-013-04: Verify regulation fields"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)
            regulations = context.get('regulations', [])

            for idx, reg_data in enumerate(regulations):
                # Verify required fields present and not empty
                assert reg_data.get('id', '').strip(), f"Regulation {idx} has empty id"
                assert reg_data.get('title', '').strip(), f"Regulation {idx} has empty title"
                assert reg_data.get('url', '').strip(), f"Regulation {idx} has empty url"
                assert reg_data.get('summary', '').strip(), f"Regulation {idx} has empty summary"

                # Verify URL format
                url = reg_data['url']
                assert url.startswith(('http://', 'https://')), \
                    f"Regulation {idx} url must start with http:// or https://"

                # Verify minimum content length
                assert len(reg_data['summary']) >= 20, \
                    f"Regulation {idx} summary too short (< 20 chars)"
                assert len(reg_data['title']) >= 5, \
                    f"Regulation {idx} title too short (< 5 chars)"

            test_results.append({
                'testId': f'TC-S5-013-04-{case_id}',
                'testName': f'Regulation Fields - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: All {len(regulations)} regulations valid")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-04-{case_id}',
                'testName': f'Regulation Fields - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_05_common_issues():
    """TC-S5-013-05: Verify commonIssues array"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)

            assert 'commonIssues' in context
            common_issues = context['commonIssues']
            assert isinstance(common_issues, list)
            issue_count = len(common_issues)
            assert issue_count >= 10, f"Expected ≥10 common issues, got {issue_count}"

            by_severity = {'error': 0, 'warning': 0, 'info': 0}

            for idx, issue in enumerate(common_issues):
                required_fields = ['issue', 'severity', 'suggestion']
                for field in required_fields:
                    assert field in issue and str(issue[field]).strip(), \
                        f"Issue {idx} missing or empty '{field}' field"

                severity = issue['severity']
                assert severity in ['error', 'warning', 'info'], \
                    f"Issue {idx} has invalid severity: '{severity}'"

                by_severity[severity] += 1

            test_results.append({
                'testId': f'TC-S5-013-05-{case_id}',
                'testName': f'Common Issues - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: {issue_count} issues (E:{by_severity['error']}, W:{by_severity['warning']}, I:{by_severity['info']})")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-05-{case_id}',
                'testName': f'Common Issues - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_10_schema_version():
    """TC-S5-013-10: Verify schema version"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)

            assert 'schemaVersion' in context
            schema_version = context['schemaVersion']
            assert schema_version == '2.0', \
                f"Expected schemaVersion '2.0', got '{schema_version}'"

            test_results.append({
                'testId': f'TC-S5-013-10-{case_id}',
                'testName': f'Schema Version - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"✓ {case_name}: Schema version {schema_version}")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-10-{case_id}',
                'testName': f'Schema Version - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def test_12_schema_validation():
    """TC-S5-013-12: Validate against schema"""
    context_manager = ContextManager()
    test_results = []

    for case_id, case_name in SCHEMA_V2_CONTEXTS:
        try:
            context = load_case_context(context_manager, case_id)

            # Manually validate required top-level fields
            required_fields = [
                'schemaVersion', 'caseId', 'caseType', 'name', 'description',
                'requiredDocuments', 'regulations', 'validationRules', 'commonIssues'
            ]

            errors = []
            for field in required_fields:
                if field not in context:
                    errors.append(f"Missing required field: {field}")

            # Check minimum thresholds
            if len(context.get('requiredDocuments', [])) < 15:
                errors.append(f"Insufficient required documents: {len(context.get('requiredDocuments', []))}")

            if len(context.get('regulations', [])) < 10:
                errors.append(f"Insufficient regulations: {len(context.get('regulations', []))}")

            if len(context.get('commonIssues', [])) < 20:
                errors.append(f"Insufficient common issues: {len(context.get('commonIssues', []))}")

            assert len(errors) == 0, ', '.join(errors)

            test_results.append({
                'testId': f'TC-S5-013-12-{case_id}',
                'testName': f'Schema Validation - {case_name}',
                'testType': 'python',
                'status': 'passed',
                'executionTime': 0.2,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            docs = len(context.get('requiredDocuments', []))
            regs = len(context.get('regulations', []))
            issues = len(context.get('commonIssues', []))
            print(f"✓ {case_name}: Valid - {docs} docs, {regs} regs, {issues} issues")

        except AssertionError as e:
            test_results.append({
                'testId': f'TC-S5-013-12-{case_id}',
                'testName': f'Schema Validation - {case_name}',
                'testType': 'python',
                'status': 'failed',
                'executionTime': 0.2,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'errorMessage': str(e)
            })
            print(f"✗ {case_name}: FAILED - {e}")

    return test_results


def add_pending_tests():
    """Add pending tests that require S5-005 (Case Validation Agent)"""
    pending_tests = [
        ('TC-S5-013-06', 'Validation Service Integration'),
        ('TC-S5-013-07', 'AI Document Matching'),
        ('TC-S5-013-08', 'Missing Document Suggestions'),
        ('TC-S5-013-09', 'Regulation Citation'),
        ('TC-S5-013-13', 'AI Regulation Citing'),
        ('TC-S5-013-14', 'AI Alternative Handling'),
    ]

    results = []
    for test_id, test_name in pending_tests:
        results.append({
            'testId': test_id,
            'testName': test_name,
            'testType': 'python',
            'status': 'skipped',
            'executionTime': 0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'errorMessage': 'PENDING: Requires S5-005 (Case Validation Agent) implementation'
        })
        print(f"⊘ {test_id}: PENDING (requires S5-005)")

    return results


def main():
    """Run all tests and generate results"""
    print("=" * 70)
    print("S5-013 Enhanced Acte Context Research - Test Execution")
    print("=" * 70)

    all_results = []

    # Execute implementation-ready tests
    print("\n--- TC-S5-013-01: Required Documents Count ---")
    all_results.extend(test_01_required_documents())

    print("\n--- TC-S5-013-02: Document Criticality ---")
    all_results.extend(test_02_criticality_fields())

    print("\n--- TC-S5-013-03: Regulations Array ---")
    all_results.extend(test_03_regulations_array())

    print("\n--- TC-S5-013-04: Regulation Fields ---")
    all_results.extend(test_04_regulation_fields())

    print("\n--- TC-S5-013-05: Common Issues ---")
    all_results.extend(test_05_common_issues())

    print("\n--- TC-S5-013-10: Schema Version ---")
    all_results.extend(test_10_schema_version())

    print("\n--- TC-S5-013-12: Schema Validation ---")
    all_results.extend(test_12_schema_validation())

    # Add pending tests
    print("\n--- Pending Tests (Require S5-005) ---")
    all_results.extend(add_pending_tests())

    # Calculate summary
    summary = {
        'total': len(all_results),
        'passed': sum(1 for r in all_results if r['status'] == 'passed'),
        'failed': sum(1 for r in all_results if r['status'] == 'failed'),
        'skipped': sum(1 for r in all_results if r['status'] == 'skipped'),
        'manual': 0
    }

    # Generate test results JSON
    test_results = {
        'requirementId': 'S5-013',
        'executionTimestamp': datetime.now(timezone.utc).isoformat(),
        'summary': summary,
        'testCases': all_results
    }

    # Write test results to file
    output_path = Path(__file__).parent / 'test-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("Test Execution Summary")
    print("=" * 70)
    print(f"Total Tests:  {summary['total']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Skipped:      {summary['skipped']}")
    print(f"\nResults written to: {output_path}")

    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
