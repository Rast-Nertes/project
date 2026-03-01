"""
PATCH /api/v1/notifications — Mark as read (own notifications)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Notification, Users
from schemas.notifications import NotificationUpdate, NotificationOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.patch("/{notif_id}", response_model=NotificationOut)
async def update_notification(
    notif_id: int,
    data: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Обновить уведомление (например, пометить прочитанным — И)."""
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    if notif.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(notif, field, value)
    await db.commit()
    await db.refresh(notif)
    return notif
