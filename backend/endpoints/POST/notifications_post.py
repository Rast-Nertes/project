"""
POST /api/v1/notifications — Create notification (admin only)
Admin broadcasts or targets a specific user.
After creation the notification is also pushed via WebSocket.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Notification, Users
from schemas.notifications import NotificationCreate, NotificationOut
from services.notification_service import manager
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Создать уведомление и отправить через WebSocket (только admin — Ф)."""
    notif = Notification(**data.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    # Push real-time WebSocket notification
    await manager.send_to_user(
        data.user_id,
        {
            "type": "notification",
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
        },
    )
    return notif
