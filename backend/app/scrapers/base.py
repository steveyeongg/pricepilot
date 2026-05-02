"""Base scraper with shared HTTP client, retry logic, and rate limiting."""
import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from app.config import get_settings

settings = get_settings()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-MY,en;q=0.9,ms;q=0.8",
    "Accept": "application/json, text/html, */*",
}


class BaseScraper(ABC):
    platform: str = "unknown"

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            proxies = settings.proxies
            proxy = random.choice(proxies) if proxies else None
            self._client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=settings.scrape_timeout_secs,
                follow_redirects=True,
                proxies={"all://": proxy} if proxy else None,
            )
        return self._client

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        client = await self._get_client()
        delay_secs = settings.scrape_request_delay_ms / 1000
        await asyncio.sleep(delay_secs + random.uniform(0, 0.5))

        for attempt in range(settings.scrape_max_retries):
            try:
                resp = await client.get(url, **kwargs)
                resp.raise_for_status()
                return resp
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                if attempt == settings.scrape_max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Failed to GET {url} after {settings.scrape_max_retries} retries")

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[dict]:
        """Return list of price result dicts with keys: title, price, url, platform, etc."""
        ...

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
