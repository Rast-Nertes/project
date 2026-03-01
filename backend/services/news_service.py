"""
Insight IS — News Collection Service
Aggregates news from multiple external APIs.
"""

import asyncio
from datetime import datetime
from typing import List, Optional
import httpx
from loguru import logger

from settings.settings import settings
from services.external_api.newsapi_client import NewsAPIClient
from services.external_api.gnews_client import GNewsClient
from services.external_api.newsdata_client import NewsDataClient


class NewsService:
    def __init__(self):
        self.newsapi = NewsAPIClient(settings.news_api_key)
        self.gnews = GNewsClient(settings.gnews_api_key)
        self.newsdata = NewsDataClient(settings.news_data_api_key)

    async def fetch_all(self, query: str = "finance", max_per_source: int = 10) -> List[dict]:
        """
        Параллельно собирает новости из всех источников.
        Возвращает нормализованный список статей:
        {title, content, source, url, publication_date, raw}
        """
        tasks = [
            self.newsapi.fetch(query, max_per_source),
            self.gnews.fetch(query, max_per_source),
            self.newsdata.fetch(query, max_per_source),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles: List[dict] = []
        for i, result in enumerate(results):
            source_name = ["NewsAPI", "GNews", "NewsData"][i]
            if isinstance(result, Exception):
                logger.error(f"{source_name} fetch error: {result}")
            else:
                logger.info(f"{source_name}: получено {len(result)} статей")
                articles.extend(result)

        # Deduplicate by URL
        seen_urls: set = set()
        unique = []
        for a in articles:
            url = a.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(a)

        logger.info(f"Итого уникальных статей: {len(unique)}")
        return unique


news_service = NewsService()
