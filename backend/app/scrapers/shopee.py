"""
Shopee Malaysia scraper using their unofficial search API.
Endpoint: https://shopee.com.my/api/v4/search/search_items
"""
import re
from app.scrapers.base import BaseScraper


class ShopeeScraper(BaseScraper):
    platform = "shopee"
    _BASE = "https://shopee.com.my"
    _SEARCH_API = f"{_BASE}/api/v4/search/search_items"
    _ITEM_URL = f"{_BASE}/api/v4/item/get"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                self._SEARCH_API,
                params={
                    "keyword": query,
                    "limit": min(limit, 50),
                    "newest": 0,
                    "order": "relevancy",
                    "page_type": "search",
                    "scenario": "PAGE_GLOBAL_SEARCH",
                    "version": 2,
                },
                headers={
                    "Referer": f"{self._BASE}/search?keyword={query}",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            data = resp.json()
            items = data.get("items", []) or []
            results = [self._parse(item) for item in items[:limit] if item.get("item_basic")]
            return [r for r in results if r.get("price")]
        except Exception:
            return []

    def _parse(self, item: dict) -> dict:
        basic = item.get("item_basic", {})

        # Shopee prices are in cents * 100000 (divide by 100000)
        raw_price = basic.get("price", 0)
        raw_original = basic.get("price_before_discount", 0)
        price = raw_price / 100000 if raw_price else None
        original = raw_original / 100000 if raw_original and raw_original != raw_price else None

        shopid = basic.get("shopid", "")
        itemid = basic.get("itemid", "")
        slug = re.sub(r"[^a-z0-9]+", "-", basic.get("name", "").lower())[:60]
        url = f"{self._BASE}/{slug}-i.{shopid}.{itemid}" if shopid and itemid else None

        images = basic.get("images", [])
        image_url = f"https://cf.shopee.com.my/file/{images[0]}" if images else None

        return {
            "platform": self.platform,
            "title": basic.get("name", "")[:300],
            "price": price,
            "original_price": original,
            "discount_pct": self._calc_discount(price, original),
            "currency": "MYR",
            "url": url,
            "image_url": image_url,
            "seller_name": basic.get("shop_name", "") or None,
            "rating": float(basic.get("item_rating", {}).get("rating_star", 0) or 0) or None,
            "review_count": basic.get("liked_count") or None,
            "in_stock": basic.get("stock", 1) > 0,
        }

    @staticmethod
    def _calc_discount(price: float | None, original: float | None) -> float | None:
        if price and original and original > price:
            return round((original - price) / original * 100, 1)
        return None
