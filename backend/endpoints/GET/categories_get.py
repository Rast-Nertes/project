"""
GET /api/v1/categories — Category retrieval
GET /api/v1/assets — Asset retrieval
Access: all authenticated users
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Category, Users
from schemas.categories import CategoryOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=list[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    """Список всех категорий."""
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return cat
