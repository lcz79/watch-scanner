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
from scrapers import chrono24, ebay, subito, watchfinder
from utils.watch_filter import is_watch_listing
from utils.logger import get_logger

_logger = get_logger("agent.marketplace")


def _apply_watch_filter(listings: list[WatchListing]) -> list[WatchListing]:
    """
    Applica is_watch_listing su ogni listing aggregato.
    Usa title/description come testo e il prezzo già parsato.
    """
    filtered = []
    for listing in listings:
        text = listing.description or listing.seller or ""
        if is_watch_listing(text, "", listing.price):
            filtered.append(listing)
        else:
            _logger.debug(
                f"Filter: rimosso '{text[:60]}' "
                f"(source={listing.source}, price={listing.price})"
            )
    removed = len(listings) - len(filtered)
    if removed:
        _logger.info(f"Filter: rimossi {removed}/{len(listings)} listing non-orologio")
    return filtered


class MarketplaceAgent(BaseAgent):
    """
    Monitora Chrono24, eBay, Subito.it, Watchfinder.
    In mock mode: dati simulati con URL strutturati realisticamente.
    In real mode: Playwright scraping con listing individuali e link diretti.
    Applica is_watch_listing su TUTTI i risultati aggregati prima di restituirli.
    """

    def __init__(self):
        super().__init__("marketplace_agent")

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        await asyncio.sleep(0.1)
        listings: list[WatchListing] = []
        listings.extend(mock_chrono24_listings(query.reference))
        listings.extend(mock_ebay_listings(query.reference))
        listings.extend(mock_watchbox_listings(query.reference))
        listings.extend(mock_watchfinder_listings(query.reference))
        return _apply_watch_filter(listings)

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        """
        Lancia browser Playwright condiviso e scrapa in parallelo
        Chrono24, eBay, Subito.it e Watchfinder.
        Ogni risultato è un annuncio individuale con link diretto,
        prezzo reale e venditore.
        Il filtro is_watch_listing viene applicato dopo l'aggregazione.
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
                watchfinder.scrape(query.reference, context),
                return_exceptions=True,
            )

            await browser.close()

        listings: list[WatchListing] = []
        scraper_names = ["chrono24", "ebay", "subito", "watchfinder"]
        for name, r in zip(scraper_names, results):
            if isinstance(r, Exception):
                self.logger.error(f"Scraper '{name}' failed: {r}")
            else:
                self.logger.info(f"Scraper '{name}': {len(r)} listing")
                listings.extend(r)

        # Filtro finale aggregato su tutti i sorgenti
        return _apply_watch_filter(listings)
