"""
src/browser.py

Encapsulates all logic related to managing the browser lifecycle.
Separate initialization makes it easier to change browser types
or intercept logic without affecting the scrapers.
"""

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Route,
    Request,
)


async def block_resources(route: Route, request: Request):
    """
    A network interceptor handler to block expensive resources.
    """
    # Block heavy resources you don't need (images, fonts, stylesheets, media)
    # This results in huge speed boosts and reduced bandwidth.
    if request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()


class BrowserManager:
    """
    Class to manage Playwright browser and context objects.
    Using a class allows us to store the browser and context state
    consistently during a session.
    """

    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.playwright = None

    async def start(self, headless: bool = True):
        """
        Starts the Playwright driver and launches a browser.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)

        # Creating a unique session context with a realistic user agent
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0"
        )

        # Global network routing to optimize speed
        await self.context.route("**/*", block_resources)

    async def get_new_page(self):
        """
        Helper method to create a new page in the current context.
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call .start() first.")
        return await self.context.new_page()

    async def close(self):
        """
        Cleans up and closes all Playwright resources.
        """
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
