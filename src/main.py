"""
src/main.py

The main orchestrator of the project.
It defines the business logic:
Where to start, how many pages to crawl, and where to save results.
"""

import asyncio
import json
import os
from urllib.parse import urljoin
from browser import BrowserManager
from scraper.listing import extract_listing_items
from scraper.detail import extract_book_details
from utils.navigation import get_next_page_url, navigate_back_safely
from utils.config import BASE_URL
from models.item import BookItem


async def run_scraper(target_book_count: int = 100):
    """
    Orchestrates the scraping flow:
    1. Start Browser
    2. Loop through listing pages until target count is reached
    3. For each listing, loop through book items
    4. Visit each book detail, extract, and update results
    5. Save the aggregated results.
    """
    browser_manager = BrowserManager()
    await browser_manager.start(headless=True)

    # We use a single page object for the entire session
    page = await browser_manager.get_new_page()

    all_books = []
    current_page_url = BASE_URL
    pages_scraped = 0

    print(f"Starting crawl at {BASE_URL}")

    try:
        while current_page_url and len(all_books) < target_book_count:
            print(f"\n--- Scraping Page {pages_scraped + 1} ---")
            await page.goto(current_page_url, wait_until="networkidle")

            # 1. DISCOVERY PASS: Extract all basic data from the listing page in one go
            listing_items = await extract_listing_items(page)
            print(f"Found {len(listing_items)} books on the listing page.")

            # 2. ENUMERATION PASS: Visit each detail link we just collected
            for book_raw in listing_items:
                if len(all_books) >= target_book_count:
                    break

                detail_url = book_raw["url"]
                print(
                    f"  [{len(all_books) + 1}/{target_book_count}] Visiting: {book_raw['title'][:30]}..."
                )

                # Navigate directly to the detail page
                await page.goto(detail_url, wait_until="domcontentloaded")

                # Extract deeper data
                detail_data = await extract_book_details(page)

                # Combine and validate with Pydantic
                combined_record = {**book_raw, **detail_data}
                validated_book = BookItem(**combined_record)
                all_books.append(validated_book.model_dump(mode="json"))

            # 3. PAGINATION: We return to the listing page to find the 'Next' button
            await page.goto(current_page_url, wait_until="domcontentloaded")
            next_relative_url = await get_next_page_url(page)

            if next_relative_url:
                current_page_url = urljoin(page.url, next_relative_url)
                pages_scraped += 1
            else:
                current_page_url = None

    finally:
        # Securely close the browser context
        print("\nCrawl complete. Closing browser...")
        await browser_manager.close()

    # 7. Output Result as JSON
    os.makedirs("output", exist_ok=True)
    output_path = "output/books_full_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=4)

    print(f"Successfully scraped {len(all_books)} books!")
    print(f"Data saved to: {output_path}")


if __name__ == "__main__":
    # Scrape until we have 100 books!
    asyncio.run(run_scraper(target_book_count=100))
