"""
src/scraper/listing.py

Extracts books data from the listing gallery.
Separating this from the detail scraping keeps things
easy to modify if the layout of the listing gallery changes.
"""

from urllib.parse import urljoin
from typing import List
from playwright.async_api import Page
from utils.config import LISTING_SELECTORS


async def extract_listing_items(page: Page) -> List[dict]:
    """
    Parses all products available on the current listing page.
    Returns a list of dictionaries with raw extracted data.
    """
    items = []

    # Locate all product containers
    product_nodes = await page.query_selector_all(LISTING_SELECTORS["product_pod"])

    for node in product_nodes:
        # Extract title and detail link from the title anchor
        title_node = await node.query_selector(LISTING_SELECTORS["title_link"])
        title = await title_node.get_attribute("title") if title_node else "N/A"
        href = await title_node.get_attribute("href") if title_node else ""

        # PRODUCTION TIP: Use urljoin to handle relative paths correctly.
        # This resolves links like 'item.html' into 'https://site.com/catalogue/item.html'
        # based on the current page URL, preventing 404s on subpages.
        absolute_url = urljoin(page.url, href)

        # Extract price, rating, and availability
        price_node = await node.query_selector(LISTING_SELECTORS["price"])
        price = await price_node.inner_text() if price_node else "N/A"

        rating_node = await node.query_selector(LISTING_SELECTORS["rating"])
        # Rating is stored in a class like "star-rating Three"
        rating_class = await rating_node.get_attribute("class") if rating_node else ""
        rating_val = rating_class.replace("star-rating ", "") if rating_class else "N/A"

        availability_node = await node.query_selector(LISTING_SELECTORS["availability"])
        availability = (
            await availability_node.inner_text() if availability_node else "N/A"
        )

        items.append(
            {
                "title": title,
                "price": price,
                "rating": rating_val,
                "availability": availability.strip(),
                "url": absolute_url,
            }
        )

    return items
