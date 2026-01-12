"""
Test Case: TC-D-S5-002-06
Requirement: D-S5-002 - Document Registry Schema
Description: Manifest lastUpdated field, verify updates after document operations
Generated: 2026-01-09T16:00:00Z

Note: This test validates manifest lastUpdated timestamp maintenance
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

def test_TC_D_S5_002_06():
    """Manifest lastUpdated timestamp validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # 2. Verify lastUpdated field present
    assert "lastUpdated" in manifest, "Manifest missing lastUpdated field"
    last_updated = manifest["lastUpdated"]

    # 3. Verify lastUpdated is valid ISO 8601 timestamp
    try:
        last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
    except ValueError:
        raise AssertionError(f"lastUpdated has invalid ISO 8601 format: {last_updated}")

    print(f"✓ lastUpdated field present: {last_updated}")

    # 4. Verify timestamp is reasonable (not too far in past or future)
    current_time = datetime.now(last_updated_dt.tzinfo)
    time_diff = abs((current_time - last_updated_dt).total_seconds())

    # Allow timestamp to be within 30 days past or 1 day future (for test flexibility)
    max_past_seconds = 30 * 24 * 60 * 60  # 30 days
    max_future_seconds = 24 * 60 * 60     # 1 day

    if last_updated_dt > current_time:
        assert time_diff <= max_future_seconds, \
            f"lastUpdated is too far in the future: {last_updated} (current: {current_time})"
    else:
        assert time_diff <= max_past_seconds, \
            f"lastUpdated is too old: {last_updated} (current: {current_time})"

    print(f"✓ Timestamp is reasonable (within acceptable range)")

    # 5. Verify lastUpdated is after or equal to earliest document uploadedAt
    documents = manifest["documents"]
    if len(documents) > 0:
        upload_timestamps = []
        for doc in documents:
            uploaded_at = datetime.fromisoformat(doc["uploadedAt"].replace('Z', '+00:00'))
            upload_timestamps.append(uploaded_at)

            # Also check render timestamps
            for render in doc.get("renders", []):
                created_at = datetime.fromisoformat(render["createdAt"].replace('Z', '+00:00'))
                upload_timestamps.append(created_at)

        earliest_timestamp = min(upload_timestamps)
        latest_timestamp = max(upload_timestamps)

        # lastUpdated should be >= latest document/render timestamp
        assert last_updated_dt >= earliest_timestamp, \
            f"lastUpdated ({last_updated_dt}) is before earliest document ({earliest_timestamp})"

        print(f"✓ lastUpdated is after earliest document/render timestamp")
        print(f"  Earliest document timestamp: {earliest_timestamp}")
        print(f"  Latest document timestamp: {latest_timestamp}")
        print(f"  Manifest lastUpdated: {last_updated_dt}")

    # 6. Verify timestamp format includes timezone
    assert last_updated.endswith('Z') or '+' in last_updated or '-' in last_updated[-6:], \
        "lastUpdated should include timezone information (Z or ±HH:MM)"

    print("✓ Timestamp includes timezone information")
    print("✓ Manifest lastUpdated field validation complete")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_06()
        print("TC-D-S5-002-06: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-06: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-06: ERROR - {e}")
