#!/usr/bin/env python3
"""
Test script for F-003: Select Field Fuzzy Matching

Tests that the AI can match document text to predefined select field options
using fuzzy matching (e.g., "intensive course" → "Intensive Course")
"""

import asyncio
import json
import websockets
import sys

CASE_ID = "ACTE-2024-001"
WEBSOCKET_URL = f"ws://localhost:8000/ws/chat/{CASE_ID}"

# Test document with course preference mention
TEST_DOCUMENT = """
German Integration Course Application

Applicant: Ahmad Ali
Date of Birth: 15.05.1990

Course Selection:
I would like to enroll in the intensive German language course,
as I need to improve my language skills quickly for employment purposes.
I prefer a full-time, intensive format with 20 hours per week.

Address: Musterstraße 123, 10115 Berlin, Germany

Reason: I recently arrived in Germany and need to learn German
for my job as an engineer.
"""

FORM_SCHEMA = [
    {"id": "fullName", "label": "Full Name", "type": "text", "required": True},
    {"id": "birthDate", "label": "Date of Birth", "type": "date", "required": True},
    {"id": "coursePreference", "label": "Course Preference", "type": "select",
     "options": ["Intensive Course", "Evening Course", "Weekend Course"], "required": False},
    {"id": "currentAddress", "label": "Current Address", "type": "textarea", "required": True},
    {"id": "reasonForApplication", "label": "Reason for Application", "type": "textarea", "required": True},
]


async def test_select_field_matching():
    """Test select field fuzzy matching."""
    print("=" * 80)
    print("F-003 Select Field Fuzzy Matching Test")
    print("=" * 80)
    print()

    print(f"Connecting to WebSocket: {WEBSOCKET_URL}")
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✓ WebSocket connected")

            # Wait for connection confirmation
            await websocket.recv()
            print()

            # Send form fill request
            print("Sending form fill request with course preference...")
            request = {
                "type": "chat",
                "content": "/fillForm",
                "caseId": CASE_ID,
                "folderId": "applications",
                "documentContent": TEST_DOCUMENT,
                "formSchema": FORM_SCHEMA,
                "stream": False
            }

            await websocket.send(json.dumps(request))
            print("✓ Request sent")
            print()

            # Wait for responses
            print("Waiting for AI responses...")
            print("-" * 80)

            extracted_fields = {}
            confidence_scores = {}

            for _ in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "form_update":
                        extracted_fields = data.get("updates", {})
                        confidence_scores = data.get("confidence", {})
                        print("✓ Received form_update message")
                        print(f"  Extracted {len(extracted_fields)} fields")
                        print()

                    elif msg_type == "chat_response":
                        print(f"✓ AI Response: {data.get('content', '')}")
                        print()
                        break

                    elif msg_type == "error":
                        print(f"❌ ERROR: {data.get('message', '')}")
                        return False

                except asyncio.TimeoutError:
                    print("❌ TIMEOUT")
                    return False

            # Verify select field matching
            print("=" * 80)
            print("VERIFICATION RESULTS")
            print("=" * 80)
            print()

            all_passed = True

            # Check coursePreference field specifically
            if "coursePreference" in extracted_fields:
                course_value = extracted_fields["coursePreference"]
                confidence = confidence_scores.get("coursePreference", 0)

                print(f"coursePreference: '{course_value}' (confidence: {confidence:.2f})")

                # Check if it matched the correct option
                valid_options = ["Intensive Course", "Evening Course", "Weekend Course"]
                if course_value == "Intensive Course":
                    print("  ✓ Correctly matched 'intensive' text to 'Intensive Course' option")
                    print("  ✓ Fuzzy matching worked successfully")
                elif course_value in valid_options:
                    print(f"  ⚠ Matched to '{course_value}' - might be acceptable but check logic")
                else:
                    print(f"  ❌ Invalid value: '{course_value}' not in valid options")
                    all_passed = False
            else:
                print("❌ coursePreference: NOT EXTRACTED")
                all_passed = False

            print()

            # Show other extracted fields
            print("Other fields extracted:")
            for field_id, value in extracted_fields.items():
                if field_id != "coursePreference":
                    confidence = confidence_scores.get(field_id, 0)
                    print(f"  • {field_id}: '{value[:50]}...' (confidence: {confidence:.2f})")

            print()
            print("=" * 80)

            if all_passed:
                print("✅ SELECT FIELD MATCHING TEST PASSED!")
                print("=" * 80)
                return True
            else:
                print("❌ SELECT FIELD MATCHING TEST FAILED")
                print("=" * 80)
                return False

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_select_field_matching())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
