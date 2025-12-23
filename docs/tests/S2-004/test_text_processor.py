"""
TC-S2-004-03: TextProcessor Text Extraction Test

Tests that TextProcessor correctly extracts text content from .txt files
with proper encoding detection and normalization.
"""

import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.tools.text_processor import TextProcessor
from backend.tools.document_processor import get_processor


def test_text_processor_extraction():
    """Test TextProcessor extracts text correctly from .txt files."""
    print("=" * 70)
    print("TC-S2-004-03: TextProcessor Text Extraction Test")
    print("=" * 70)

    # Setup: Create a temporary text file with known content
    test_content = """Birth Certificate
Vorname: Ahmad
Nachname: Ali
Geburtsdatum: 15.05.1990
Geburtsort: Kabul, Afghanistan

This is a test document with German umlauts: äöüÄÖÜß
Line endings should be normalized."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        temp_file = f.name
        f.write(test_content)

    try:
        # Test 1: Get processor for .txt file
        print("\n1. Testing processor registry for .txt files...")
        processor = get_processor(temp_file)

        assert processor is not None, "No processor found for .txt file"
        assert isinstance(processor, TextProcessor), \
            f"Expected TextProcessor, got {type(processor)}"

        print(f"✓ TextProcessor registered for .txt files")

        # Test 2: Extract text content
        print("\n2. Testing text extraction...")
        extracted_text = processor.extract_text(temp_file)

        assert extracted_text is not None, "Extracted text is None"
        assert len(extracted_text) > 0, "Extracted text is empty"
        assert "Ahmad" in extracted_text, "Expected content not found in extracted text"
        assert "Ali" in extracted_text, "Expected content not found"
        assert "Kabul" in extracted_text, "Expected content not found"

        print(f"✓ Text extracted successfully ({len(extracted_text)} characters)")
        print(f"✓ Content verification passed")

        # Test 3: Verify encoding handling (German umlauts)
        print("\n3. Testing encoding handling...")
        assert "äöü" in extracted_text, "German umlauts not preserved"
        assert "ÄÖÜ" in extracted_text, "German umlauts (uppercase) not preserved"
        assert "ß" in extracted_text, "German sharp s not preserved"

        print(f"✓ UTF-8 encoding correctly handled (German umlauts preserved)")

        # Test 4: Get metadata
        print("\n4. Testing metadata extraction...")
        metadata = processor.get_metadata(temp_file)

        assert metadata is not None, "Metadata is None"
        assert metadata.file_extension == '.txt', \
            f"Wrong extension: {metadata.file_extension}"
        assert metadata.content_type == 'text/plain', \
            f"Wrong content type: {metadata.content_type}"
        assert metadata.encoding is not None, "Encoding not detected"
        assert metadata.file_size > 0, "File size not captured"

        print(f"✓ Metadata extracted:")
        print(f"  - File size: {metadata.file_size} bytes")
        print(f"  - Encoding: {metadata.encoding}")
        print(f"  - Content type: {metadata.content_type}")

        # Test 5: Verify supports_format
        print("\n5. Testing format support check...")
        assert processor.supports_format('.txt'), ".txt not supported"
        assert processor.supports_format('.text'), ".text not supported"
        assert not processor.supports_format('.pdf'), "PDF should not be supported"

        print(f"✓ Format support check works correctly")

        print("\n✓ TC-S2-004-03 PASSED: TextProcessor extracts text correctly")
        return True

    finally:
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        result = test_text_processor_extraction()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ TC-S2-004-03 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TC-S2-004-03 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
