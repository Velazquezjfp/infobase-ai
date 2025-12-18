#!/usr/bin/env python3
"""Single test for debugging"""

import asyncio
import json
import time
import websockets

async def test_single():
    """Test a single request"""
    ws_url = "ws://localhost:8000/ws/chat/ACTE-2024-001"

    print("Connecting...")
    async with websockets.connect(ws_url) as ws:
        print("Connected!")

        # Wait for confirmation
        confirmation = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print(f"Confirmation: {confirmation}")

        # Send message
        start = time.perf_counter()
        await ws.send(json.dumps({
            "type": "chat",
            "content": "Hello",
            "caseId": "ACTE-2024-001",
            "stream": True
        }))
        print("Message sent")

        # Get first response
        response1 = await asyncio.wait_for(ws.recv(), timeout=10.0)
        first_token_time = (time.perf_counter() - start) * 1000
        print(f"First token time: {first_token_time:.2f}ms")
        print(f"First response: {response1[:200]}")

        # Get second response to check format
        response2 = await asyncio.wait_for(ws.recv(), timeout=10.0)
        print(f"Second response: {response2[:200]}")

        # Get third response
        response3 = await asyncio.wait_for(ws.recv(), timeout=10.0)
        print(f"Third response: {response3[:200]}")

if __name__ == "__main__":
    asyncio.run(test_single())
