"""
Instagram Discovery Agent.

Scopre nuovi dealer di orologi su Instagram tramite:
  1. Hashtag crawl — cerca post recenti su hashtag di settore
  2. Follower expansion — estrae follower degli account seed

Per ogni account trovato: upsert nel DB tramite resellers_db.
"""

import asyncio
import random

from utils.logger import get_logger
from agents.discovery import resellers_db as db_module

logger = get_logger("discovery.instagram")

SEED_HASHTAGS = [
    "rolexforsale", "watchdealer", "luxurywatches", "daytona",
    "watchreseller", "orologiousato", "rolexdealer", "patekphilippe",
    "audemarspiguet", "watchcollector", "luxurywatchforsale",
    "watchscanner", "orologi", "orologi_lusso", "venditaorologi",
    "watchforsale", "preownedwatches", "vintagerolex", "watchmarket",
]

# Account seed fissi + account Watch Scanner (aggiunto come punto di partenza principale)
SEED_ACCOUNTS = [
    "watch.scanner",          # account principale Watch Scanner — SEED PRIMARIO
    "watchesofitalia", "luxurywatchesmilan", "watchmarket_it",
    "orologi_secondmano", "watchhunter_eu",
]

# Quanti top-dealer scoperti nella fase 1 vengono usati come seed per la fase cascade
CASCADE_TOP_N = 20


def _build_account_dict(user) -> dict:
    """Converte un oggetto instagrapi UserShort/UserInfo in dict standard."""
    return {
        "username": getattr(user, "username", ""),
        "bio": getattr(user, "biography", "") or "",
        "followers_count": getattr(user, "follower_count", 0) or 0,
        "post_count": getattr(user, "media_count", 0) or 0,
        "website": getattr(user, "external_url", "") or "",
        "pk": str(getattr(user, "pk", "")),
    }


async def upsert_dealer(account: dict, discovered_via: str):
    """Inserisce o aggiorna il dealer nel DB condiviso, salvando anche il sito web."""
    from agents.discovery.bio_link_extractor import resolve_bio_links

    db = db_module.load()
    username = account.get("username", "")
    if not username or db_module.is_known(db, username):
        return

    score, reasons = db_module.score_account(
        bio=account.get("bio", ""),
        recent_captions=[],
        followers=account.get("followers_count", 0),
        following=0,
    )

    # BUG FIX 1: salva il website (external_url da Instagram API)
    website = account.get("website", "") or ""

    # BUG FIX 2: se non c'è website diretto, prova a estrarlo dalla bio
    if not website and account.get("bio"):
        try:
            bio_links = await resolve_bio_links(account["bio"])
            if bio_links:
                website = bio_links[0]  # prendi il primo link rilevante
                logger.debug(f"  @{username} — bio link estratto: {website}")
        except Exception as e:
            logger.debug(f"  @{username} — bio_link_extractor errore: {e}")

    if score >= db_module.MIN_SCORE:
        db_module.add_reseller(
            db,
            username=username,
            platform="instagram",
            score=score,
            reasons=reasons,
            followers=account.get("followers_count", 0),
            bio=account.get("bio", ""),
            discovered_via=discovered_via,
            pk=account.get("pk", ""),
        )
        # BUG FIX 1 (cont.): persiste il website nel DB SQLite
        if website:
            db_module.upsert_dealer({"username": username, "website": website})
            logger.info(f"  @{username} — sito salvato: {website}")
    else:
        db_module.blacklist(db, username)
    db_module.save(db)


