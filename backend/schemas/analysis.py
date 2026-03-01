"""
Insight IS — Pydantic Schemas: Analysis
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.news import NewsOut

class AnalysisCreate(BaseModel):
    news_id: Optional[int] = None
    asset_id: Optional[int] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None   # positive / negative / neutral
    impact: Optional[str] = None      # high / medium / low
    confidence: Optional[float] = None


class AnalysisUpdate(BaseModel):
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    impact: Optional[str] = None
    confidence: Optional[float] = None


class AnalysisOut(BaseModel):
    id: int
    news_id: Optional[int] = None
    asset_id: Optional[int] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    impact: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    news: Optional[NewsOut] = None

    model_config = {"from_attributes": True}
