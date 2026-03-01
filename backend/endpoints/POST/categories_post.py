"""
POST /api/v1/categories — Create category (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Category, Users
from schemas.categories import CategoryCreate, CategoryOut
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Создать категорию (только admin — Ф)."""
    existing = await db.execute(select(Category).where(Category.name == data.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Категория уже существует")

    cat = Category(name=data.name)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat
