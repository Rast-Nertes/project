"""
Insight IS — WebSocket Notification Manager
Manages active WebSocket connections per user_id.
Used by notification endpoints to broadcast real-time events.
"""

from typing import Dict, List
from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    def __init__(self):
        # user_id -> list of active connections (multi-tab/device support)
        self._connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user_id={user_id} | total={self.total}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self._connections:
            self._connections[user_id].discard(websocket) if hasattr(
                self._connections[user_id], "discard"
            ) else None
            try:
                self._connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id} | total={self.total}")

    async def send_to_user(self, user_id: int, message: dict):
        """Send JSON message to all connections of a specific user."""
        connections = self._connections.get(user_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)

    async def broadcast(self, message: dict):
        """Broadcast JSON message to ALL connected users."""
        for user_id in list(self._connections.keys()):
            await self.send_to_user(user_id, message)

    @property
    def total(self) -> int:
        return sum(len(v) for v in self._connections.values())


# Singleton — imported by endpoints
manager = ConnectionManager()
