#!/bin/bash
# Test Execution Script for S5-010: Optional Persistent Chat History

echo "================================================================================"
echo "S5-010: Optional Persistent Chat History - Test Execution"
echo "================================================================================"

# Initialize counters
total=0
passed=0
failed=0

# Test directory
TEST_DIR="docs/tests/S5-010"

# Array to store results
declare -a results

# Run each test
for test_file in "$TEST_DIR"/TC-S5-010-*.py; do
    test_name=$(basename "$test_file" .py)
    echo ""
    echo "Running $test_name..."

    # Run test and capture output
    output=$(python "$test_file" 2>&1)
    exit_code=$?

    total=$((total + 1))

    if [ $exit_code -eq 0 ]; then
        passed=$((passed + 1))
        echo "✓ $test_name: PASSED"
        results+=("$test_name:passed")
    else
        failed=$((failed + 1))
        echo "✗ $test_name: FAILED"
        echo "$output"
        results+=("$test_name:failed:$output")
    fi
done

# Print summary
echo ""
echo "================================================================================"
echo "Test Execution Summary"
echo "================================================================================"
echo "Total:   $total"
echo "Passed:  $passed"
echo "Failed:  $failed"
echo "================================================================================"

# Export results for JSON generation
export TEST_RESULTS="${results[@]}"
export TOTAL=$total
export PASSED=$passed
export FAILED=$failed

# Exit with appropriate code
if [ $failed -eq 0 ]; then
    exit 0
else
    exit 1
fi
