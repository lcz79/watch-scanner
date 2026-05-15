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


def _normalize_ref(s: str) -> str:
    """Normalizza una referenza: uppercase, rimuove spazi e trattini."""
    return s.upper().replace(" ", "").replace("-", "")


def _is_exact_match(listing_ref: str, query_ref: str) -> bool:
    """
    True se la referenza del listing corrisponde esattamente alla query.
    Confronto case-insensitive, ignorando spazi e trattini.
    """
    norm_query = _normalize_ref(query_ref)
    norm_listing = _normalize_ref(listing_ref)
    return norm_query in norm_listing or norm_listing in norm_query


def _sort_and_deduplicate(
    listings: list[WatchListing],
    reference: str = "",
) -> tuple[list[WatchListing], list[WatchListing]]:
    """
    Rimuove duplicati per URL, filtra outlier di prezzo, ordina per prezzo crescente.

    Ritorna una tupla (exact_matches, related):
    - exact_matches: listing che corrispondono esattamente alla referenza cercata
    - related: listing della stessa famiglia ma con variante diversa (es. 5711/1G vs 5711/1A)
    """
    try:
        from watch_db import is_price_plausible
        _price_check = lambda ref, price: is_price_plausible(ref, price)
    except Exception:
        _price_check = lambda ref, price: True

    seen_urls = set()
    exact: list[WatchListing] = []
    related: list[WatchListing] = []
    skipped = 0

    for l in listings:
        if l.url in seen_urls:
            continue
        seen_urls.add(l.url)

        # Scarta prezzi assurdi (< 500€ = accessori/errori OCR)
        if l.price < 500:
            skipped += 1
            continue

        # Scarta stories a bassa confidence
        if l.source == "instagram_story" and getattr(l, "confidence", 1.0) < 0.5:
            skipped += 1
            continue

        # Verifica plausibilità prezzo rispetto al DB canonico
        ref = reference or getattr(l, "reference", "")
        if ref and not _price_check(ref, l.price):
            logger.debug(f"Prezzo fuori range per {ref}: {l.price}€ da {l.source} — scartato")
            skipped += 1
            continue

        # Separa exact match da related
        if reference:
            listing_ref_field = getattr(l, "reference", "") or ""
            listing_description = getattr(l, "description", "") or ""
            # Controlla sia il campo reference che la description
            if _is_exact_match(listing_ref_field, reference) or _is_exact_match(listing_description, reference):
                exact.append(l)
            else:
                related.append(l)
        else:
            exact.append(l)

    if skipped:
        logger.debug(f"Filtrati {skipped} listing con prezzo non plausibile")

    return sorted(exact, key=lambda x: x.price), sorted(related, key=lambda x: x.price)


async def _apply_vision_filter(listings: list[WatchListing]) -> list[WatchListing]:
    """Applica vision filter solo se ci sono listing con immagini (opzionale, più lento)."""
    try:
        from utils.vision_filter import filter_listings_by_image
        return await filter_listings_by_image(listings)
    except Exception as e:
        logger.warning(f"Vision filter error: {e}")
        return listings


async def run_scan(query: WatchQuery) -> ScanResult:
    """
    Esegue tutti gli agenti in parallelo e aggrega i risultati.
    Gli errori di un singolo agente non bloccano gli altri.
    """
    # Normalizza referenza: strip + uppercase per matching coerente
    query = query.model_copy(update={"reference": query.reference.strip().upper()})

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

    # Aggiungi listing pre-indicizzati dalle Instagram Stories (GPT-4o Vision)
    try:
        from agents.stories_intelligence_agent import get_listings_for_reference
        story_listings_raw = get_listings_for_reference(query.reference)
        for sl in story_listings_raw:
            all_listings.append(WatchListing(
                source="instagram_story_ai",
                reference=sl.get("reference_raw") or query.reference,
                price=float(sl["price"]) if sl.get("price") else 0,
                currency=sl.get("currency", "EUR"),
                seller=f"@{sl['dealer_username']}",
                url=sl.get("story_url") or f"https://www.instagram.com/{sl['dealer_username']}/",
                condition=sl.get("condition", "unknown"),
                scraped_at=datetime.fromisoformat(sl["scraped_at"]) if sl.get("scraped_at") else datetime.now(),
                description=f"{sl.get('brand', '')} {sl.get('model', '')} — story @{sl['dealer_username']}",
                image_url=sl.get("image_url"),
            ))
        if story_listings_raw:
            agents_used.append("stories_ai")
            logger.info(f"[{scan_id}] stories_ai: {len(story_listings_raw)} listing pre-indicizzati")
    except Exception as e:
        logger.debug(f"[{scan_id}] stories_ai merge error: {e}")

    listings, related_listings = _sort_and_deduplicate(all_listings, reference=query.reference)

    # Filtra per max_price se specificato
    if query.max_price:
        listings = [l for l in listings if l.price <= query.max_price]
        related_listings = [l for l in related_listings if l.price <= query.max_price]

    best = listings[0] if listings else None
    duration = (datetime.now() - start_time).total_seconds()

    logger.info(
        f"[{scan_id}] Done | found={len(listings)} exact + {len(related_listings)} related"
        f" | best={best.price if best else 'N/A'} | {duration:.2f}s"
    )

    return ScanResult(
        scan_id=scan_id,
        query=query,
        listings=listings,
        related_listings=related_listings,
        best_price=best.price if best else None,
        best_listing=best,
        total_found=len(listings),
        scanned_at=start_time,
        agents_used=agents_used,
        duration_seconds=duration,
    )


def get_agents_status() -> list[AgentStatus]:
    return [agent.status() for agent in _agents.values()]
