#!/usr/bin/env python3
"""
D-001 Test Execution Script
Hierarchical Context Data Schema (Case-Instance Scoped) Tests
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Define paths
BASE_DIR = Path(__file__).parent
CONTEXTS_DIR = BASE_DIR / "backend/data/contexts"
CASE_DIR = CONTEXTS_DIR / "cases/ACTE-2024-001"
CASE_FILE = CASE_DIR / "case.json"
FOLDERS_DIR = CASE_DIR / "folders"
TEST_RESULTS_DIR = BASE_DIR / "docs/tests/data/D-001"

# Test results storage
test_results = []

def log_test(test_id: str, test_name: str, status: str, execution_time: float,
             error_message: str = None, details: Dict = None):
    """Log a test result"""
    result = {
        "testId": test_id,
        "testName": test_name,
        "testType": "python",
        "status": status,
        "executionTime": execution_time,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if error_message:
        result["errorMessage"] = error_message
    if details:
        result["details"] = details
    test_results.append(result)
    return result

def load_json(file_path: Path) -> Dict:
    """Load and parse JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_tc_d001_01_case_context_schema():
    """TC-D-001-01: Case-Instance Context Schema Validation"""
    test_id = "TC-D-001-01"
    test_name = "Case-Instance Context Schema Validation"
    start = datetime.now()

    try:
        # Load case.json
        if not CASE_FILE.exists():
            raise FileNotFoundError(f"Case file not found: {CASE_FILE}")

        context = load_json(CASE_FILE)

        # Verify required keys
        required_keys = [
            "caseId", "caseType", "name", "description",
            "regulations", "requiredDocuments", "validationRules", "commonIssues"
        ]
        missing_keys = [key for key in required_keys if key not in context]

        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        # Verify schemaVersion
        if "schemaVersion" not in context:
            raise ValueError("Missing schemaVersion field")

        if context["schemaVersion"] != "1.0":
            raise ValueError(f"Invalid schemaVersion: {context['schemaVersion']}, expected 1.0")

        # Verify caseId matches directory
        if context["caseId"] != "ACTE-2024-001":
            raise ValueError(f"CaseId mismatch: {context['caseId']}, expected ACTE-2024-001")

        # Verify caseType
        if context["caseType"] != "integration_course":
            raise ValueError(f"Invalid caseType: {context['caseType']}")

        # Verify data types
        assert isinstance(context["caseId"], str), "caseId must be string"
        assert isinstance(context["caseType"], str), "caseType must be string"
        assert isinstance(context["name"], str), "name must be string"
        assert isinstance(context["description"], str), "description must be string"
        assert isinstance(context["regulations"], list), "regulations must be array"
        assert isinstance(context["requiredDocuments"], list), "requiredDocuments must be array"
        assert isinstance(context["validationRules"], list), "validationRules must be array"
        assert isinstance(context["commonIssues"], list), "commonIssues must be array"

        # Check file size
        file_size = CASE_FILE.stat().st_size
        if file_size >= 100 * 1024:  # 100KB
            raise ValueError(f"File too large: {file_size} bytes (limit: 102400)")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"caseId": context["caseId"], "caseType": context["caseType"],
                         "fileSize": file_size, "schemaVersion": context["schemaVersion"]})
        print(f"✓ {test_id}: {test_name} - PASSED")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_02_regulations_array():
    """TC-D-001-02: Regulations Array Structure"""
    test_id = "TC-D-001-02"
    test_name = "Regulations Array Structure"
    start = datetime.now()

    try:
        context = load_json(CASE_FILE)
        regulations = context["regulations"]

        # Verify minimum count
        if len(regulations) < 5:
            raise ValueError(f"Insufficient regulations: {len(regulations)}, expected 5+")

        # Verify structure of each regulation
        regulation_ids = []
        for idx, regulation in enumerate(regulations):
            if "id" not in regulation:
                raise ValueError(f"Regulation {idx} missing 'id' field")
            if "title" not in regulation:
                raise ValueError(f"Regulation {idx} missing 'title' field")
            if "summary" not in regulation:
                raise ValueError(f"Regulation {idx} missing 'summary' field")

            # Check for duplicates
            if regulation["id"] in regulation_ids:
                raise ValueError(f"Duplicate regulation ID: {regulation['id']}")
            regulation_ids.append(regulation["id"])

            # Verify summary is meaningful
            if len(regulation["summary"]) < 20:
                raise ValueError(f"Regulation {regulation['id']} summary too short")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"regulationCount": len(regulations),
                         "regulationIds": regulation_ids})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(regulations)} regulations)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_03_folder_context_schema():
    """TC-D-001-03: Case-Specific Folder Context Schema"""
    test_id = "TC-D-001-03"
    test_name = "Case-Specific Folder Context Schema"
    start = datetime.now()

    try:
        personal_data_file = FOLDERS_DIR / "personal-data.json"
        if not personal_data_file.exists():
            raise FileNotFoundError(f"File not found: {personal_data_file}")

        context = load_json(personal_data_file)

        # Verify required keys
        required_keys = ["folderId", "folderName", "purpose", "expectedDocuments", "validationCriteria"]
        missing_keys = [key for key in required_keys if key not in context]

        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        # Verify folderId
        if context["folderId"] != "personal-data":
            raise ValueError(f"Invalid folderId: {context['folderId']}")

        # Verify expectedDocuments
        expected_docs = context["expectedDocuments"]
        required_doc_types = ["birth_certificate", "passport", "national_id"]

        for doc_type in required_doc_types:
            if doc_type not in expected_docs:
                raise ValueError(f"Missing expected document type: {doc_type}")

        # Verify validationCriteria
        if len(context["validationCriteria"]) < 3:
            raise ValueError(f"Insufficient validation criteria: {len(context['validationCriteria'])}")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"folderId": context["folderId"],
                         "expectedDocsCount": len(expected_docs),
                         "criteriaCount": len(context["validationCriteria"])})
        print(f"✓ {test_id}: {test_name} - PASSED")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_04_certificates_validation():
    """TC-D-001-04: Certificates Folder Validation Criteria"""
    test_id = "TC-D-001-04"
    test_name = "Certificates Folder Validation Criteria"
    start = datetime.now()

    try:
        certificates_file = FOLDERS_DIR / "certificates.json"
        if not certificates_file.exists():
            raise FileNotFoundError(f"File not found: {certificates_file}")

        context = load_json(certificates_file)
        validation_criteria = context.get("validationCriteria", [])

        # Convert to string for searching
        criteria_str = json.dumps(validation_criteria).lower()

        # Check for CEFR level validation
        has_cefr = "cefr" in criteria_str or "a1" in criteria_str or "a2" in criteria_str

        # Check for recognized institution
        has_institution = "institution" in criteria_str or "goethe" in criteria_str

        if not has_cefr:
            raise ValueError("Missing CEFR level validation criteria")

        if not has_institution:
            raise ValueError("Missing recognized institution validation")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"hasCEFR": has_cefr, "hasInstitution": has_institution})
        print(f"✓ {test_id}: {test_name} - PASSED")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_05_json_syntax():
    """TC-D-001-05: Case-Instance JSON Syntax Validation"""
    test_id = "TC-D-001-05"
    test_name = "Case-Instance JSON Syntax Validation"
    start = datetime.now()

    try:
        # Find all case directories
        cases_dir = CONTEXTS_DIR / "cases"
        templates_dir = CONTEXTS_DIR / "templates"

        valid_files = []
        invalid_files = []
        case_dirs = []

        # Validate case directories
        if cases_dir.exists():
            for case_dir in cases_dir.iterdir():
                if case_dir.is_dir():
                    case_dirs.append(case_dir.name)
                    # Validate case.json
                    case_file = case_dir / "case.json"
                    if case_file.exists():
                        try:
                            with open(case_file, 'r', encoding='utf-8') as f:
                                json.load(f)
                            valid_files.append(str(case_file.relative_to(BASE_DIR)))
                        except json.JSONDecodeError as e:
                            invalid_files.append({
                                "file": str(case_file.relative_to(BASE_DIR)),
                                "error": str(e)
                            })

                    # Validate folder contexts
                    folders_dir = case_dir / "folders"
                    if folders_dir.exists():
                        for json_file in folders_dir.glob("*.json"):
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    json.load(f)
                                valid_files.append(str(json_file.relative_to(BASE_DIR)))
                            except json.JSONDecodeError as e:
                                invalid_files.append({
                                    "file": str(json_file.relative_to(BASE_DIR)),
                                    "error": str(e)
                                })

        # Validate template directories
        if templates_dir.exists():
            for template_dir in templates_dir.iterdir():
                if template_dir.is_dir():
                    for json_file in template_dir.rglob("*.json"):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                json.load(f)
                            valid_files.append(str(json_file.relative_to(BASE_DIR)))
                        except json.JSONDecodeError as e:
                            invalid_files.append({
                                "file": str(json_file.relative_to(BASE_DIR)),
                                "error": str(e)
                            })

        if invalid_files:
            raise ValueError(f"Invalid JSON files: {invalid_files}")

        if len(valid_files) == 0:
            raise ValueError("No JSON files found to validate")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"totalFiles": len(valid_files), "caseDirs": case_dirs,
                         "validFiles": valid_files})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(valid_files)} files, {len(case_dirs)} cases)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_06_context_size():
    """TC-D-001-06: Context Size Performance Check"""
    test_id = "TC-D-001-06"
    test_name = "Context Size Performance Check"
    start = datetime.now()

    try:
        file_size = CASE_FILE.stat().st_size

        if file_size >= 100 * 1024:  # 100KB
            raise ValueError(f"File too large: {file_size} bytes (limit: 102400)")

        # Measure parse time
        parse_start = datetime.now()
        context = load_json(CASE_FILE)
        parse_time = (datetime.now() - parse_start).total_seconds() * 1000  # ms

        if parse_time > 50:
            raise ValueError(f"Parse time too slow: {parse_time}ms (limit: 50ms)")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"fileSize": file_size, "parseTimeMs": parse_time})
        print(f"✓ {test_id}: {test_name} - PASSED ({file_size} bytes, {parse_time:.2f}ms)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_07_unique_folder_ids():
    """TC-D-001-07: Unique Folder IDs"""
    test_id = "TC-D-001-07"
    test_name = "Unique Folder IDs"
    start = datetime.now()

    try:
        folder_files = list(FOLDERS_DIR.glob("*.json"))

        if len(folder_files) != 6:
            raise ValueError(f"Expected 6 folder files, found {len(folder_files)}")

        folder_ids = []
        for folder_file in folder_files:
            context = load_json(folder_file)
            folder_id = context.get("folderId")

            if not folder_id:
                raise ValueError(f"Missing folderId in {folder_file.name}")

            if folder_id in folder_ids:
                raise ValueError(f"Duplicate folderId: {folder_id}")

            folder_ids.append(folder_id)

        # Verify expected IDs
        expected_ids = {
            "personal-data", "certificates", "integration-docs",
            "applications", "emails", "evidence"
        }

        if set(folder_ids) != expected_ids:
            raise ValueError(f"Folder IDs mismatch. Expected: {expected_ids}, Found: {set(folder_ids)}")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"folderIds": sorted(folder_ids)})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(folder_ids)} unique IDs)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_schema01_required_documents():
    """TC-D-001-SCHEMA01: Required Documents Structure"""
    test_id = "TC-D-001-SCHEMA01"
    test_name = "Required Documents Structure"
    start = datetime.now()

    try:
        context = load_json(CASE_FILE)
        required_docs = context["requiredDocuments"]

        if len(required_docs) < 10:
            raise ValueError(f"Insufficient required documents: {len(required_docs)}, expected 10+")

        for idx, doc in enumerate(required_docs):
            if "documentType" not in doc:
                raise ValueError(f"Document {idx} missing 'documentType'")
            if "mandatory" not in doc:
                raise ValueError(f"Document {idx} missing 'mandatory'")
            if "validationRules" not in doc:
                raise ValueError(f"Document {idx} missing 'validationRules'")

            assert isinstance(doc["documentType"], str), f"Document {idx} documentType must be string"
            assert isinstance(doc["mandatory"], bool), f"Document {idx} mandatory must be boolean"
            assert isinstance(doc["validationRules"], list), f"Document {idx} validationRules must be array"

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"requiredDocsCount": len(required_docs)})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(required_docs)} documents)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_schema02_validation_rules():
    """TC-D-001-SCHEMA02: Validation Rules Structure"""
    test_id = "TC-D-001-SCHEMA02"
    test_name = "Validation Rules Structure"
    start = datetime.now()

    try:
        context = load_json(CASE_FILE)
        validation_rules = context["validationRules"]

        if len(validation_rules) < 8:
            raise ValueError(f"Insufficient validation rules: {len(validation_rules)}, expected 8+")

        for idx, rule in enumerate(validation_rules):
            if "rule_id" not in rule:
                raise ValueError(f"Rule {idx} missing 'rule_id'")
            if "condition" not in rule:
                raise ValueError(f"Rule {idx} missing 'condition'")
            if "action" not in rule:
                raise ValueError(f"Rule {idx} missing 'action'")

            assert isinstance(rule["rule_id"], str), f"Rule {idx} rule_id must be string"
            assert isinstance(rule["condition"], str), f"Rule {idx} condition must be string"
            assert isinstance(rule["action"], str), f"Rule {idx} action must be string"

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"validationRulesCount": len(validation_rules)})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(validation_rules)} rules)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def test_tc_d001_schema03_common_issues():
    """TC-D-001-SCHEMA03: Common Issues Structure"""
    test_id = "TC-D-001-SCHEMA03"
    test_name = "Common Issues Structure"
    start = datetime.now()

    try:
        context = load_json(CASE_FILE)
        common_issues = context["commonIssues"]

        if len(common_issues) == 0:
            raise ValueError("No common issues defined")

        for idx, issue in enumerate(common_issues):
            if "issue" not in issue:
                raise ValueError(f"Issue {idx} missing 'issue' field")
            if "severity" not in issue:
                raise ValueError(f"Issue {idx} missing 'severity' field")
            if "suggestion" not in issue:
                raise ValueError(f"Issue {idx} missing 'suggestion' field")

            # Verify severity levels
            valid_severities = ["error", "warning", "info"]
            if issue["severity"] not in valid_severities:
                raise ValueError(f"Issue {idx} has invalid severity: {issue['severity']}")

        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "passed", execution_time,
                 details={"commonIssuesCount": len(common_issues)})
        print(f"✓ {test_id}: {test_name} - PASSED ({len(common_issues)} issues)")
        return True

    except Exception as e:
        execution_time = (datetime.now() - start).total_seconds()
        log_test(test_id, test_name, "failed", execution_time, str(e))
        print(f"✗ {test_id}: {test_name} - FAILED: {e}")
        return False

