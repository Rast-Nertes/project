"""
DELETE /api/v1/categories — Delete category (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Category, Users
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Удалить категорию (только admin — У)."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await db.delete(cat)
    await db.commit()
