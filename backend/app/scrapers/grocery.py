"""
Malaysian grocery store scrapers.
Targets: AEON Online, Jaya Grocer, 99 Speedmart, Giant, Lotus's.
Uses BeautifulSoup HTML scraping.
"""
import logging
import re
from typing import Optional
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

log = logging.getLogger(__name__)


class AeonScraper(BaseScraper):
    platform = "aeon"
    _BASE = "https://www.aeon.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/en/product-listing/",
                params={"q": query, "pageSize": limit},
                headers={"Accept": "text/html"},
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select(".product-item, .product-tile")[:limit]:
                title = _text(card, ".product-name, h3, .name")
                price = _price(card, ".price-box .price, .product-price, [class*='price']")
                url = _href(card, "a", self._BASE)
                img = _src(card, "img")
                if title and price:
                    results.append(_make_result(self.platform, title, price, None, url, img))
            log.info("[aeon] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[aeon] Search failed for '%s': %s", query, exc)
            return []


class JayaGrocerScraper(BaseScraper):
    platform = "jaya_grocer"
    _BASE = "https://www.jayagrocer.com"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/search",
                params={"q": query},
                headers={"Accept": "text/html"},
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select(".product-card, .product-item, [class*='product']")[:limit]:
                title = _text(card, ".product-title, .title, h3, h4")
                price = _price(card, ".price, .product-price, [class*='price']")
                url = _href(card, "a", self._BASE)
                img = _src(card, "img")
                if title and price:
                    results.append(_make_result(self.platform, title, price, None, url, img))
            log.info("[jaya_grocer] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[jaya_grocer] Search failed for '%s': %s", query, exc)
            return []


class SpeedmartScraper(BaseScraper):
    platform = "99speedmart"
    _BASE = "https://www.99speedmart.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/search",
                params={"keyword": query},
                headers={"Accept": "text/html"},
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select(".product-item, .product, [class*='product-card']")[:limit]:
                title = _text(card, "h2, h3, .product-name, .name")
                price = _price(card, ".price, .product-price, [class*='price']")
                url = _href(card, "a", self._BASE)
                img = _src(card, "img")
                if title and price:
                    results.append(_make_result(self.platform, title, price, None, url, img))
            log.info("[99speedmart] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[99speedmart] Search failed for '%s': %s", query, exc)
            return []


class GiantScraper(BaseScraper):
    platform = "giant"
    _BASE = "https://www.giant.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/search/",
                params={"q": query},
                headers={"Accept": "text/html"},
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select(".product-item, .product-listing-card")[:limit]:
                title = _text(card, ".product-name, h3")
                price_el = card.select_one(".price-box .price, .special-price .price, .regular-price .price")
                price = _price_from_el(price_el)
                orig_el = card.select_one(".old-price .price")
                original = _price_from_el(orig_el)
                url = _href(card, "a", self._BASE)
                img = _src(card, "img")
                if title and price:
                    results.append(_make_result(self.platform, title, price, original, url, img))
            log.info("[giant] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[giant] Search failed for '%s': %s", query, exc)
            return []


class LotusScraper(BaseScraper):
    platform = "lotus"
    _BASE = "https://www.lotuss.com.my"

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            resp = await self._get(
                f"{self._BASE}/en/search/",
                params={"text": query},
                headers={"Accept": "text/html"},
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for card in soup.select(".product-item, .yCmsComponent.product")[:limit]:
                title = _text(card, ".product-name, h3, h2")
                price = _price(card, ".value, .price-value, [itemprop='price']")
                url = _href(card, "a", self._BASE)
                img = _src(card, "img")
                if title and price:
                    results.append(_make_result(self.platform, title, price, None, url, img))
            log.info("[lotus] Returned %d items for '%s'", len(results), query)
            return results
        except Exception as exc:
            log.error("[lotus] Search failed for '%s': %s", query, exc)
            return []


# --- helpers ---

def _text(soup, selector: str) -> Optional[str]:
    for sel in selector.split(","):
        el = soup.select_one(sel.strip())
        if el:
            return el.get_text(strip=True)[:300]
    return None


def _price(soup, selector: str) -> Optional[float]:
    for sel in selector.split(","):
        el = soup.select_one(sel.strip())
        if el:
            v = _price_from_el(el)
            if v:
                return v
    return None


def _price_from_el(el) -> Optional[float]:
    if not el:
        return None
    raw = el.get_text(strip=True) or el.get("content", "")
    cleaned = re.sub(r"[^\d.]", "", raw.replace(",", ""))
    try:
        v = float(cleaned)
        return v if v > 0 else None
    except ValueError:
        return None


def _href(soup, selector: str, base: str) -> Optional[str]:
    el = soup.select_one(selector)
    if not el:
        return None
    href = el.get("href", "")
    if href.startswith("http"):
        return href
    return f"{base}{href}" if href else None


def _src(soup, selector: str) -> Optional[str]:
    el = soup.select_one(selector)
    if not el:
        return None
    return el.get("src") or el.get("data-src") or el.get("data-lazy-src")


def _make_result(
    platform: str,
    title: str,
    price: float,
    original: Optional[float],
    url: Optional[str],
    img: Optional[str],
) -> dict:
    discount = None
    if original and original > price:
        discount = round((original - price) / original * 100, 1)
    return {
        "platform": platform,
        "title": title,
        "price": price,
        "original_price": original,
        "discount_pct": discount,
        "currency": "MYR",
        "url": url,
        "image_url": img,
        "seller_name": None,
        "rating": None,
        "review_count": None,
        "in_stock": True,
    }
