"""
POST /api/v1/news — Create news (admin only)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import News, Users
from schemas.news import NewsCreate, NewsOut
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.post("/", response_model=NewsOut, status_code=status.HTTP_201_CREATED)
async def create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Создать новость вручную (только admin — Ф)."""
    news = News(**data.model_dump())
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news
