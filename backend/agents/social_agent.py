import asyncio
from agents.base_agent import BaseAgent
from models.schemas import WatchQuery, WatchListing
from mock.mock_data import mock_instagram_listings, mock_tiktok_listings


async def _run_instagram_full(reference: str, username: str, password: str):
    """Login + ricerca post. get_client è sincrono → run_in_executor per non bloccare il loop."""
    from scrapers.instagram import scrape, get_client

    loop = asyncio.get_event_loop()
    # get_client è sincrono: lo eseguiamo in executor per permettere la cancellazione via wait_for
    cl = await loop.run_in_executor(None, get_client, username, password)
    if not cl:
        return cl, []

    posts = await scrape(reference, username, password)
    return cl, posts if isinstance(posts, list) else []


class SocialAgent(BaseAgent):
    """
    Monitora post e stories dei reseller su Instagram.
    Ogni risultato è un annuncio individuale con prezzo estratto dalla caption.

    Setup richiesto:
      Nel file backend/.env:
        INSTAGRAM_USERNAME=tuo_username
        INSTAGRAM_PASSWORD=tua_password

    Il primo login salva la sessione in instagram_session.json (~90 giorni).
    """

    def __init__(self):
        super().__init__("social_agent")

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        await asyncio.sleep(0.2)
        listings = []
        listings.extend(mock_instagram_listings(query.reference))
        listings.extend(mock_tiktok_listings(query.reference))
        return listings

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        # Playwright stories: sempre disponibili dal DB locale, indipendente da Instagram
        from scrapers.stories.pipeline import get_stories_listings
        playwright_stories = await get_stories_listings(query.reference)
        if playwright_stories:
            self.logger.info(f"Playwright stories: {len(playwright_stories)} risultati per {query.reference}")

        if not self.settings.instagram_username or not self.settings.instagram_password:
            self.logger.warning("INSTAGRAM_USERNAME/PASSWORD non configurati — solo Playwright stories")
            return playwright_stories

        from scrapers.instagram_stories import get_cached_stories
        cached_stories = get_cached_stories(query.reference)

        # Tenta Instagram (instagrapi) — se fallisce per qualsiasi motivo, restituiamo
        # comunque le Playwright stories già recuperate sopra
        try:
            cl, listings = await asyncio.wait_for(
                _run_instagram_full(
                    query.reference,
                    self.settings.instagram_username,
                    self.settings.instagram_password,
                ),
                timeout=30.0,
            )
            return listings + cached_stories + playwright_stories
        except Exception as e:
            self.logger.warning(f"Instagram fallito ({type(e).__name__}) — uso solo Playwright stories")
            return cached_stories + playwright_stories
