"""WebSocket router for real-time updates."""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        # Create a copy to avoid modification during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove failed connection
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time wire updates."""
    await manager.connect(websocket)

    try:
        # Keep connection alive and listen for messages
        while True:
            # Receive data from client
            await websocket.receive_text()

            # Echo back or handle client messages
            await websocket.send_json(
                {
                    "type": "ack",
                    "message": "Message received",
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_wire_update(wire_id: int, status: str, user_id: int):
    """Broadcast wire status update to all connected clients."""
    message = {
        "type": "wire_update",
        "wire_id": wire_id,
        "status": status,
        "user_id": user_id,
        "timestamp": asyncio.get_event_loop().time(),
    }
    await manager.broadcast(message)
