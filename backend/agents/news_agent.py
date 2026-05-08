"""
Watch News Agent.

Scansiona RSS feeds di testate orologerie ogni 12 ore.
Fonti: Hodinkee, WatchPro, Fratello, Monochrome, ABlogToWatch, Europastar, Revolution.

Salva in SQLite (news.db) con deduplicazione per URL.
"""

import asyncio
import json
import re
import sqlite3
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
from utils.logger import get_logger

logger = get_logger("news_agent")

DB_PATH = Path(__file__).parent.parent / "data" / "news.db"

SCAN_INTERVAL_HOURS = 12

RSS_FEEDS = [
    ("Hodinkee",       "https://www.hodinkee.com/articles.rss"),
    ("Fratello",       "https://www.fratellowatches.com/feed/"),
    ("Monochrome",     "https://monochrome-watches.com/feed/"),
    ("ABlogToWatch",   "https://www.ablogtowatch.com/feed/"),
    ("Europastar",     "https://www.europastar.com/feed/rss/"),
    ("Revolution",     "https://revolutionwatch.com/feed/"),
    ("WatchTime",      "https://www.watchtime.com/feed/rss/"),
]

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

BRAND_TAGS = [
    "rolex", "patek", "patek philippe", "audemars", "ap", "royal oak",
    "omega", "tudor", "iwc", "panerai", "cartier", "breitling",
    "lange", "jaeger", "vacheron", "hublot", "richard mille", "zenith",
    "grand seiko", "seiko", "longines", "tissot",
]
TOPIC_TAGS = [
    "auction", "asta", "new release", "nuovo", "vintage", "market",
    "mercato", "price", "prezzo", "investment", "investimento",
    "baselworld", "watches & wonders", "geneve", "sotheby", "christie",
    "phillips", "antiquorum", "record", "limited",
]


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = _connect()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS watch_news (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT    NOT NULL,
                summary      TEXT,
                url          TEXT    NOT NULL UNIQUE,
                image_url    TEXT,
                source       TEXT    NOT NULL,
                source_url   TEXT,
                published_at TIMESTAMP,
                scraped_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags         TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_news_published
                ON watch_news(published_at DESC);
            CREATE INDEX IF NOT EXISTS idx_news_source
                ON watch_news(source);
        """)
    conn.close()
    logger.debug("news_db schema OK")


def _extract_tags(title: str, summary: str) -> list[str]:
    text = (title + " " + (summary or "")).lower()
    found = []
    for kw in BRAND_TAGS + TOPIC_TAGS:
        if kw in text:
            found.append(kw.replace(" ", "-"))
    return list(dict.fromkeys(found))[:10]


def _strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def _parse_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    try:
        # ISO format fallback
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).isoformat()
    except Exception:
        return None


def _extract_image(entry) -> str | None:
    # media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    # media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            if m.get("type", "").startswith("image"):
                return m.get("url")
    # enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image"):
                return enc.get("href") or enc.get("url")
    # img tag in summary
    if hasattr(entry, "summary"):
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary or "")
        if m:
            return m.group(1)
    return None


async def fetch_feed(source_name: str, feed_url: str) -> list[dict]:
    import feedparser
    try:
        async with httpx.AsyncClient(timeout=15, headers={"User-Agent": _UA}, follow_redirects=True) as client:
            r = await client.get(feed_url)
            r.raise_for_status()
            content = r.text
    except Exception as e:
        logger.warning(f"[news] {source_name} feed error: {e}")
        return []

    try:
        feed = feedparser.parse(content)
        items = []
        for entry in feed.entries[:20]:
            title = _strip_html(getattr(entry, "title", ""))
            if not title:
                continue
            url = getattr(entry, "link", "")
            if not url:
                continue
            summary = _strip_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            image_url = _extract_image(entry)
            published_at = _parse_date(getattr(entry, "published", None))
            tags = _extract_tags(title, summary)
            items.append({
                "title": title,
                "summary": summary,
                "url": url,
                "image_url": image_url,
                "source": source_name,
                "source_url": feed_url,
                "published_at": published_at,
                "tags": json.dumps(tags),
            })
        logger.info(f"[news] {source_name}: {len(items)} articoli")
        return items
    except Exception as e:
        logger.warning(f"[news] {source_name} parse error: {e}")
        return []


def save_news(items: list[dict]) -> int:
    if not items:
        return 0
    conn = _connect()
    inserted = 0
    with conn:
        for item in items:
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO watch_news
                        (title, summary, url, image_url, source, source_url, published_at, tags)
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        item["title"], item.get("summary"), item["url"],
                        item.get("image_url"), item["source"], item.get("source_url"),
                        item.get("published_at"), item.get("tags"),
                    ),
                )
                if conn.execute("SELECT changes()").fetchone()[0]:
                    inserted += 1
            except Exception as e:
                logger.debug(f"[news] insert error: {e}")
    conn.close()
    return inserted


def get_recent_news(limit: int = 20, source: str | None = None, tag: str | None = None) -> list[dict]:
    conn = _connect()
    q = "SELECT * FROM watch_news WHERE 1=1"
    params: list = []
    if source:
        q += " AND source = ?"
        params.append(source)
    if tag:
        q += " AND tags LIKE ?"
        params.append(f'%"{tag}"%')
    q += " ORDER BY published_at DESC NULLS LAST, scraped_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["tags"] = json.loads(d.get("tags") or "[]")
        except Exception:
            d["tags"] = []
        result.append(d)
    return result


def get_stats() -> dict:
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) FROM watch_news").fetchone()[0]
    sources = conn.execute(
        "SELECT source, COUNT(*) as n FROM watch_news GROUP BY source ORDER BY n DESC"
    ).fetchall()
    conn.close()
    return {"total": total, "sources": [dict(r) for r in sources]}


async def run_news_scan() -> int:
    init_db()
    tasks = [fetch_feed(name, url) for name, url in RSS_FEEDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_items = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)
    inserted = save_news(all_items)
    logger.info(f"[news] Scan completato: {len(all_items)} articoli trovati, {inserted} nuovi")
    return inserted


async def start_news_scheduler():
    logger.info(f"[news] Scheduler avviato (ogni {SCAN_INTERVAL_HOURS}h)")
    await asyncio.sleep(30)  # prima run 30s dopo l'avvio
    while True:
        try:
            count = await run_news_scan()
            logger.info(f"[news] Scan periodico: {count} nuovi articoli")
        except Exception as e:
            logger.error(f"[news] Scheduler error: {e}")
        await asyncio.sleep(SCAN_INTERVAL_HOURS * 3600)
