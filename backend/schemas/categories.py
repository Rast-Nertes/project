"""
Insight IS — Pydantic Schemas: Categories & Assets
"""

from typing import Optional
from pydantic import BaseModel


# ── Categories ─────────────────────────────────

class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── Assets ─────────────────────────────────────

class AssetCreate(BaseModel):
    name: str
    ticker: str
    asset_type: str = "stock"
    exchange: Optional[str] = None


class AssetOut(BaseModel):
    id: int
    name: str
    ticker: str
    asset_type: str
    exchange: Optional[str] = None

    model_config = {"from_attributes": True}
