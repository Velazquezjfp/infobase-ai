#!/bin/bash
# Test script for F-006: Document Loading Implementation
# This script verifies all required text files exist and are properly encoded

echo "========================================="
echo "F-006: Document Loading Test Script"
echo "========================================="
echo ""

# Base directory
BASE_DIR="/home/javiervel/clients/BAMF/Diga/app/bamf-acte-companion"
DOCS_DIR="$BASE_DIR/public/documents/ACTE-2024-001"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test file
test_file() {
    local filepath="$1"
    local filename=$(basename "$filepath")

    echo -n "Testing $filename... "

    # Check if file exists
    if [ ! -f "$filepath" ]; then
        echo "❌ FAILED - File not found"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check encoding
    encoding=$(file -i "$filepath" | grep -o 'charset=[^ ]*' | cut -d= -f2)
    if [ "$encoding" != "utf-8" ]; then
        echo "❌ FAILED - Not UTF-8 (detected: $encoding)"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check file is not empty
    if [ ! -s "$filepath" ]; then
        echo "❌ FAILED - File is empty"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check for German characters (if filename suggests German content)
    if echo "$filename" | grep -q "Birth_Certificate\|Language_Certificate"; then
        if ! grep -q 'ä\|ö\|ü\|ß\|Ä\|Ö\|Ü' "$filepath"; then
            echo "⚠️  WARNING - No German umlauts found (expected in German document)"
        fi
    fi

    echo "✅ PASSED"
    ((TESTS_PASSED++))
    return 0
}

echo "1. Testing Personal Data Documents"
echo "-----------------------------------"
test_file "$DOCS_DIR/personal-data/Birth_Certificate.txt"
test_file "$DOCS_DIR/personal-data/Passport_Scan.txt"
echo ""

echo "2. Testing Certificates"
echo "-----------------------"
test_file "$DOCS_DIR/certificates/Language_Certificate_A1.txt"
echo ""

echo "3. Testing Applications"
echo "-----------------------"
test_file "$DOCS_DIR/applications/Integration_Application.txt"
echo ""

echo "4. Testing Emails"
echo "-----------------"
test_file "$DOCS_DIR/emails/Confirmation_Email.txt"
echo ""

echo "5. Testing Evidence"
echo "-------------------"
test_file "$DOCS_DIR/evidence/School_Transcripts.txt"
echo ""

# Test case isolation - verify ACTE-2024-002 and ACTE-2024-003 directories exist
echo "6. Testing Case Isolation Structure"
echo "------------------------------------"
for case_id in ACTE-2024-002 ACTE-2024-003; do
    case_dir="$BASE_DIR/public/documents/$case_id"
    if [ -d "$case_dir" ]; then
        echo "✅ $case_id directory exists"
        ((TESTS_PASSED++))
    else
        echo "⚠️  $case_id directory not found (expected for multi-case support)"
    fi
done
echo ""

# Test frontend files
echo "7. Testing Frontend Implementation"
echo "-----------------------------------"

# Check documentLoader exists
if [ -f "$BASE_DIR/src/lib/documentLoader.ts" ]; then
    echo "✅ documentLoader.ts exists"
    ((TESTS_PASSED++))
else
    echo "❌ documentLoader.ts not found"
    ((TESTS_FAILED++))
fi

# Check types updated
if grep -q "'txt'" "$BASE_DIR/src/types/case.ts"; then
    echo "✅ Document type includes 'txt'"
    ((TESTS_PASSED++))
else
    echo "❌ Document type missing 'txt'"
    ((TESTS_FAILED++))
fi

# Check CaseTreeExplorer updated
if grep -q "loadDocumentContent" "$BASE_DIR/src/components/workspace/CaseTreeExplorer.tsx"; then
    echo "✅ CaseTreeExplorer uses loadDocumentContent"
    ((TESTS_PASSED++))
else
    echo "❌ CaseTreeExplorer not updated"
    ((TESTS_FAILED++))
fi

# Check DocumentViewer updated
if grep -q "selectedDocument.content" "$BASE_DIR/src/components/workspace/DocumentViewer.tsx"; then
    echo "✅ DocumentViewer displays text content"
    ((TESTS_PASSED++))
else
    echo "❌ DocumentViewer not updated"
    ((TESTS_FAILED++))
fi

echo ""
echo "========================================="
echo "Test Results"
echo "========================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
