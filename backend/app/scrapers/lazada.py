"""
Lazada Malaysia scraper using their unofficial catalog search API.
Endpoint: https://www.lazada.com.my/catalog/api/search
"""
import logging
import re
from app.scrapers.base import BaseScraper

log = logging.getLogger(__name__)


class LazadaScraper(BaseScraper):
    platform = "lazada"
    _BASE = "https://www.lazada.com.my"
    _SEARCH_API = f"{_BASE}/catalog/api/search"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                self._SEARCH_API,
                params={"q": query, "page": 1, "limit": min(limit, 40)},
                headers={
                    "Referer": f"{self._BASE}/catalog/?q={query}",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            data = resp.json()
            items = data.get("mods", {}).get("listItems", [])
            results = [self._parse(item) for item in items[:limit] if item.get("price")]
            log.info("[lazada] API returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.warning("[lazada] API failed for '%s': %s — trying HTML fallback", query, exc)
            return await self._scrape_html(query, limit)

    def _parse(self, item: dict) -> dict:
        price_raw = item.get("price", "0")
        price = self._clean_price(str(price_raw))
        original_raw = item.get("originalPrice", "")
        original = self._clean_price(str(original_raw)) if original_raw else None

        return {
            "platform": self.platform,
            "title": item.get("name", "")[:300],
            "price": price,
            "original_price": original,
            "discount_pct": self._calc_discount(price, original),
            "currency": "MYR",
            "url": f"{self._BASE}{item.get('productUrl', '')}",
            "image_url": item.get("image", ""),
            "seller_name": item.get("sellerName", ""),
            "rating": float(item.get("ratingScore", 0) or 0) or None,
            "review_count": int(item.get("review", 0) or 0) or None,
            "in_stock": True,
        }

    async def _scrape_html(self, query: str, limit: int) -> list[dict]:
        """Fallback: parse Lazada search results page HTML."""
        try:
            resp = await self._get(
                f"{self._BASE}/catalog/",
                params={"q": query},
                headers={"Accept": "text/html"},
            )
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select("[data-qa-locator='product-item']")[:limit]:
                title_el = card.select_one("[class*='RfADt']")
                price_el = card.select_one("[class*='aBrP0']")
                url_el = card.select_one("a[href]")
                img_el = card.select_one("img")
                if not (title_el and price_el):
                    continue
                price = self._clean_price(price_el.get_text())
                if not price:
                    continue
                results.append({
                    "platform": self.platform,
                    "title": title_el.get_text(strip=True)[:300],
                    "price": price,
                    "original_price": None,
                    "discount_pct": None,
                    "currency": "MYR",
                    "url": url_el["href"] if url_el else None,
                    "image_url": img_el.get("src") if img_el else None,
                    "seller_name": None,
                    "rating": None,
                    "review_count": None,
                    "in_stock": True,
                })
            log.info("[lazada] HTML fallback returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[lazada] HTML fallback also failed for '%s': %s", query, exc)
            return []

    @staticmethod
    def _clean_price(raw: str) -> float | None:
        cleaned = re.sub(r"[^\d.]", "", raw.replace(",", ""))
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    @staticmethod
    def _calc_discount(price: float | None, original: float | None) -> float | None:
        if price and original and original > price:
            return round((original - price) / original * 100, 1)
        return None
