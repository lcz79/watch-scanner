import asyncio
from playwright.async_api import async_playwright

from agents.base_agent import BaseAgent
from models.schemas import WatchQuery, WatchListing
from mock.mock_data import (
    mock_chrono24_listings,
    mock_ebay_listings,
    mock_watchbox_listings,
    mock_watchfinder_listings,
)
from scrapers import chrono24, ebay, subito


class MarketplaceAgent(BaseAgent):
    """
    Monitora Chrono24, eBay, WatchBox, Watchfinder.
    In mock mode: dati simulati con URL strutturati realisticamente.
    In real mode: Playwright scraping con listing individuali e link diretti.
    """

    def __init__(self):
        super().__init__("marketplace_agent")

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        await asyncio.sleep(0.1)
        listings = []
        listings.extend(mock_chrono24_listings(query.reference))
        listings.extend(mock_ebay_listings(query.reference))
        listings.extend(mock_watchbox_listings(query.reference))
        listings.extend(mock_watchfinder_listings(query.reference))
        return listings

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        """
        Lancia browser Playwright condiviso e scrapa in parallelo
        Chrono24 + eBay. Ogni risultato è un annuncio individuale
        con link diretto, prezzo reale e venditore.
        """
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="it-IT",
                timezone_id="Europe/Rome",
            )

            results = await asyncio.gather(
                chrono24.scrape(query.reference, context),
                ebay.scrape(query.reference, context),
                subito.scrape(query.reference, context),
                return_exceptions=True,
            )

            await browser.close()

        listings = []
        for r in results:
            if isinstance(r, Exception):
                self.logger.error(f"Scraper failed: {r}")
            else:
                listings.extend(r)

        return listings
