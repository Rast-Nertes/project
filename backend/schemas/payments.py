"""
Insight IS — Pydantic Schemas: Payments & Subscriptions
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Subscriptions ─────────────────────────────

class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    model_config = {"from_attributes": True}


# ── Payments ──────────────────────────────────

class PaymentCreate(BaseModel):
    subscription_id: int
    amount: float
    transaction_id: str


class PaymentOut(BaseModel):
    id: int
    subscription_id: int
    amount: float
    transaction_id: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
