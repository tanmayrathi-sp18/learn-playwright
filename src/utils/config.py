"""
src/utils/config.py

Centralized configuration for the scraper.
Using a config file instead of hardcoding strings throughout the app
makes it much easier to update selectors if the website changes.
"""

# The target website
BASE_URL = "https://books.toscrape.com/"

# Timeout settings (in milliseconds)
DEFAULT_TIMEOUT = 30000

# Selectors for the Listing Page
LISTING_SELECTORS = {
    "product_pod": "article.product_pod",
    "title_link": "h3 a",
    "price": ".price_color",
    "rating": "p.star-rating",
    "availability": ".availability",
    "next_button": "li.next a",
}

# Selectors for the Detail Page
DETAIL_SELECTORS = {
    "description": "#product_description + p",
    "upc": "table.table-striped tr:nth-child(1) td",
    "product_type": "table.table-striped tr:nth-child(2) td",
    "price_excl_tax": "table.table-striped tr:nth-child(3) td",
    "price_incl_tax": "table.table-striped tr:nth-child(4) td",
    "tax": "table.table-striped tr:nth-child(5) td",
    "availability_stock": "table.table-striped tr:nth-child(6) td",
    "num_reviews": "table.table-striped tr:nth-child(7) td",
}
