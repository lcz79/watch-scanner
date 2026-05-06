import asyncio
from agents.base_agent import BaseAgent
from models.schemas import WatchQuery, WatchListing
from mock.mock_data import mock_instagram_listings, mock_tiktok_listings, mock_facebook_listings


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


async def _tiktok_scan(reference: str) -> list[WatchListing]:
    """Wrapper con timeout per TikTok scraper."""
    from scrapers.tiktok_scraper import scrape as tiktok_scrape
    return await asyncio.wait_for(tiktok_scrape(reference), timeout=30.0)


async def _facebook_scan(reference: str) -> list[WatchListing]:
    """Wrapper con timeout per Facebook Marketplace scraper."""
    from scrapers.facebook_marketplace import scrape as fb_scrape
    return await asyncio.wait_for(fb_scrape(reference), timeout=30.0)


async def _bio_links_scan(reference: str) -> list[WatchListing]:
    """
    Wrapper per il bio link extractor.
    Carica i reseller noti dal DB discovery (con bio) e scrapa i loro siti web.
    """
    from scrapers.bio_link_extractor import scrape_resellers_batch

    try:
        # Usa una query diretta al DB per ottenere anche la bio
        from agents.discovery.resellers_db import _connect, init_db
        init_db()
        conn = _connect()
        rows = conn.execute(
            "SELECT username, platform, bio, website, score "
            "FROM dealers WHERE score >= 3 AND bio IS NOT NULL AND bio != '' "
            "ORDER BY score DESC LIMIT 30"
        ).fetchall()
        conn.close()

        resellers = [dict(r) for r in rows]
        if not resellers:
            return []

        return await asyncio.wait_for(
            scrape_resellers_batch(resellers, reference, max_concurrent=3),
            timeout=30.0,
        )
    except Exception:
        return []


class SocialAgent(BaseAgent):
    """
    Monitora post, stories e video dei reseller su:
      - Instagram (post via instagrapi + stories via Playwright)
      - TikTok (video con hashtag watch/orologio)
      - Facebook Marketplace (annunci pubblici)
      - Siti web reseller (da bio link)

    Setup richiesto nel file backend/.env:
      INSTAGRAM_USERNAME=tuo_username
      INSTAGRAM_PASSWORD=tua_password
      TIKTOK_SESSION_ID=<cookie sessionid TikTok, opzionale>
      FACEBOOK_COOKIES=<JSON array cookie Facebook, opzionale>

    Il primo login Instagram salva la sessione in instagram_session.json (~90 giorni).
    """

    def __init__(self):
        super().__init__("social_agent")

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        await asyncio.sleep(0.2)
        listings = []
        listings.extend(mock_instagram_listings(query.reference))
        listings.extend(mock_tiktok_listings(query.reference))
        listings.extend(mock_facebook_listings(query.reference))
        return listings

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        reference = query.reference

        # ── Fase 1: Playwright stories (dal DB locale, sempre disponibili) ────
        from scrapers.stories.pipeline import get_stories_listings
        playwright_stories_task = asyncio.create_task(
            get_stories_listings(reference)
        )

        # ── Fase 2: TikTok + Facebook Marketplace in parallelo ────────────────
        # return_exceptions=True: un fallimento non blocca gli altri
        tiktok_task = asyncio.create_task(_tiktok_scan(reference))
        facebook_task = asyncio.create_task(_facebook_scan(reference))
        bio_links_task = asyncio.create_task(_bio_links_scan(reference))

        # ── Fase 3: Instagram instagrapi (opzionale) ──────────────────────────
        instagram_listings: list[WatchListing] = []
        cached_stories: list[WatchListing] = []

        if self.settings.instagram_username and self.settings.instagram_password:
            from scrapers.instagram_stories import get_cached_stories
            cached_stories = get_cached_stories(reference)

            try:
                _cl, instagram_listings = await asyncio.wait_for(
                    _run_instagram_full(
                        reference,
                        self.settings.instagram_username,
                        self.settings.instagram_password,
                    ),
                    timeout=30.0,
                )
            except Exception as e:
                self.logger.warning(
                    f"Instagram instagrapi fallito ({type(e).__name__}) — continuo con gli altri"
                )
        else:
            self.logger.info("INSTAGRAM_USERNAME/PASSWORD non configurati — skip instagrapi")

        # ── Raccogli tutti i risultati ────────────────────────────────────────
        playwright_stories = await playwright_stories_task
        if playwright_stories:
            self.logger.info(f"Playwright stories: {len(playwright_stories)} risultati")

        # Attendi TikTok, Facebook e bio links
        gathered = await asyncio.gather(
            tiktok_task,
            facebook_task,
            bio_links_task,
            return_exceptions=True,
        )

        tiktok_listings: list[WatchListing] = []
        facebook_listings: list[WatchListing] = []
        bio_link_listings: list[WatchListing] = []

        if isinstance(gathered[0], list):
            tiktok_listings = gathered[0]
            self.logger.info(f"TikTok: {len(tiktok_listings)} risultati")
        else:
            self.logger.warning(f"TikTok fallito: {gathered[0]}")

        if isinstance(gathered[1], list):
            facebook_listings = gathered[1]
            self.logger.info(f"Facebook Marketplace: {len(facebook_listings)} risultati")
        else:
            self.logger.warning(f"Facebook Marketplace fallito: {gathered[1]}")

        if isinstance(gathered[2], list):
            bio_link_listings = gathered[2]
            self.logger.info(f"Bio links: {len(bio_link_listings)} risultati")
        else:
            self.logger.debug(f"Bio links fallito: {gathered[2]}")

        # ── Unisci tutti i risultati ──────────────────────────────────────────
        all_listings = (
            playwright_stories
            + instagram_listings
            + cached_stories
            + tiktok_listings
            + facebook_listings
            + bio_link_listings
        )

        # Deduplicazione per URL (due scraper possono trovare lo stesso post)
        seen: set[str] = set()
        unique: list[WatchListing] = []
        for listing in all_listings:
            if listing.url not in seen:
                seen.add(listing.url)
                unique.append(listing)

        self.logger.info(
            f"Social scan totale: {len(unique)} listing unici per {reference} "
            f"(stories={len(playwright_stories)}, ig={len(instagram_listings)}, "
            f"tt={len(tiktok_listings)}, fb={len(facebook_listings)}, "
            f"bio={len(bio_link_listings)})"
        )
        return unique