def save_test_results():
    """Save test results to JSON file"""
    # Ensure directory exists
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Calculate summary
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")

    results_json = {
        "requirementId": "D-001",
        "executionTimestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "manual": 0
        },
        "testCases": test_results
    }

    results_file = TEST_RESULTS_DIR / "test-results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Test results saved to: {results_file}")
    return results_json

def main():
    """Main test execution"""
    print("="*80)
    print("D-001: Hierarchical Context Data Schema Tests")
    print("Case-Instance Scoped Context Validation")
    print("="*80)
    print()

    # Execute all tests
    tests = [
        test_tc_d001_01_case_context_schema,
        test_tc_d001_02_regulations_array,
        test_tc_d001_03_folder_context_schema,
        test_tc_d001_04_certificates_validation,
        test_tc_d001_05_json_syntax,
        test_tc_d001_06_context_size,
        test_tc_d001_07_unique_folder_ids,
        test_tc_d001_schema01_required_documents,
        test_tc_d001_schema02_validation_rules,
        test_tc_d001_schema03_common_issues,
    ]

    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
        print()

    # Save results
    results_json = save_test_results()

    # Print summary
    print()
    print("="*80)
    print("Test Execution Summary")
    print("="*80)
    print(f"Total Tests:  {results_json['summary']['total']}")
    print(f"Passed:       {results_json['summary']['passed']}")
    print(f"Failed:       {results_json['summary']['failed']}")
    print(f"Success Rate: {results_json['summary']['passed']/results_json['summary']['total']*100:.1f}%")
    print("="*80)

    # Exit code
    if results_json['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
