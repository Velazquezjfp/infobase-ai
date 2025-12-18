#!/usr/bin/env python3
"""Simple WebSocket connection test"""

import asyncio
import json
import websockets

async def test_simple_connection():
    """Test basic WebSocket connection"""
    try:
        print("Connecting to ws://localhost:8000/ws/chat/ACTE-2024-001...")
        async with websockets.connect("ws://localhost:8000/ws/chat/ACTE-2024-001") as ws:
            print("Connected successfully!")

            # Wait for connection confirmation
            confirmation = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"Received confirmation: {confirmation}")

            # Send a simple message
            print("Sending Hello message...")
            await ws.send(json.dumps({
                "type": "chat",
                "content": "Hello",
                "caseId": "ACTE-2024-001"
            }))

            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            print(f"Received response: {response[:200]}...")

            print("\n✅ WebSocket connection test PASSED")
            return True

    except asyncio.TimeoutError:
        print("\n❌ Test FAILED: Timeout waiting for response")
        return False
    except Exception as e:
        print(f"\n❌ Test FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_connection())
    exit(0 if result else 1)
