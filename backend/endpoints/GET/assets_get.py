"""
GET /api/v1/assets — Asset retrieval
Access: all authenticated users
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Asset, Users
from schemas.categories import AssetOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=list[AssetOut])
async def list_assets(
    asset_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    """Список всех финансовых активов, опционально фильтр по типу."""
    query = select(Asset)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    result = await db.execute(query.order_by(Asset.ticker))
    return result.scalars().all()


@router.get("/{asset_id}", response_model=AssetOut)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Актив не найден")
    return asset
