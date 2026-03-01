"""
Insight IS — Polygon.io Client
Financial data: aggregates, tickers, news.
"""

from typing import Optional, List
import httpx
from loguru import logger


class PolygonClient:
    BASE = "https://api.polygon.io"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_ticker(self, symbol: str) -> Optional[dict]:
        """Get ticker details."""
        if not self.api_key:
            return None
        url = f"{self.BASE}/v3/reference/tickers/{symbol}"
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(url, params={"apiKey": self.api_key})
                resp.raise_for_status()
                result = resp.json().get("results", {})
                return {
                    "ticker": result.get("ticker"),
                    "name": result.get("name"),
                    "market": result.get("market"),
                    "type": result.get("type"),
                }
            except Exception as e:
                logger.error(f"Polygon ticker error: {e}")
                return None

    async def get_news(self, ticker: str, limit: int = 10) -> List[dict]:
        """Get news articles for a ticker."""
        if not self.api_key:
            return []
        url = f"{self.BASE}/v2/reference/news"
        params = {"ticker": ticker, "limit": limit, "apiKey": self.api_key}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json().get("results", [])
            except Exception as e:
                logger.error(f"Polygon news error: {e}")
                return []
