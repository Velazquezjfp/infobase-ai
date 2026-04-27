"""
TC-S2-004-05: PDFProcessor NotImplementedError Test

Tests that PDFProcessor.extract_text() raises NotImplementedError
with a helpful message directing users to Phase 3 implementation.
"""

import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.tools.pdf_processor import PDFProcessor


def test_pdf_processor_not_implemented():
    """Test PDFProcessor raises NotImplementedError with helpful message."""
    print("=" * 70)
    print("TC-S2-004-05: PDFProcessor NotImplementedError Test")
    print("=" * 70)

    # Setup: Create a temporary fake PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        temp_file = f.name
        f.write(b'%PDF-1.4\n%Fake PDF content for testing')

    try:
        # Test 1: Create processor
        print("\n1. Creating PDFProcessor instance...")
        processor = PDFProcessor()
        print(f"✓ PDFProcessor created")

        # Test 2: Try to extract text - should raise NotImplementedError
        print("\n2. Testing extract_text() raises NotImplementedError...")
        error_raised = False
        error_message = None

        try:
            processor.extract_text(temp_file)
        except NotImplementedError as e:
            error_raised = True
            error_message = str(e)
        except Exception as e:
            raise AssertionError(
                f"Expected NotImplementedError, got {type(e).__name__}: {e}"
            )

        assert error_raised, "extract_text() did not raise NotImplementedError"
        print(f"✓ NotImplementedError raised as expected")

        # Test 3: Verify error message is helpful
        print("\n3. Verifying error message content...")
        assert error_message is not None, "Error message is None"

        # Check for key phrases in the error message
        expected_phrases = [
            "PDF",
            "not yet implemented",
            "Phase 3",
            ".txt"
        ]

        for phrase in expected_phrases:
            assert phrase in error_message, \
                f"Expected phrase '{phrase}' not found in error message"

        print(f"✓ Error message is helpful and informative:")
        print(f"  '{error_message[:100]}...'")

        # Test 4: Verify get_metadata returns basic metadata (doesn't raise error)
        print("\n4. Testing get_metadata() returns basic info...")
        metadata = processor.get_metadata(temp_file)

        assert metadata is not None, "Metadata is None"
        assert metadata.file_extension == '.pdf', \
            f"Wrong extension: {metadata.file_extension}"
        assert metadata.content_type == 'application/pdf', \
            f"Wrong content type: {metadata.content_type}"
        assert 'pdfSupport' in metadata.extra, "Missing stub indicator in metadata"
        assert metadata.extra['pdfSupport'] == 'stub', \
            f"Wrong stub indicator: {metadata.extra['pdfSupport']}"

        print(f"✓ get_metadata() returns basic file info without error")
        print(f"  - Content type: {metadata.content_type}")
        print(f"  - Stub status: {metadata.extra.get('pdfSupport')}")

        print("\n✓ TC-S2-004-05 PASSED: PDFProcessor correctly raises NotImplementedError")
        print("  with helpful message directing to Phase 3")
        return True

    finally:
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        result = test_pdf_processor_not_implemented()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-05 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-05 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
