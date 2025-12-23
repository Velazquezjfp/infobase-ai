"""
TC-S2-004-02: Conflict Resolution Test (Folder wins over Case)

Tests that when a field value conflicts between folder and case contexts,
the folder context value takes precedence according to the cascading rules.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.context_manager import (
    ContextEntry,
    ContextSource,
    resolve_conflict
)


def test_conflict_resolution():
    """Test that folder context wins conflicts with case context."""
    print("=" * 70)
    print("TC-S2-004-02: Conflict Resolution Test (Folder vs Case)")
    print("=" * 70)

    # Setup: Create conflicting entries for the same field from folder and case
    case_entry = ContextEntry(
        key="required_documents_count",
        value=5,  # Case says 5 documents required
        source=ContextSource.CASE,
        source_name="case.json"
    )

    folder_entry = ContextEntry(
        key="required_documents_count",
        value=3,  # Folder says only 3 documents required
        source=ContextSource.FOLDER,
        source_name="personal-data.json"
    )

    # Test: Resolve the conflict
    print("\n1. Testing folder vs case conflict resolution...")
    print(f"   Case value: {case_entry.value}")
    print(f"   Folder value: {folder_entry.value}")

    winner, conflicts = resolve_conflict([case_entry, folder_entry])

    # Assert: Folder should win
    assert winner.source == ContextSource.FOLDER, \
        f"Expected FOLDER to win, but got {winner.source}"
    assert winner.value == 3, \
        f"Expected folder value (3), got {winner.value}"
    assert len(conflicts) == 1, \
        f"Expected 1 conflict, got {len(conflicts)}"

    print(f"\n✓ Folder context wins: {winner.value}")
    print(f"✓ Conflict detected and resolved:")
    print(f"  - Resolved value: {conflicts[0]['resolvedValue']} "
          f"(from {conflicts[0]['resolvedSource']})")
    print(f"  - Rejected value: {conflicts[0]['conflictingValue']} "
          f"(from {conflicts[0]['conflictingSource']})")
    print(f"  - Reason: {conflicts[0]['reason']}")

    # Test: Verify conflict metadata
    assert conflicts[0]['key'] == "required_documents_count", \
        f"Wrong key in conflict: {conflicts[0]['key']}"
    assert conflicts[0]['resolvedSource'] == 'folder', \
        f"Wrong resolved source: {conflicts[0]['resolvedSource']}"
    assert conflicts[0]['conflictingSource'] == 'case', \
        f"Wrong conflicting source: {conflicts[0]['conflictingSource']}"

    print("\n✓ Conflict metadata correct")

    print("\n✓ TC-S2-004-02 PASSED: Folder wins over case in conflicts")
    return True


if __name__ == "__main__":
    try:
        result = test_conflict_resolution()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-02 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-02 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
