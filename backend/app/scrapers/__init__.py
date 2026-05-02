import asyncio
from typing import Optional
from app.scrapers.lazada import LazadaScraper
from app.scrapers.shopee import ShopeeScraper
from app.scrapers.grocery import AeonScraper, JayaGrocerScraper, LotusScraper

# 99 Speedmart does not have a searchable online store (consistently 404).
SCRAPERS = {
    "lazada": LazadaScraper,
    "shopee": ShopeeScraper,
    "aeon": AeonScraper,
    "jaya_grocer": JayaGrocerScraper,
    "lotus": LotusScraper,
}

ALL_PLATFORMS = list(SCRAPERS.keys())
ECOMMERCE_PLATFORMS = ["lazada", "shopee"]
GROCERY_PLATFORMS = ["aeon", "jaya_grocer", "lotus"]


async def search_all(
    query: str,
    platforms: Optional[list[str]] = None,
    limit_per_platform: int = 10,
) -> list[dict]:
    """Run all scrapers concurrently and merge results."""
    targets = platforms or ALL_PLATFORMS
    tasks = []
    scraper_instances = []

    for name in targets:
        cls = SCRAPERS.get(name)
        if cls:
            s = cls()
            scraper_instances.append(s)
            tasks.append(s.search(query, limit=limit_per_platform))

    results_nested = await asyncio.gather(*tasks, return_exceptions=True)

    flat = []
    for r in results_nested:
        if isinstance(r, list):
            flat.extend(r)

    # Close clients
    await asyncio.gather(*[s.close() for s in scraper_instances], return_exceptions=True)

    return flat
