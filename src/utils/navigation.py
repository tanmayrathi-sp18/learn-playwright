"""
src/utils/navigation.py

Specific logic for moving between listing pages and details.
Separating this keeps the main orchestrator cleaner.
"""

from playwright.async_api import Page, TimeoutError
from src.utils.config import LISTING_SELECTORS


async def get_next_page_url(page: Page) -> str:
    """
    Checks if a 'Next' button exists on the current page
    and returns the target URL if found.
    """
    try:
        next_button = await page.query_selector(LISTING_SELECTORS["next_button"])
        if next_button:
            # Get the path from the href attribute
            href = await next_button.get_attribute("href")
            # books.toscrape.com uses relative URLs like 'page-2.html'
            return href
        return None
    except TimeoutError:
        return None


async def navigate_back_safely(page: Page):
    """
    Triggers a backward navigation and waits for the listing
    to be visible again.
    """
    # Simply using page.go_back() can be faster and preserve
    # the scroll state in many modern SPAs.
    # For static sites like this, it mimics a real user clicking 'Back'.
    await page.go_back(wait_until="domcontentloaded")
    # Ensuring the listing pod is present before we continue scraping
    await page.wait_for_selector(LISTING_SELECTORS["product_pod"])
