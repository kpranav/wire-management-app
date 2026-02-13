"""Tests for WebSocket functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="AsyncClient with ASGITransport doesn't support WebSocket. "
    "Use websockets library for WebSocket testing."
)
async def test_websocket_connection(client: AsyncClient):
    """Test WebSocket connection."""
    # Note: Testing WebSocket with httpx AsyncClient + ASGITransport is not supported
    # For full WebSocket testing, use the websockets library directly
    # Example: async with websockets.connect("ws://localhost:8000/ws") as websocket:

    async with client.websocket_connect("/ws") as websocket:
        # Send a test message
        await websocket.send_text("test")

        # Receive acknowledgment
        data = await websocket.receive_json()

        assert data["type"] == "ack"
        assert "message" in data