async def discover_from_hashtags(cl, hashtags: list[str], per_hashtag: int = 20) -> list[dict]:
    """
    Cerca account dai post recenti di una lista di hashtag.

    Args:
        cl: istanza instagrapi.Client già autenticata.
        hashtags: lista di hashtag (senza #).
        per_hashtag: numero massimo di post da esaminare per hashtag.

    Returns:
        Lista di dict {username, bio, followers_count, post_count, website}.
    """
    results: list[dict] = []
    seen: set[str] = set()

    for hashtag in hashtags:
        try:
            logger.info(f"[hashtag] #{hashtag} — fetching up to {per_hashtag} post...")
            medias = cl.hashtag_medias_recent_v1(hashtag, amount=per_hashtag)

            for media in medias:
                username = getattr(media.user, "username", None)
                if not username or username in seen:
                    continue
                seen.add(username)

                try:
                    user_info = cl.user_info_by_username(username)
                    account = _build_account_dict(user_info)
                    results.append(account)
                    logger.debug(f"  @{username} — {account['followers_count']} follower")
                    await upsert_dealer(account, discovered_via=f"#{hashtag}")
                    await asyncio.sleep(random.uniform(2, 5))

                except Exception as e:
                    _handle_instagrapi_error(e, context=f"user_info @{username}")
                    if _is_fatal(e):
                        logger.error("[hashtag] Errore fatale — uscita anticipata.")
                        return results

        except Exception as e:
            _handle_instagrapi_error(e, context=f"hashtag #{hashtag}")
            if _is_fatal(e):
                logger.error("[hashtag] Errore fatale — uscita anticipata.")
                return results

        await asyncio.sleep(random.uniform(2, 5))

    logger.info(f"[hashtag] Completato — {len(results)} account trovati su {len(hashtags)} hashtag")
    return results


async def discover_from_account_followers(cl, username: str, limit: int = 50) -> list[dict]:
    """
    Estrae i follower di un account seed.

    Args:
        cl: istanza instagrapi.Client già autenticata.
        username: handle dell'account target (senza @).
        limit: numero massimo di follower da estrarre.

    Returns:
        Lista di dict {username, bio, followers_count, post_count, website}.
    """
    results: list[dict] = []

    try:
        logger.info(f"[followers] @{username} — fetching up to {limit} follower...")
        user_info = cl.user_info_by_username(username)
        pk = int(user_info.pk)
        await asyncio.sleep(random.uniform(2, 5))

        followers = cl.user_followers(pk, amount=limit)

        for follower_pk, follower_user in followers.items():
            follower_username = getattr(follower_user, "username", None)
            if not follower_username:
                continue

            try:
                full_info = cl.user_info(follower_pk)
                account = _build_account_dict(full_info)
                results.append(account)
                logger.debug(f"  @{follower_username} — {account['followers_count']} follower")
                await upsert_dealer(account, discovered_via=f"follower di @{username}")
                await asyncio.sleep(random.uniform(2, 5))

            except Exception as e:
                _handle_instagrapi_error(e, context=f"user_info follower @{follower_username}")
                if _is_fatal(e):
                    logger.error("[followers] Errore fatale — uscita anticipata.")
                    return results

    except Exception as e:
        _handle_instagrapi_error(e, context=f"followers di @{username}")

    logger.info(f"[followers] @{username} — {len(results)} follower estratti")
    return results


async def discover_from_account_following(cl, username: str, limit: int = 50) -> list[dict]:
    """Estrae gli account che un seed SEGUE (following) — spesso altri dealer."""
    results: list[dict] = []
    try:
        logger.info(f"[following] @{username} — fetching up to {limit} following...")
        user_info = cl.user_info_by_username(username)
        pk = int(user_info.pk)
        await asyncio.sleep(random.uniform(2, 5))

        following = cl.user_following(pk, amount=limit)
        for f_pk, f_user in following.items():
            f_username = getattr(f_user, "username", None)
            if not f_username:
                continue
            try:
                full_info = cl.user_info(f_pk)
                account = _build_account_dict(full_info)
                results.append(account)
                await upsert_dealer(account, discovered_via=f"following di @{username}")
                await asyncio.sleep(random.uniform(2, 5))
            except Exception as e:
                _handle_instagrapi_error(e, context=f"user_info following @{f_username}")
                if _is_fatal(e):
                    return results
    except Exception as e:
        _handle_instagrapi_error(e, context=f"following di @{username}")

    logger.info(f"[following] @{username} — {len(results)} following estratti")
    return results


