"""
Shopee Malaysia scraper.

Strategy:
1. Hit the Shopee search HTML page with JS rendering (render=True via ScraperAPI).
   Shopee's internal API (/api/v4/search/search_items) requires live session
   cookies so it always 403s from server-side scrapers — even with a proxy.
2. Try to extract product JSON from window.__SC_HYDRATED_DATA__ or
   __NEXT_DATA__ script tags first (fast, 1 credit).
3. Fall back to DOM parsing of the rendered page if no embedded JSON is found.
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

log = logging.getLogger(__name__)


class ShopeeScraper(BaseScraper):
    platform = "shopee"
    _BASE = "https://shopee.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        # First try: non-rendered HTML (faster, 1 credit) — works if page has embedded JSON
        try:
            resp = await self._get(
                f"{self._BASE}/search",
                params={"keyword": query},
                render=False,
            )
            results = self._parse_html(resp.text, query, limit)
            if results:
                log.info("[shopee] Non-rendered HTML returned %d items for '%s'", len(results), query)
                return results
        except Exception as exc:
            log.debug("[shopee] Non-rendered attempt failed for '%s': %s", query, exc)

        # Second try: JS-rendered HTML (5 credits) — needed when content is dynamic
        try:
            resp = await self._get(
                f"{self._BASE}/search",
                params={"keyword": query},
                render=True,
            )
            results = self._parse_html(resp.text, query, limit)
            log.info("[shopee] Rendered HTML returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[shopee] Search failed for '%s': %s", query, exc)
            return []

    def _parse_html(self, html: str, query: str, limit: int) -> list[dict]:
        """Try all extraction strategies against the page HTML."""
        soup = BeautifulSoup(html, "lxml")

        # Strategy 1: Look for embedded JSON blobs that contain price data
        for script in soup.find_all("script"):
            text = script.string or ""
            # Skip very short or obviously irrelevant scripts
            if len(text) < 100 or "price" not in text.lower():
                continue
            for var in ["__SC_HYDRATED_DATA__", "pageData", "__INITIAL_STATE__", "initData"]:
                if var not in text:
                    continue
                try:
                    match = re.search(rf'{re.escape(var)}\s*[=:]\s*(\{{)', text)
                    if not match:
                        continue
                    start = match.start(1)
                    blob = self._balanced_json(text[start:])
                    data = json.loads(blob)
                    results = self._extract_from_json(data, limit)
                    if results:
                        log.debug("[shopee] Extracted %d items via %s", len(results), var)
                        return results
                except Exception as e:
                    log.debug("[shopee] JSON extract via %s failed: %s", var, e)

        # Strategy 2: parse rendered DOM product cards
        return self._parse_dom(soup, limit)

    def _extract_from_json(self, data: dict, limit: int) -> list[dict]:
        """Recursively search for items arrays in an arbitrary JSON structure."""
        results = []
        self._find_items(data, results)
        return results[:limit]

    def _find_items(self, obj, results: list, depth: int = 0):
        """Depth-first search for objects that look like Shopee product listings."""
        if depth > 8 or len(results) >= 30:
            return
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and ("item_basic" in item or ("price" in item and "name" in item)):
                    parsed = self._parse_item(item)
                    if parsed.get("price"):
                        results.append(parsed)
                elif isinstance(item, (dict, list)):
                    self._find_items(item, results, depth + 1)
        elif isinstance(obj, dict):
            for v in obj.values():
                self._find_items(v, results, depth + 1)

    def _parse_item(self, item: dict) -> dict:
        """Parse a single product item from Shopee JSON."""
        basic = item.get("item_basic") or item

        raw_price = basic.get("price", 0) or 0
        raw_original = basic.get("price_before_discount", 0) or 0

        # Shopee API prices are in units * 100000
        if isinstance(raw_price, (int, float)) and raw_price > 10000:
            price = raw_price / 100000
            original = raw_original / 100000 if raw_original and raw_original != raw_price else None
        else:
            price = float(raw_price) if raw_price else None
            original = float(raw_original) if raw_original and raw_original != raw_price else None

        shopid = basic.get("shopid", "")
        itemid = basic.get("itemid", "")
        name = basic.get("name", "") or item.get("name", "")
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower())[:60]
        url = f"{self._BASE}/{slug}-i.{shopid}.{itemid}" if shopid and itemid else None

        images = basic.get("images", [])
        image_url = f"https://cf.shopee.com.my/file/{images[0]}" if images else None

        return {
            "platform": self.platform,
            "title": name[:300],
            "price": price,
            "original_price": original,
            "discount_pct": self._calc_discount(price, original),
            "currency": "MYR",
            "url": url,
            "image_url": image_url,
            "seller_name": basic.get("shop_name") or None,
            "rating": float((basic.get("item_rating") or {}).get("rating_star", 0) or 0) or None,
            "review_count": basic.get("liked_count") or None,
            "in_stock": (basic.get("stock", 1) or 1) > 0,
        }

    def _parse_dom(self, soup: BeautifulSoup, limit: int) -> list[dict]:
        """Parse rendered Shopee product cards from the DOM."""
        results = []

        # Shopee renders items as <li> elements inside the search grid
        # Try multiple selector patterns since class names change
        containers = (
            soup.select("li[class*='col-xs-2-4']") or
            soup.select("[data-sqe='item']") or
            soup.select("div[class*='shopee-search-item-result__item']") or
            soup.select("div[class*='item-card']") or
            []
        )

        for card in containers[:limit]:
            try:
                # Title: any <a> or named div
                title_el = (
                    card.select_one("[data-sqe='name']") or
                    card.select_one("div[class*='ellipsis']") or
                    card.select_one("a")
                )
                title = title_el.get_text(strip=True)[:300] if title_el else None
                if not title:
                    continue

                # Price: look for "RM" followed by digits, or a price-classed element
                text = card.get_text(" ")
                price_match = re.search(r"RM\s*([\d,]+\.?\d*)", text)
                if not price_match:
                    continue
                price_str = price_match.group(1).replace(",", "")
                price = float(price_str) if price_str else None
                if not price:
                    continue

                # URL
                link = card.select_one("a[href]")
                href = link["href"] if link else None
                url = href if href and href.startswith("http") else (f"{self._BASE}{href}" if href else None)

                # Image
                img = card.select_one("img")
                image_url = img.get("src") or img.get("data-src") if img else None

                results.append({
                    "platform": self.platform,
                    "title": title,
                    "price": price,
                    "original_price": None,
                    "discount_pct": None,
                    "currency": "MYR",
                    "url": url,
                    "image_url": image_url,
                    "seller_name": None,
                    "rating": None,
                    "review_count": None,
                    "in_stock": True,
                })
            except Exception:
                continue

        return results

    @staticmethod
    def _balanced_json(text: str) -> str:
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
    def _calc_discount(price: float | None, original: float | None) -> float | None:
        if price and original and original > price:
            return round((original - price) / original * 100, 1)
        return None
