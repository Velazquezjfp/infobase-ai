"""
TC-S2-004-01: Context Precedence Test (Document > Folder > Case)

Tests that when document, folder, and case contexts all provide information,
the document context takes highest precedence, followed by folder, then case.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.context_manager import (
    ContextManager,
    ContextEntry,
    ContextSource,
    resolve_conflict
)


def test_context_precedence():
    """Test that document context takes precedence over folder and case."""
    print("=" * 70)
    print("TC-S2-004-01: Context Precedence Test (Document > Folder > Case)")
    print("=" * 70)

    # Setup: Create conflicting context entries for the same field
    case_entry = ContextEntry(
        key="applicant_name",
        value="Ahmad Ali (Case)",
        source=ContextSource.CASE,
        source_name="case.json"
    )

    folder_entry = ContextEntry(
        key="applicant_name",
        value="Ahmad Ali (Folder)",
        source=ContextSource.FOLDER,
        source_name="personal-data.json"
    )

    document_entry = ContextEntry(
        key="applicant_name",
        value="Ahmad Ali (Document)",
        source=ContextSource.DOCUMENT,
        source_name="passport.txt"
    )

    # Test: Resolve conflict with all three sources
    print("\n1. Testing with all three context sources...")
    winner, conflicts = resolve_conflict([case_entry, folder_entry, document_entry])

    # Assert: Document should win
    assert winner.source == ContextSource.DOCUMENT, \
        f"Expected DOCUMENT to win, but got {winner.source}"
    assert winner.value == "Ahmad Ali (Document)", \
        f"Expected document value, got {winner.value}"
    assert len(conflicts) == 2, f"Expected 2 conflicts, got {len(conflicts)}"

    print(f"✓ Document context takes precedence: '{winner.value}'")
    print(f"✓ Conflicts resolved: {len(conflicts)}")
    for conflict in conflicts:
        print(f"  - Rejected {conflict['conflictingSource']}: "
              f"'{conflict['conflictingValue']}'")

    # Test: With only folder and case (no document)
    print("\n2. Testing with folder and case only (no document)...")
    winner2, conflicts2 = resolve_conflict([case_entry, folder_entry])

    # Assert: Folder should win
    assert winner2.source == ContextSource.FOLDER, \
        f"Expected FOLDER to win, but got {winner2.source}"
    assert winner2.value == "Ahmad Ali (Folder)", \
        f"Expected folder value, got {winner2.value}"

    print(f"✓ Folder context takes precedence over case: '{winner2.value}'")

    # Test: With only case (no folder or document)
    print("\n3. Testing with case only...")
    winner3, conflicts3 = resolve_conflict([case_entry])

    # Assert: Case should be used (no conflict)
    assert winner3.source == ContextSource.CASE, \
        f"Expected CASE, but got {winner3.source}"
    assert len(conflicts3) == 0, f"Expected no conflicts, got {len(conflicts3)}"

    print(f"✓ Case context used when no higher precedence available: '{winner3.value}'")

    print("\n✓ TC-S2-004-01 PASSED: Context precedence works correctly")
    print("  Document > Folder > Case hierarchy verified")
    return True


if __name__ == "__main__":
    try:
        result = test_context_precedence()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-01 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-01 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
