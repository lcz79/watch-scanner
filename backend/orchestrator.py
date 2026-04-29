import asyncio
import uuid
from datetime import datetime

from agents.marketplace_agent import MarketplaceAgent
from agents.social_agent import SocialAgent
from agents.reseller_website_agent import ResellerWebsiteAgent
from agents.vision_agent import VisionAgent
from models.schemas import WatchQuery, ScanResult, WatchListing, AgentStatus
from utils.logger import get_logger

logger = get_logger("orchestrator")

# Istanze singleton degli agenti
_agents = {
    "marketplace": MarketplaceAgent(),
    "social": SocialAgent(),
    "reseller_websites": ResellerWebsiteAgent(),
    "vision": VisionAgent(),
}


def _sort_and_deduplicate(listings: list[WatchListing]) -> list[WatchListing]:
    """Rimuove duplicati per URL e ordina per prezzo crescente."""
    seen_urls = set()
    unique = []
    for l in listings:
        if l.url not in seen_urls:
            seen_urls.add(l.url)
            unique.append(l)

    # Filtra outlier di prezzo (accessori, OCR errati < 500€) e stories a bassa confidenza
    unique = [
        l for l in unique
        if l.price >= 500
        and not (l.source == "instagram_story" and getattr(l, 'confidence', 1.0) < 0.5)
    ]

    return sorted(unique, key=lambda x: x.price)


async def run_scan(query: WatchQuery) -> ScanResult:
    """
    Esegue tutti gli agenti in parallelo e aggrega i risultati.
    Gli errori di un singolo agente non bloccano gli altri.
    """
    start_time = datetime.now()
    scan_id = str(uuid.uuid4())[:8]

    logger.info(f"[{scan_id}] Starting scan | ref={query.reference} | agents={list(_agents.keys())}")

    tasks = {name: agent.run(query) for name, agent in _agents.items()}
    raw_results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    all_listings: list[WatchListing] = []
    agents_used: list[str] = []

    for agent_name, result in zip(tasks.keys(), raw_results):
        if isinstance(result, Exception):
            logger.error(f"[{scan_id}] Agent '{agent_name}' failed: {result}")
        else:
            all_listings.extend(result)
            if result:
                agents_used.append(agent_name)

    listings = _sort_and_deduplicate(all_listings)

    # Filtra per max_price se specificato
    if query.max_price:
        listings = [l for l in listings if l.price <= query.max_price]

    best = listings[0] if listings else None
    duration = (datetime.now() - start_time).total_seconds()

    logger.info(f"[{scan_id}] Done | found={len(listings)} | best={best.price if best else 'N/A'} | {duration:.2f}s")

    return ScanResult(
        scan_id=scan_id,
        query=query,
        listings=listings,
        best_price=best.price if best else None,
        best_listing=best,
        total_found=len(listings),
        scanned_at=start_time,
        agents_used=agents_used,
        duration_seconds=duration,
    )


def get_agents_status() -> list[AgentStatus]:
    return [agent.status() for agent in _agents.values()]
