"""
Insight IS — Alpha Vantage Client (alphavantage.co)
Financial market data: stock quotes, time series.
"""

from typing import Optional
import httpx
from loguru import logger


class AlphaVantageClient:
    BASE = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get real-time global stock quote."""
        if not self.api_key:
            logger.warning("Alpha Vantage key not set")
            return None
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(self.BASE, params=params)
                resp.raise_for_status()
                data = resp.json()
                q = data.get("Global Quote", {})
                return {
                    "symbol": q.get("01. symbol"),
                    "price": float(q.get("05. price", 0)),
                    "change": float(q.get("09. change", 0)),
                    "change_pct": q.get("10. change percent", "0%"),
                    "volume": int(q.get("06. volume", 0)),
                }
            except Exception as e:
                logger.error(f"Alpha Vantage error: {e}")
                return None

    async def get_news_sentiment(self, tickers: str) -> list:
        """Get news & sentiment for tickers (premium endpoint)."""
        if not self.api_key:
            return []
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": tickers,
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                resp = await client.get(self.BASE, params=params)
                resp.raise_for_status()
                return resp.json().get("feed", [])
            except Exception as e:
                logger.error(f"Alpha Vantage sentiment error: {e}")
                return []
