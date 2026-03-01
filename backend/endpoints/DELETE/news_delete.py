"""
DELETE /api/v1/news — Delete news (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import News, Users
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Удалить новость (только admin — У)."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await db.delete(news)
    await db.commit()
