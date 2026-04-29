"""
Agente che scrapa dealer reseller via API pubbliche Shopify e WooCommerce.
Nessun Playwright — usa solo httpx contro /products.json e /wp-json/wc/store/products.
"""
import asyncio
from agents.base_agent import BaseAgent
from models.schemas import WatchQuery, WatchListing
from utils.logger import get_logger

logger = get_logger("agent.reseller_website")


class ResellerWebsiteAgent(BaseAgent):
    def __init__(self):
        super().__init__("reseller_website_agent")

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        from scrapers.dealer_scraper import discover_and_scrape_dealers
        try:
            listings = await asyncio.wait_for(
                discover_and_scrape_dealers(query.reference),
                timeout=45.0,
            )
            self.logger.info(f"Dealer API: {len(listings)} risultati per {query.reference}")
            return listings
        except asyncio.TimeoutError:
            self.logger.warning("Dealer API timeout (45s)")
            return []
        except Exception as e:
            self.logger.error(f"Dealer API error: {e}")
            return []

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        return []
