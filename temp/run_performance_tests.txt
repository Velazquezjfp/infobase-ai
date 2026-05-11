#!/bin/bash
# NFR-001 Performance Test Runner
#
# This script helps run the NFR-001 performance tests and collect results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "======================================================================"
echo "NFR-001: Real-Time AI Response Performance Test Runner"
echo "======================================================================"
echo

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend is not running!"
    echo "   Please start the backend first:"
    echo "   cd backend && python3 main.py"
    exit 1
fi

# Check if websockets library is installed
echo
echo "🔍 Checking Python dependencies..."
if python3 -c "import websockets" 2>/dev/null; then
    echo "✅ websockets library is installed"
else
    echo "❌ websockets library not found"
    echo "   Installing websockets..."
    pip3 install websockets
fi

# Run the performance tests
echo
echo "======================================================================"
echo "Running Performance Tests..."
echo "======================================================================"
echo

python3 "$SCRIPT_DIR/test_nfr001_performance.py"

TEST_EXIT_CODE=$?

# Check backend logs for metrics
echo
echo "======================================================================"
echo "Backend Logs (Last 50 lines with metrics):"
echo "======================================================================"
echo

# Try to find backend log output (adjust path if needed)
if [ -f "$PROJECT_ROOT/backend/logs/app.log" ]; then
    echo "📊 Metrics from backend logs:"
    grep -E "(Response complete|First token|Streaming complete)" "$PROJECT_ROOT/backend/logs/app.log" | tail -n 20
elif docker ps | grep -q backend 2>/dev/null; then
    echo "📊 Metrics from Docker container:"
    docker logs $(docker ps -qf "name=backend") 2>&1 | grep -E "(Response complete|First token|Streaming complete)" | tail -n 20
else
    echo "⚠️  Could not find backend logs"
    echo "   Check your terminal where backend is running for metrics output"
fi

echo
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
echo

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo
    echo "Next steps:"
    echo "  1. Review the performance metrics above"
    echo "  2. Check backend logs for detailed timing information"
    echo "  3. Update test status in docs/tests/non-functional/NFR-001-tests.md"
    exit 0
else
    echo "❌ Some tests failed"
    echo
    echo "Next steps:"
    echo "  1. Review the failed tests above"
    echo "  2. Check backend logs for errors"
    echo "  3. Adjust implementation if needed"
    echo "  4. Re-run tests"
    exit 1
fi
