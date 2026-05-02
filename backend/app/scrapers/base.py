"""Base scraper with shared HTTP client, retry logic, rate limiting, and ScraperAPI proxy support."""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import quote

import httpx
from app.config import get_settings

settings = get_settings()
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-MY,en;q=0.9,ms;q=0.8",
    "Accept": "application/json, text/html, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class BaseScraper(ABC):
    platform: str = "unknown"

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=settings.scrape_timeout_secs,
                follow_redirects=True,
            )
        return self._client

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        client = await self._get_client()
        delay_secs = settings.scrape_request_delay_ms / 1000
        await asyncio.sleep(delay_secs + random.uniform(0, 0.5))

        # Merge any params into the URL string so we can optionally wrap it
        params = kwargs.pop("params", None)
        final_url = str(httpx.URL(url).copy_merge_params(params or {}))

        # Route through ScraperAPI when a key is configured.
        # ScraperAPI makes the request from a rotating residential IP, bypassing
        # bot-detection on Lazada, Shopee, and grocery sites.
        using_proxy = bool(settings.scraperapi_key)
        if using_proxy:
            proxy_url = (
                f"http://api.scraperapi.com"
                f"?api_key={settings.scraperapi_key}"
                f"&url={quote(final_url, safe='')}"
            )
            log.debug("[%s] Routing via ScraperAPI: %s", self.platform, final_url)
            # Drop custom headers — ScraperAPI provides its own realistic headers
            kwargs.pop("headers", None)
            request_url = proxy_url
        else:
            request_url = final_url

        for attempt in range(settings.scrape_max_retries):
            try:
                resp = await client.get(request_url, **kwargs)
                log.info("[%s] GET %s → %s", self.platform, url, resp.status_code)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                log.warning(
                    "[%s] HTTP %s on %s (attempt %d/%d)",
                    self.platform, status, url, attempt + 1, settings.scrape_max_retries,
                )
                if status in (403, 429):
                    if not using_proxy:
                        log.warning(
                            "[%s] Blocked by bot-detection — set SCRAPERAPI_KEY env var to bypass",
                            self.platform,
                        )
                    raise
                if attempt == settings.scrape_max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except httpx.RequestError as exc:
                log.warning(
                    "[%s] Request error on %s: %s (attempt %d/%d)",
                    self.platform, url, exc, attempt + 1, settings.scrape_max_retries,
                )
                if attempt == settings.scrape_max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Failed to GET {url}")

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[dict]:
        ...

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
