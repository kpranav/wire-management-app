"""Tests for WebSocket functionality."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_websocket_connection(client: AsyncClient):
    """Test WebSocket connection."""
    # Note: Testing WebSocket with httpx is limited
    # This is a basic connectivity test
    # For full WebSocket testing, consider using websockets library

    async with client.websocket_connect("/ws") as websocket:
        # Send a test message
        await websocket.send_text("test")

        # Receive acknowledgment
        data = await websocket.receive_json()

        assert data["type"] == "ack"
        assert "message" in data
