"""
Lazada Malaysia scraper.

Strategy:
1. Hit the catalog search page (HTML).
2. Extract product JSON from the embedded <script id="__NEXT_DATA__"> tag.
3. Parse the listItems array from that data.
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

log = logging.getLogger(__name__)


class LazadaScraper(BaseScraper):
    platform = "lazada"
    _BASE = "https://www.lazada.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/catalog/",
                params={"q": query},
            )
            items = self._extract_items(resp.text)
            results = [self._parse(item) for item in items[:limit] if self._has_price(item)]
            results = [r for r in results if r.get("price")]
            log.info("[lazada] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[lazada] Search failed for '%s': %s", query, exc)
            return []

    def _extract_items(self, html: str) -> list[dict]:
        """Extract listItems from the page via multiple strategies."""
        soup = BeautifulSoup(html, "lxml")

        # Strategy 1: Next.js __NEXT_DATA__ JSON blob
        next_script = soup.find("script", {"id": "__NEXT_DATA__"})
        if next_script and next_script.string:
            try:
                data = json.loads(next_script.string)
                items = self._dig(data, "props", "pageProps", "initialData", "data", "mainInfo", "listItems")
                if items:
                    log.debug("[lazada] Extracted %d items via __NEXT_DATA__", len(items))
                    return items
                # alternate path
                items = self._dig(data, "props", "pageProps", "data", "mainInfo", "listItems")
                if items:
                    return items
            except Exception as e:
                log.debug("[lazada] __NEXT_DATA__ parse failed: %s", e)

        # Strategy 2: window.pageData or window.__pageData__ in any <script> tag
        for script in soup.find_all("script"):
            text = script.string or ""
            if "listItems" not in text:
                continue
            for pat in [
                r'window\.__pageData__\s*=\s*(\{)',
                r'window\.pageData\s*=\s*(\{)',
                r'"listItems"\s*:\s*\[',
            ]:
                if re.search(pat, text):
                    try:
                        # Find first '{' and parse to matching '}'
                        start = text.index("{")
                        data = json.loads(self._balanced_json(text[start:]))
                        items = self._dig(data, "mods", "listItems") or self._dig(data, "data", "mods", "listItems")
                        if items:
                            log.debug("[lazada] Extracted %d items via window.pageData", len(items))
                            return items
                    except Exception as e:
                        log.debug("[lazada] window.pageData parse failed: %s", e)
                    break

        log.debug("[lazada] No embedded JSON found; returning empty list")
        return []

    @staticmethod
    def _balanced_json(text: str) -> str:
        """Return the minimal balanced JSON object starting at position 0."""
        depth = 0
        in_str = False
        escape = False
        for i, ch in enumerate(text):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_str:
                escape = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[: i + 1]
        return text

    @staticmethod
    def _dig(obj: dict, *keys):
        """Safely navigate nested dicts."""
        for k in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(k)
        return obj

    def _has_price(self, item: dict) -> bool:
        return bool(item.get("price") or item.get("priceShow"))

    def _parse(self, item: dict) -> dict:
        price_raw = item.get("price") or item.get("priceShow") or "0"
        price = self._clean_price(str(price_raw))
        original_raw = item.get("originalPrice") or item.get("originalPriceShow") or ""
        original = self._clean_price(str(original_raw)) if original_raw else None

        product_url = item.get("productUrl") or item.get("itemUrl") or ""
        if product_url and not product_url.startswith("http"):
            product_url = f"{self._BASE}{product_url}"

        return {
            "platform": self.platform,
            "title": (item.get("name") or item.get("title") or "")[:300],
            "price": price,
            "original_price": original,
            "discount_pct": self._calc_discount(price, original),
            "currency": "MYR",
            "url": product_url or None,
            "image_url": item.get("image") or item.get("imgUrl") or None,
            "seller_name": item.get("sellerName") or item.get("shopName") or None,
            "rating": float(item.get("ratingScore") or item.get("rating") or 0) or None,
            "review_count": int(item.get("review") or item.get("reviews") or 0) or None,
            "in_stock": True,
        }

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
