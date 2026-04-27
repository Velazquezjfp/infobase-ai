"""
TC-S2-004-07: Case Context Fallback Test

Tests that when no folder context is available, the system correctly
falls back to using case context for AI prompts.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.context_manager import ContextManager


def test_case_context_fallback():
    """Test case context is used as fallback when folder context missing."""
    print("=" * 70)
    print("TC-S2-004-07: Case Context Fallback Test")
    print("=" * 70)

    # Setup: Initialize context manager
    print("\n1. Initializing ContextManager...")
    try:
        context_mgr = ContextManager()
        print(f"✓ ContextManager initialized")
    except Exception as e:
        print(f"✗ Failed to initialize ContextManager: {e}")
        raise

    # Test 1: Load case context
    print("\n2. Loading case context for ACTE-2024-001...")
    try:
        case_ctx = context_mgr.load_case_context("ACTE-2024-001")
        assert case_ctx is not None, "Case context is None"
        assert 'caseId' in case_ctx, "Missing caseId in case context"
        assert case_ctx['caseId'] == "ACTE-2024-001", \
            f"Wrong case ID: {case_ctx.get('caseId')}"

        print(f"✓ Case context loaded successfully")
        print(f"  - Case ID: {case_ctx.get('caseId')}")
        print(f"  - Case Type: {case_ctx.get('caseType')}")
    except Exception as e:
        print(f"✗ Failed to load case context: {e}")
        raise

    # Test 2: Try to load non-existent folder context (should return None)
    print("\n3. Attempting to load non-existent folder context...")
    folder_ctx = context_mgr.load_folder_context(
        "ACTE-2024-001",
        "non-existent-folder"
    )

    assert folder_ctx is None, \
        f"Expected None for non-existent folder, got {type(folder_ctx)}"

    print(f"✓ Non-existent folder context returns None (graceful fallback)")

    # Test 3: Merge contexts with no folder context
    print("\n4. Testing merge with case context only (no folder)...")
    merged = context_mgr.merge_contexts(
        case_ctx=case_ctx,
        folder_ctx=None,  # No folder context
        doc_ctx="Test document content"
    )

    assert merged is not None, "Merged context is None"
    assert len(merged) > 0, "Merged context is empty"
    assert "CASE CONTEXT" in merged, "Case context section missing"
    assert "ACTE-2024-001" in merged, "Case ID not in merged context"
    assert "FOLDER CONTEXT" not in merged, \
        "Folder context should not appear when None"

    print(f"✓ Merge successful with case context only")
    print(f"  - Merged context length: {len(merged)} characters")
    print(f"  - Contains case information: Yes")
    print(f"  - Contains folder information: No (as expected)")

    # Test 4: Merge with tracking (enhanced method)
    print("\n5. Testing merge_contexts_with_tracking fallback...")
    merged_tracked = context_mgr.merge_contexts_with_tracking(
        case_ctx=case_ctx,
        folder_ctx=None,
        doc_ctx="Test document",
        doc_name="test.txt"
    )

    assert merged_tracked is not None, "Tracked merge result is None"
    assert merged_tracked.prompt_text is not None, "Prompt text is None"
    assert len(merged_tracked.sources) >= 1, "No sources tracked"

    # Should have case and document, but not folder
    source_types = [s.split(":")[0] for s in merged_tracked.sources]
    assert "Case" in source_types, "Case not in sources"
    assert "Document" in source_types, "Document not in sources"
    assert "Folder" not in source_types, "Folder should not be in sources"

    print(f"✓ Tracking correctly shows sources used:")
    print(f"  - Sources: {merged_tracked.get_source_summary()}")
    print(f"  - Entries tracked: {len(merged_tracked.entries)}")

    print("\n✓ TC-S2-004-07 PASSED: Case context used as fallback")
    print("  when folder context is not available")
    return True


if __name__ == "__main__":
    try:
        result = test_case_context_fallback()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-07 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-07 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
