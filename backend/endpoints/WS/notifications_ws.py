"""
WebSocket /ws/notifications — Real-time notification push
Clients connect with JWT token as query param: /ws/notifications?token=<access_token>
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from loguru import logger

from services.auth_service import decode_access_token
from services.notification_service import manager

router = APIRouter()


@router.websocket("/notifications")
async def ws_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    WebSocket endpoint для получения уведомлений в реальном времени.
    Подключение: ws://host/ws/notifications?token=<access_token>
    """
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("WebSocket: отклонён — недействительный токен")
        return

    user_id: int = int(payload.get("sub", 0))
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)
    try:
        # Send welcome message
        await websocket.send_json({"type": "connected", "user_id": user_id})
        # Keep connection alive — wait for any client pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: user_id={user_id}")
