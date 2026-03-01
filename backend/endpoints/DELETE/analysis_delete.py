"""
DELETE /api/v1/analysis — Delete analysis (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Analysis, Users
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Удалить анализ (только admin — У)."""
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    await db.delete(item)
    await db.commit()
