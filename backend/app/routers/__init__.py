"""Routers package."""
from app.routers.auth import router as auth_router
from app.routers.websocket import router as websocket_router
from app.routers.wires import router as wires_router

__all__ = ["auth_router", "wires_router", "websocket_router"]
