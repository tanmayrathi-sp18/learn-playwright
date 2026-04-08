"""
advanced_async_scraper.py

This script demonstrates how to construct an advanced, asynchronous scraper using Playwright.
It targets `https://books.toscrape.com/`, demonstrating performance and complex features.

Concepts covered:
1. Asynchronous Playwright execution (`asyncio`).
2. Setting fake authentication/custom headers.
3. Network interception (e.g., blocking images or tracking pixels to save bandwidth).
4. Taking screenshots of the page or specific elements.
"""

import asyncio
import json
from playwright.async_api import async_playwright, Route, Request

TARGET_URL = "https://books.toscrape.com/"


async def handle_route(route: Route, request: Request):
    """
    Network Interception Handler.
    This function examines outgoing network requests and decides whether to
    allow them or abort them. This is very useful to block images, ads, or analytics
    to make our scraper blazing fast.
    """
    # Block image requests to save bandwidth and load times
    if request.resource_type == "image":
        # print(f"Blocking image: {request.url}")
        await route.abort()
    else:
        # Continue the request as normal
        await route.continue_()


async def scrape_books():
    """
    Main function to scrape books using Playwright asynchronously.
    """
    # 1. Start the async Playwright context manager.
    async with async_playwright() as p:
        print("Launching the browser...")
        browser = await p.chromium.launch(headless=True)

        # 2. Setup a browser context. A context allows setting custom headers,
        # user agents, timezone, cookies, etc.
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0",
            extra_http_headers={
                # Example: Passing a fake authorization token or custom header
                "Authorization": "Bearer my_super_secret_fake_token",
                "X-Custom-Header": "LearningPlaywright",
            },
        )

        # Open a new page within this custom context
        page = await context.new_page()

        # 3. Setup Network Interception
        # We tell the page to intercept ALL network routes ("**/*") using our handler
        await page.route("**/*", handle_route)

        print(f"Navigating to {TARGET_URL}...")
        await page.goto(
            TARGET_URL, wait_until="networkidle"
        )  # Wait until network traffic settles

        scraped_data = []

        # 4. Take a screenshot of the entire page
        print("Taking a screenshot of the homepage...")
        await page.screenshot(path="books_homepage.png", full_page=True)

        # 5. Extract Data
        # All books are contained in `article` tags with class `product_pod`
        book_elements = await page.query_selector_all("article.product_pod")
        print(f"Found {len(book_elements)} books on the page.")

        for index, block in enumerate(book_elements):
            # The title is inside an h3 tag, within an anchor tag's 'title' attribute
            # We can use evaluate to run javascript inside the browser to get the attribute
            title_node = await block.query_selector("h3 a")
            book_title = (
                await title_node.get_attribute("title") if title_node else "Unknown"
            )

            # The price is in a div class 'product_price' -> p class 'price_color'
            price_node = await block.query_selector(".product_price .price_color")
            book_price = await price_node.inner_text() if price_node else "Unknown"

            scraped_data.append(
                {"id": index + 1, "title": book_title, "price": book_price}
            )

            # Example: Take a screenshot of just the FIRST book element
            if index == 0:
                print("Taking a screenshot of the first book element...")
                await block.screenshot(path="first_book_element.png")

        # 6. Close the browser
        await browser.close()
        print("Browser closed.")

        return scraped_data


if __name__ == "__main__":
    print("Starting asynchronous scraping job...")
    # asyncio.run() executes the main async function
    data = asyncio.run(scrape_books())

    # Save the output to a JSON file
    output_filename = "books_output.json"
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Scraping completed! Data saved to '{output_filename}'.")
    print(
        "Check out 'books_homepage.png' and 'first_book_element.png' for the screenshots!"
    )
