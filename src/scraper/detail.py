"""
src/scraper/detail.py

Module to extract deep data from a single book's detail page.
Separating this allows us to reuse this extraction logic
even if we find a book URL directly, without a listing page.
"""

from playwright.async_api import Page
from src.utils.config import DETAIL_SELECTORS


async def extract_book_details(page: Page) -> dict:
    """
    Parses a single book detail page and returns specific product data.
    Uses robust extraction methods to handle potential missing elements.
    """

    # Helper to safely get text from a selector
    async def get_text(selector: str, default: str = "N/A") -> str:
        try:
            # wait_for_selector ensures the element is there before we grab the text
            # timeout is small because we expect the page to be loaded already
            element = await page.wait_for_selector(selector, timeout=2000)
            if element:
                return (await element.inner_text()).strip()
            return default
        except Exception:
            return default

    # Extracting each field using our helper
    return {
        "description": await get_text(DETAIL_SELECTORS["description"]),
        "upc": await get_text(DETAIL_SELECTORS["upc"]),
        "product_type": await get_text(DETAIL_SELECTORS["product_type"]),
        "price_excl_tax": await get_text(DETAIL_SELECTORS["price_excl_tax"]),
        "price_incl_tax": await get_text(DETAIL_SELECTORS["price_incl_tax"]),
        "tax": await get_text(DETAIL_SELECTORS["tax"]),
        "availability_stock": await get_text(DETAIL_SELECTORS["availability_stock"]),
        "num_reviews": await get_text(DETAIL_SELECTORS["num_reviews"], default="0"),
    }
