"""
GET /api/v1/analysis — Analysis retrieval
Access: all authenticated users (Ч per access matrix)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import get_db
from database.models import Analysis, Users
from schemas.analysis import AnalysisOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=list[AnalysisOut])
async def list_analysis(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    asset_id: int | None = None,
    sentiment: str | None = None,
    impact: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    """Список аналитических записей с фильтром по активу, тональности, влиянию."""
    query = select(Analysis).options(selectinload(Analysis.news))
    filters = []
    if asset_id:
        filters.append(Analysis.asset_id == asset_id)
    if sentiment:
        filters.append(Analysis.sentiment == sentiment)
    if impact:
        filters.append(Analysis.impact == impact)
    if filters:
        from sqlalchemy import and_
        query = query.where(and_(*filters))
    query = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    return item
