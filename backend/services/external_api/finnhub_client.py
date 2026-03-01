"""
Insight IS — Finnhub Client (finnhub.io)
Real-time stock quotes, company news, sentiment.
"""

from typing import Optional, List
import httpx
from loguru import logger


class FinnhubClient:
    BASE = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_quote(self, symbol: str) -> Optional[dict]:
        if not self.api_key:
            return None
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.BASE}/quote",
                    params={"symbol": symbol, "token": self.api_key}
                )
                resp.raise_for_status()
                d = resp.json()
                return {
                    "symbol": symbol,
                    "current": d.get("c"),
                    "high": d.get("h"),
                    "low": d.get("l"),
                    "open": d.get("o"),
                    "prev_close": d.get("pc"),
                    "change": d.get("d"),
                    "change_pct": d.get("dp"),
                }
            except Exception as e:
                logger.error(f"Finnhub quote error: {e}")
                return None

    async def get_company_news(self, symbol: str, date_from: str, date_to: str) -> List[dict]:
        """Get company news. Dates format: YYYY-MM-DD."""
        if not self.api_key:
            return []
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.BASE}/company-news",
                    params={"symbol": symbol, "from": date_from, "to": date_to, "token": self.api_key}
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f"Finnhub news error: {e}")
                return []

    async def get_sentiment(self, symbol: str) -> Optional[dict]:
        """Get news sentiment for a symbol."""
        if not self.api_key:
            return None
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.BASE}/news-sentiment",
                    params={"symbol": symbol, "token": self.api_key}
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f"Finnhub sentiment error: {e}")
                return None
