"""
PATCH /api/v1/news — Update news (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import News, Users
from schemas.news import NewsUpdate, NewsOut
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.patch("/{news_id}", response_model=NewsOut)
async def update_news(
    news_id: int,
    data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Обновить новость (только admin — И)."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(news, field, value)
    await db.commit()
    await db.refresh(news)
    return news
