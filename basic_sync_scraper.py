"""
basic_sync_scraper.py

This script demonstrates how to construct a simple, synchronous scraper using Playwright.
It navigates to `https://quotes.toscrape.com/`, extracts quotes and their authors,
and saves the data to a JSON file.

Concepts covered:
1. Starting a synchronous browser instance (Chromium).
2. Navigating to a URL.
3. Using CSS selectors to identify elements securely.
4. Extracting text content.
"""

import json
from playwright.sync_api import sync_playwright

# The URL we want to scrape
TARGET_URL = "https://quotes.toscrape.com/"


def scrape_quotes():
    """
    Main function to scrape quotes using Playwright synchronously.
    """
    # 1. Start the Playwright context manager.
    with sync_playwright() as p:
        # 2. Launching Chromium.
        # headless=True means the browser will NOT show a visible window.
        # Set headless=False if you want to watch the browser work!
        print("Launching the browser...")
        browser = p.chromium.launch(headless=True)

        # 3. Create a new "page" (like opening a new tab)
        page = browser.new_page()

        # 4. Navigate to the website. wait_until="domcontentloaded" ensures we
        #    don't wait unnecessarily long for things like images to load if
        #    we only need HTML text.
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until="domcontentloaded")

        scraped_data = []

        # 5. Extract data.
        # Playwright allows us to find all elements matching a CSS selector using `query_selector_all`.
        # On `quotes.toscrape.com`, each quote block is a `div` with the class `quote`.
        quote_elements = page.query_selector_all(".quote")
        print(f"Found {len(quote_elements)} quotes on the page.")

        # Loop through each element and extract specific parts.
        for index, block in enumerate(quote_elements):
            # Find the text span with class 'text'
            text_el = block.query_selector(".text")
            # Find the author small tag with class 'author'
            author_el = block.query_selector(".author")

            if text_el and author_el:
                # Get the internal text content
                quote_text = text_el.inner_text()
                author_name = author_el.inner_text()

                scraped_data.append(
                    {"id": index + 1, "quote": quote_text, "author": author_name}
                )

        # 6. Close the browser to free up resources.
        browser.close()
        print("Browser closed.")

        return scraped_data


if __name__ == "__main__":
    print("Starting synchronous scraping job...")
    data = scrape_quotes()

    # Save the output to a JSON file
    output_filename = "quotes_output.json"
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Scraping completed! Data saved to '{output_filename}'.")
