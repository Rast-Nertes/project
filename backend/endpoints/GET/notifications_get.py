"""
GET /api/v1/notifications — Notifications for the current user
Access: authenticated users (own), admin (all)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Notification, Users
from schemas.notifications import NotificationOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=list[NotificationOut])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Список уведомлений для текущего пользователя."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)  # noqa: E712
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{notif_id}", response_model=NotificationOut)
async def get_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    if notif.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return notif