async def run_instagram_discovery(username: str, password: str) -> list[dict]:
    """
    Entry point principale.

    Fasi:
      1. Hashtag crawl su hashtag di settore
      2. Followers + following dei SEED_ACCOUNTS (incluso watch.scanner)
      3. Cascade: stessa espansione sui TOP_N dealer scoperti nella fase 1+2
         → questo crea il network a cascata che il sistema richiede
    """
    try:
        from instagrapi import Client
    except ImportError:
        logger.error("instagrapi non installato. Esegui: pip install instagrapi")
        return []

    cl = Client()
    cl.delay_range = [2, 5]

    logger.info(f"[instagram] Login come @{username}...")
    try:
        cl.login(username, password)
        logger.info("[instagram] Login riuscito.")
    except Exception as e:
        logger.error(f"[instagram] Login fallito: {e}")
        return []

    all_accounts: list[dict] = []

    # ── Fase 1: Hashtag crawl ──────────────────────────────────────────────
    logger.info(f"[instagram] ── Fase 1: hashtag crawl ({len(SEED_HASHTAGS)} hashtag)")
    r1 = await discover_from_hashtags(cl, SEED_HASHTAGS, per_hashtag=25)
    all_accounts.extend(r1)
    logger.info(f"[instagram] Fase 1 OK — {len(r1)} account")
    await asyncio.sleep(random.uniform(5, 10))

    # ── Fase 2: Followers + following dei seed account ─────────────────────
    logger.info(f"[instagram] ── Fase 2: seed expansion ({len(SEED_ACCOUNTS)} account)")
    for seed in SEED_ACCOUNTS:
        try:
            r_fol = await discover_from_account_followers(cl, seed, limit=100)
            all_accounts.extend(r_fol)
            await asyncio.sleep(random.uniform(3, 7))
            r_ing = await discover_from_account_following(cl, seed, limit=100)
            all_accounts.extend(r_ing)
        except Exception as e:
            logger.warning(f"[instagram] Seed @{seed} fallito: {e}")
        await asyncio.sleep(random.uniform(5, 10))

    # ── Fase 3: Cascade sui top dealer scoperti ────────────────────────────
    # Prende i CASCADE_TOP_N dealer con score più alto dal DB e li usa come seed
    db = db_module.load()
    top_dealers = sorted(
        db.get("resellers", {}).values(),
        key=lambda d: d.get("score", 0),
        reverse=True,
    )[:CASCADE_TOP_N]

    if top_dealers:
        logger.info(f"[instagram] ── Fase 3: cascade su {len(top_dealers)} top dealer")
        for dealer in top_dealers:
            seed = dealer.get("username", "")
            if not seed or seed in SEED_ACCOUNTS:
                continue
            try:
                r_fol = await discover_from_account_followers(cl, seed, limit=50)
                all_accounts.extend(r_fol)
                await asyncio.sleep(random.uniform(3, 6))
                r_ing = await discover_from_account_following(cl, seed, limit=50)
                all_accounts.extend(r_ing)
            except Exception as e:
                logger.warning(f"[instagram] Cascade @{seed} fallito: {e}")
            await asyncio.sleep(random.uniform(4, 8))

    # Deduplication
    seen: set[str] = set()
    unique = []
    for acc in all_accounts:
        u = acc.get("username", "")
        if u and u not in seen:
            seen.add(u)
            unique.append(acc)

    stats = db_module.get_stats()
    logger.info(
        f"[instagram] ── Discovery completata: {len(unique)} account unici | "
        f"DB totale: {stats['total']} reseller | "
        f"Con sito web: {sum(1 for r in db.get('resellers', {}).values() if r.get('website'))}"
    )
    return unique


# ---------------------------------------------------------------------------
# Helpers per gestione errori instagrapi
# ---------------------------------------------------------------------------

def _handle_instagrapi_error(exc: Exception, context: str = ""):
    """Logga l'eccezione con livello appropriato."""
    name = type(exc).__name__
    msg = str(exc)[:120]
    if name in ("RateLimitError", "ChallengeRequired", "LoginRequired"):
        logger.warning(f"[instagrapi] {name} in {context}: {msg}")
    else:
        logger.debug(f"[instagrapi] {name} in {context}: {msg}")


def _is_fatal(exc: Exception) -> bool:
    """True se l'eccezione richiede uscita anticipata dalla sessione."""
    fatal_names = {"LoginRequired", "ChallengeRequired", "RateLimitError"}
    return type(exc).__name__ in fatal_names
