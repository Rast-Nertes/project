"""
DELETE /api/v1/notifications — Delete notification
Admin can delete any; users can delete own.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Notification, Users
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.delete("/{notif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Удалить уведомление. Admin — любое; пользователь — своё (У)."""
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    if notif.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    await db.delete(notif)
    await db.commit()
