"""
Usa Claude Vision per verificare che un listing mostri un orologio COMPLETO
(non un accessorio, ricambio o componente).
Usato per filtrare annunci eBay/Subito/Chrono24 che hanno image_url.
"""
import asyncio
import base64
import httpx
from utils.logger import get_logger

logger = get_logger("vision_filter")


async def _fetch_image_b64(url: str) -> tuple[str, str] | None:
    """Scarica un'immagine e la converte in base64."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                return None
            ct = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
            if ct not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
                ct = "image/jpeg"
            return base64.b64encode(r.content).decode(), ct
    except Exception as e:
        logger.debug(f"Image fetch failed {url}: {e}")
        return None


async def is_complete_watch_image(image_url: str, reference: str = "", brand: str = "") -> bool:
    """
    Usa Claude Vision per verificare che l'immagine mostri un orologio completo.
    Ritorna True se è un orologio completo, False se è un pezzo/accessorio/altra cosa.
    In caso di errore ritorna True (non filtrare per default).
    """
    result = await _fetch_image_b64(image_url)
    if not result:
        return True  # non possiamo verificare → non filtrare

    image_b64, media_type = result

    try:
        import anthropic
        client = anthropic.Anthropic()

        context = ""
        if brand:
            context += f" brand: {brand}"
        if reference:
            context += f", referenza: {reference}"

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",  # usa Haiku per costo/velocità
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64}
                    },
                    {
                        "type": "text",
                        "text": f"Questa immagine mostra un orologio da polso COMPLETO{context}? Rispondi solo: SI o NO. NO se mostra solo parti (quadrante, lancette, cinturino, ghiera, fondello, scatola vuota, catalogo, brochure)."
                    }
                ]
            }]
        )

        answer = message.content[0].text.strip().upper()
        is_watch = answer.startswith("SI") or answer.startswith("SÌ") or "YES" in answer
        logger.debug(f"Vision check {image_url[:60]}: {answer} → {'OK' if is_watch else 'SKIP'}")
        return is_watch

    except Exception as e:
        logger.debug(f"Vision check error: {e}")
        return True  # fallback: non filtrare


async def filter_listings_by_image(listings: list, max_concurrent: int = 5) -> list:
    """
    Filtra una lista di listing usando vision check sulle immagini.
    Solo i listing CON image_url vengono verificati.
    I listing senza immagine passano sempre (verificati solo dal testo).
    """
    without_image = [l for l in listings if not getattr(l, 'image_url', None)]
    with_image = [l for l in listings if getattr(l, 'image_url', None)]

    if not with_image:
        return listings

    # Verifica in batch paralleli
    sem = asyncio.Semaphore(max_concurrent)

    async def check(listing):
        async with sem:
            ok = await is_complete_watch_image(
                listing.image_url,
                reference=getattr(listing, 'reference', ''),
                brand='',
            )
            return listing if ok else None

    results = await asyncio.gather(*[check(l) for l in with_image])
    verified = [l for l in results if l is not None]

    rejected = len(with_image) - len(verified)
    if rejected:
        logger.info(f"Vision filter: {rejected} listing scartati (accessori/parti)")

    return without_image + verified
