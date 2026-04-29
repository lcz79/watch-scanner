"""
Agente di discovery per trovare reseller di orologi su Instagram.

Strategia in 3 fasi:
  1. HASHTAG CRAWL — cerca hashtag di vendita orologi, raccoglie tutti gli account
  2. ACCOUNT SCORING — punteggio per ogni account: bio, frequenza post, prezzi in caption
  3. NETWORK EXPANSION — dai reseller confermati, analizza chi seguono per trovarne altri

Il risultato viene salvato in resellers_db.json e usato dal SocialAgent.
Lancia questo script manualmente o schedulalo (es. una volta al giorno).

Uso:
  python scrapers/reseller_discovery.py --reference 116610LN
  python scrapers/reseller_discovery.py --expand  (network expansion da reseller già noti)
"""

import json
import re
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("reseller_discovery")

DB_FILE = Path(__file__).parent.parent / "resellers_db.json"

# Hashtag di partenza per la discovery
SEED_HASHTAGS = [
    # Vendita generica
    "watchforsale", "watchesofinstagram", "watchreseller",
    "orologiousato", "orologiusati", "orologiovendo", "vendoorologio",
    "preloved_watches", "prelovedwatches", "luxurywatchforsale",
    # Per brand
    "rolexforsale", "rolexreseller", "rolexsubmariner",
    "patekphilippeforsale", "audemarspiguetforsale",
    "iwcforsale", "omegaforsale", "tudorforsale",
    # Italiano
    "orologioprezzo", "vendoorologiorolex", "rolexusato",
    "orologi_secondmano", "secondmano_orologio",
    # Internazionale
    "watchdealer", "watchtrader", "horologyforsale",
    "independentwatchdealer",
]

# Keyword nella bio che indicano un reseller
BIO_RESELLER_KEYWORDS = [
    "reseller", "dealer", "trader", "vendita", "vendo", "for sale",
    "compro", "compra", "buy", "sell", "orologio", "watch", "timepiece",
    "dm for price", "dm per prezzo", "available", "disponibile",
    "preloved", "pre-owned", "preowned", "second hand", "usato",
    "luxury", "lusso", "rolex", "patek", "audemars", "omega", "tudor",
    "boutique", "authorized", "certified",
]

# Keyword nei post che indicano un annuncio di vendita
SALE_POST_KEYWORDS = [
    "vendo", "vendesi", "for sale", "forsale", "prezzo", "price",
    "asking", "dm", "available", "disponibile", "€", "euro",
    "box and papers", "full set", "con scatola",
]

# Score minimo per essere considerato reseller
MIN_SCORE = 3


def _load_db() -> dict:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text())
    return {"resellers": {}, "blacklist": [], "last_updated": None}


def _save_db(db: dict):
    db["last_updated"] = datetime.now().isoformat()
    DB_FILE.write_text(json.dumps(db, indent=2, ensure_ascii=False))
    logger.info(f"Database salvato: {len(db['resellers'])} reseller noti")


def _score_account(user_info: dict, recent_posts: list) -> tuple[int, list[str]]:
    """
    Assegna un punteggio all'account. Più alto = più probabile reseller.
    Ritorna (score, motivi).
    """
    score = 0
    reasons = []
    bio = (user_info.get("biography", "") or "").lower()

    # 1. Bio keywords (+1 per ogni keyword trovata, max 4)
    bio_matches = [kw for kw in BIO_RESELLER_KEYWORDS if kw in bio]
    bio_score = min(len(bio_matches), 4)
    if bio_score > 0:
        score += bio_score
        reasons.append(f"bio keywords: {bio_matches[:3]}")

    # 2. Link in bio (i reseller spesso hanno link a negozio/Linktree)
    if user_info.get("external_url"):
        score += 1
        reasons.append("link in bio")

    # 3. Rapporto follower/following (reseller: molti follower, following moderato)
    followers = user_info.get("follower_count", 0)
    following = user_info.get("following_count", 1)
    if 500 < followers < 500_000:
        score += 1
        reasons.append(f"{followers} follower")
    if following > 0 and followers / following > 1.5:
        score += 1
        reasons.append("buon rapporto follower/following")

    # 4. Analisi post recenti: percentuale con prezzi/keyword di vendita
    if recent_posts:
        sale_posts = 0
        price_posts = 0
        for post in recent_posts:
            caption = (post.get("caption_text", "") or "").lower()
            if any(kw in caption for kw in SALE_POST_KEYWORDS):
                sale_posts += 1
            if re.search(r'[\d\.]+\s*[€$]|[€$]\s*[\d\.]+', caption):
                price_posts += 1

        pct_sale = sale_posts / len(recent_posts)
        if pct_sale > 0.3:
            score += 2
            reasons.append(f"{sale_posts}/{len(recent_posts)} post con keyword vendita")
        if price_posts > 0:
            score += 1
            reasons.append(f"{price_posts} post con prezzi")

    return score, reasons


async def discover_via_hashtags(cl, hashtags: list[str], db: dict, max_per_tag: int = 50) -> int:
    """
    Fase 1: cerca per hashtag e raccoglie gli account.
    """
    new_found = 0
    for hashtag in hashtags:
        try:
            logger.info(f"Cercando #{hashtag}...")
            medias = cl.hashtag_medias_recent_v1(hashtag, amount=max_per_tag)

            for media in medias:
                try:
                    username = media.user.username
                    if username in db["resellers"] or username in db["blacklist"]:
                        continue

                    # Recupera info account e post recenti
                    user_info = cl.user_info_by_username(username).model_dump()
                    recent_posts = [m.model_dump() for m in cl.user_medias(media.user.pk, amount=15)]

                    score, reasons = _score_account(user_info, recent_posts)

                    if score >= MIN_SCORE:
                        db["resellers"][username] = {
                            "username": username,
                            "score": score,
                            "reasons": reasons,
                            "followers": user_info.get("follower_count", 0),
                            "bio": user_info.get("biography", "")[:200],
                            "discovered_via": f"#{hashtag}",
                            "discovered_at": datetime.now().isoformat(),
                            "pk": str(media.user.pk),
                        }
                        new_found += 1
                        logger.info(f"  ✓ @{username} (score={score}) — {reasons}")
                    else:
                        db["blacklist"].append(username)

                    await asyncio.sleep(2)  # rate limiting

                except Exception as e:
                    logger.debug(f"  Errore analisi @{media.user.username}: {e}")
                    continue

            await asyncio.sleep(3)

        except Exception as e:
            logger.warning(f"Hashtag #{hashtag} error: {e}")
            continue

    return new_found


