"""
POST /api/v1/payments — Create subscription and payment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import Payment, Plan, Subscription, Users
from schemas.payments import PaymentCreate, PaymentOut, SubscriptionCreate, SubscriptionOut
from middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.post("/subscriptions", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Подписаться на тарифный план."""
    plan_result = await db.execute(select(Plan).where(Plan.id == data.plan_id))
    plan = plan_result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Тарифный план не найден")

    sub = Subscription(
        user_id=current_user.id,
        plan_id=data.plan_id,
        started_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Создать платёж за подписку."""
    sub_result = await db.execute(
        select(Subscription).where(
            (Subscription.id == data.subscription_id) &
            (Subscription.user_id == current_user.id)
        )
    )
    if not sub_result.scalars().first():
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    payment = Payment(**data.model_dump())
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment
