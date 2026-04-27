"""
TC-S2-004-04: PDFProcessor Format Support Test

Tests that PDFProcessor correctly reports supporting .pdf format,
even though full extraction is not yet implemented (stub).
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.tools.pdf_processor import PDFProcessor
from backend.tools.document_processor import get_processor, is_supported


def test_pdf_processor_format_support():
    """Test PDFProcessor reports .pdf format as supported."""
    print("=" * 70)
    print("TC-S2-004-04: PDFProcessor Format Support Test")
    print("=" * 70)

    # Test 1: Create PDFProcessor instance
    print("\n1. Testing PDFProcessor instantiation...")
    processor = PDFProcessor()

    assert processor is not None, "Failed to create PDFProcessor instance"
    print(f"✓ PDFProcessor instance created")

    # Test 2: Check supports_format method with .pdf
    print("\n2. Testing supports_format('.pdf')...")
    supports_pdf = processor.supports_format('.pdf')

    assert supports_pdf is True, \
        f"PDFProcessor.supports_format('.pdf') returned {supports_pdf}, expected True"

    print(f"✓ PDFProcessor.supports_format('.pdf') = True")

    # Test 3: Check supports_format with variations
    print("\n3. Testing format variations...")
    assert processor.supports_format('pdf'), "Should support 'pdf' without dot"
    assert processor.supports_format('.PDF'), "Should support uppercase '.PDF'"
    assert not processor.supports_format('.txt'), "Should not support .txt"

    print(f"✓ Format variations handled correctly")

    # Test 4: Check processor registry
    print("\n4. Testing processor registry...")
    pdf_processor = get_processor('document.pdf')

    assert pdf_processor is not None, "No processor found for .pdf file"
    assert isinstance(pdf_processor, PDFProcessor), \
        f"Expected PDFProcessor, got {type(pdf_processor)}"

    print(f"✓ PDFProcessor registered in processor registry")

    # Test 5: Check global is_supported function
    print("\n5. Testing global is_supported function...")
    assert is_supported('document.pdf'), ".pdf should be supported"
    assert is_supported('file.PDF'), "Uppercase .PDF should be supported"

    print(f"✓ Global is_supported function works for PDF")

    print("\n✓ TC-S2-004-04 PASSED: PDFProcessor supports .pdf format")
    print("  (Note: Full extraction not implemented yet - stub for Phase 3)")
    return True


if __name__ == "__main__":
    try:
        result = test_pdf_processor_format_support()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-04 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-04 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