async def expand_via_network(cl, db: dict, max_accounts: int = 20) -> int:
    """
    Fase 3: dai reseller già noti, analizza chi seguono per trovarne altri.
    I reseller tendono a seguirsi a vicenda.
    """
    new_found = 0
    known_resellers = list(db["resellers"].keys())[:max_accounts]

    for username in known_resellers:
        try:
            pk = db["resellers"][username].get("pk")
            if not pk:
                continue

            logger.info(f"Network expansion da @{username}...")
            followings = cl.user_following(pk, amount=50)

            for followed_pk, followed_user in followings.items():
                followed_username = followed_user.username
                if followed_username in db["resellers"] or followed_username in db["blacklist"]:
                    continue

                try:
                    user_info = cl.user_info(followed_pk).model_dump()
                    recent_posts = [m.model_dump() for m in cl.user_medias(followed_pk, amount=12)]
                    score, reasons = _score_account(user_info, recent_posts)

                    if score >= MIN_SCORE:
                        db["resellers"][followed_username] = {
                            "username": followed_username,
                            "score": score,
                            "reasons": reasons,
                            "followers": user_info.get("follower_count", 0),
                            "bio": user_info.get("biography", "")[:200],
                            "discovered_via": f"following di @{username}",
                            "discovered_at": datetime.now().isoformat(),
                            "pk": str(followed_pk),
                        }
                        new_found += 1
                        logger.info(f"  ✓ @{followed_username} (score={score})")
                    else:
                        db["blacklist"].append(followed_username)

                    await asyncio.sleep(1.5)

                except Exception as e:
                    logger.debug(f"  Errore @{followed_username}: {e}")
                    continue

            await asyncio.sleep(4)

        except Exception as e:
            logger.warning(f"Network expansion da @{username} fallita: {e}")
            continue

    return new_found


def get_reseller_list(min_score: int = MIN_SCORE) -> list[str]:
    """
    Ritorna la lista di username reseller dal DB.
    Usata dal SocialAgent per sapere chi monitorare.
    """
    db = _load_db()
    return [
        username for username, info in db["resellers"].items()
        if info.get("score", 0) >= min_score
    ]


def get_reseller_stats() -> dict:
    db = _load_db()
    resellers = db["resellers"]
    return {
        "total": len(resellers),
        "blacklisted": len(db.get("blacklist", [])),
        "last_updated": db.get("last_updated"),
        "top_10": sorted(
            [{"username": u, **info} for u, info in resellers.items()],
            key=lambda x: x["score"],
            reverse=True
        )[:10],
    }


async def run_discovery(username_ig: str, password_ig: str, mode: str = "hashtags"):
    """Entry point principale per la discovery."""
    try:
        from instagrapi import Client
    except ImportError:
        logger.error("Installa instagrapi: pip install instagrapi")
        return

    from pathlib import Path
    SESSION_FILE = Path(__file__).parent.parent / "instagram_session.json"

    cl = Client()
    cl.delay_range = [2, 5]

    # Login
    if SESSION_FILE.exists():
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.login(username_ig, password_ig)
        except Exception:
            SESSION_FILE.unlink(missing_ok=True)
            cl.login(username_ig, password_ig)
            cl.dump_settings(str(SESSION_FILE))
    else:
        cl.login(username_ig, password_ig)
        cl.dump_settings(str(SESSION_FILE))

    db = _load_db()
    logger.info(f"DB esistente: {len(db['resellers'])} reseller, {len(db.get('blacklist',[]))} blacklist")

    if mode == "hashtags" or mode == "full":
        logger.info("=== FASE 1: Discovery via hashtag ===")
        new = await discover_via_hashtags(cl, SEED_HASHTAGS, db, max_per_tag=30)
        logger.info(f"Nuovi reseller trovati via hashtag: {new}")
        _save_db(db)

    if mode == "expand" or mode == "full":
        logger.info("=== FASE 2: Network expansion ===")
        new = await expand_via_network(cl, db, max_accounts=15)
        logger.info(f"Nuovi reseller trovati via network: {new}")
        _save_db(db)

    # Report finale
    stats = get_reseller_stats()
    logger.info(f"\n=== RISULTATO ===")
    logger.info(f"Reseller totali nel DB: {stats['total']}")
    logger.info(f"Top reseller:")
    for r in stats["top_10"]:
        logger.info(f"  @{r['username']} | score={r['score']} | {r['followers']} follower | via {r['discovered_via']}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    parser = argparse.ArgumentParser(description="WatchScanner — Instagram Reseller Discovery")
    parser.add_argument("--username", required=True, help="Username Instagram")
    parser.add_argument("--password", required=True, help="Password Instagram")
    parser.add_argument("--mode", default="hashtags", choices=["hashtags", "expand", "full"],
                        help="hashtags=solo hashtag, expand=solo network, full=entrambi")
    args = parser.parse_args()

    asyncio.run(run_discovery(args.username, args.password, args.mode))
