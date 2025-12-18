#!/usr/bin/env python3
"""
Test script for F-003: Form Auto-Fill from Document Content

This script tests the form extraction functionality by sending a form fill
request with German document content and verifying the AI extracts the correct
fields with proper date format conversion.
"""

import asyncio
import json
import websockets
import sys
from pathlib import Path

# Test configuration
CASE_ID = "ACTE-2024-001"
WEBSOCKET_URL = f"ws://localhost:8000/ws/chat/{CASE_ID}"

# Load the Birth Certificate document
BIRTH_CERT_PATH = Path("public/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt")

# Form schema (Integration Course Application form)
FORM_SCHEMA = [
    {"id": "fullName", "label": "Full Name", "type": "text", "required": True},
    {"id": "birthDate", "label": "Date of Birth", "type": "date", "required": True},
    {"id": "countryOfOrigin", "label": "Country of Origin", "type": "text", "required": True},
    {"id": "existingLanguageCertificates", "label": "Existing Language Certificates", "type": "text", "required": False},
    {"id": "coursePreference", "label": "Course Preference", "type": "select", "options": ["Intensive Course", "Evening Course", "Weekend Course"], "required": False},
    {"id": "currentAddress", "label": "Current Address", "type": "textarea", "required": True},
    {"id": "reasonForApplication", "label": "Reason for Application", "type": "textarea", "required": True},
]

# Expected results
EXPECTED_RESULTS = {
    "fullName": "Ahmad Ali",
    "birthDate": "1990-05-15",  # Converted from German format 15.05.1990
    "countryOfOrigin": "Afghanistan"
}


async def test_form_autofill():
    """Test form auto-fill with German birth certificate."""
    print("=" * 80)
    print("F-003 Form Auto-Fill Test")
    print("=" * 80)
    print()

    # Load document content
    if not BIRTH_CERT_PATH.exists():
        print(f"❌ ERROR: Document not found: {BIRTH_CERT_PATH}")
        return False

    with open(BIRTH_CERT_PATH, 'r', encoding='utf-8') as f:
        document_content = f.read()

    print(f"✓ Loaded document: {BIRTH_CERT_PATH}")
    print(f"  Document length: {len(document_content)} characters")
    print()

    # Connect to WebSocket
    print(f"Connecting to WebSocket: {WEBSOCKET_URL}")
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✓ WebSocket connected")
            print()

            # Wait for connection confirmation
            connection_msg = await websocket.recv()
            conn_data = json.loads(connection_msg)
            print(f"✓ Connection confirmed: {conn_data.get('content', '')}")
            print()

            # Send form fill request
            print("Sending form fill request...")
            request = {
                "type": "chat",
                "content": "/fillForm",
                "caseId": CASE_ID,
                "folderId": "personal-data",
                "documentContent": document_content,
                "formSchema": FORM_SCHEMA,
                "stream": False
            }

            await websocket.send(json.dumps(request))
            print("✓ Request sent")
            print()

            # Wait for responses
            print("Waiting for AI responses...")
            print("-" * 80)

            form_update_received = False
            extracted_fields = {}
            confidence_scores = {}

            # Collect responses (should receive form_update and chat_response)
            for _ in range(5):  # Max 5 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "form_update":
                        form_update_received = True
                        extracted_fields = data.get("updates", {})
                        confidence_scores = data.get("confidence", {})
                        print("✓ Received form_update message")
                        print(f"  Extracted {len(extracted_fields)} fields")
                        print()

                    elif msg_type == "chat_response":
                        print(f"✓ AI Response: {data.get('content', '')}")
                        print()
                        break  # Last message

                    elif msg_type == "error":
                        print(f"❌ ERROR: {data.get('message', 'Unknown error')}")
                        return False

                except asyncio.TimeoutError:
                    print("❌ TIMEOUT: No response within 30 seconds")
                    return False

            # Verify results
            print("=" * 80)
            print("VERIFICATION RESULTS")
            print("=" * 80)
            print()

            if not form_update_received:
                print("❌ FAILED: No form_update message received")
                return False

            # Check each expected field
            all_passed = True
            for field_id, expected_value in EXPECTED_RESULTS.items():
                if field_id in extracted_fields:
                    actual_value = extracted_fields[field_id]
                    confidence = confidence_scores.get(field_id, 0)

                    if actual_value == expected_value:
                        print(f"✓ {field_id}: '{actual_value}' (confidence: {confidence:.2f})")
                    else:
                        print(f"❌ {field_id}: Expected '{expected_value}', got '{actual_value}' (confidence: {confidence:.2f})")
                        all_passed = False
                else:
                    print(f"❌ {field_id}: NOT EXTRACTED")
                    all_passed = False

            print()

            # Show additional extracted fields
            extra_fields = set(extracted_fields.keys()) - set(EXPECTED_RESULTS.keys())
            if extra_fields:
                print("Additional fields extracted:")
                for field_id in extra_fields:
                    value = extracted_fields[field_id]
                    confidence = confidence_scores.get(field_id, 0)
                    print(f"  • {field_id}: '{value}' (confidence: {confidence:.2f})")
                print()

            # Special checks
            print("Special validations:")

            # Check date format conversion
            if "birthDate" in extracted_fields:
                birthdate = extracted_fields["birthDate"]
                if birthdate == "1990-05-15":
                    print("  ✓ Date format converted correctly: 15.05.1990 → 1990-05-15")
                else:
                    print(f"  ❌ Date format issue: Expected '1990-05-15', got '{birthdate}'")
                    all_passed = False

            # Check German → English field mapping
            if "fullName" in extracted_fields:
                fullname = extracted_fields["fullName"]
                if "Ahmad" in fullname and "Ali" in fullname:
                    print("  ✓ German labels mapped correctly: Vorname/Nachname → fullName")
                else:
                    print(f"  ⚠ Unexpected name format: '{fullname}'")

            print()
            print("=" * 80)

            if all_passed:
                print("✅ ALL TESTS PASSED!")
                print("=" * 80)
                return True
            else:
                print("❌ SOME TESTS FAILED")
                print("=" * 80)
                return False

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_form_autofill())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
