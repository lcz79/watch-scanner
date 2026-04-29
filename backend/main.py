import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
import base64
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from datetime import datetime

from config import get_settings
from models.schemas import WatchQuery, ScanResult, AlertConfig, Alert, AgentStatus
from orchestrator import run_scan, get_agents_status
from utils.logger import get_logger
from analytics.market_engine import compute_market_stats
from analytics.deal_scorer import score_all_listings
from analytics.price_history import save_snapshot, get_history
from analytics.investment_scorer import compute_investment_score
from analytics.recommender import analyze_reference as _analyze_reference, get_recommendations as _get_recommendations

logger = get_logger("main")
settings = get_settings()

# Semplice storage in memoria per gli alert (in produzione: database)
_alerts: dict[str, Alert] = {}

# Cache globale per recommendations
_recommendations_cache: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    mode = "MOCK" if settings.mock_mode else "REAL"
    logger.info(f"WatchScanner API avviata | mode={mode} | port={settings.port}")

    # Avvia scheduler notturno discovery + job stories ogni 6h
    tasks = []
    if settings.instagram_username and settings.instagram_password:
        from agents.discovery.orchestrator import start_nightly_scheduler
        from scrapers.instagram_stories import start_stories_scheduler
        tasks.append(asyncio.create_task(
            start_nightly_scheduler(settings.instagram_username, settings.instagram_password)
        ))
        tasks.append(asyncio.create_task(
            start_stories_scheduler(settings.instagram_username, settings.instagram_password)
        ))
        logger.info("Scheduler discovery notturno + stories ogni 6h avviati")
    else:
        logger.info("Scheduler disabilitato (configura INSTAGRAM_USERNAME/PASSWORD)")

    # Avvia anche il nuovo scheduler Playwright stories (se auth presente)
    from scrapers.stories.capture import has_valid_auth
    if has_valid_auth():
        from scrapers.stories.pipeline import start_stories_scheduler_playwright
        tasks.append(asyncio.create_task(start_stories_scheduler_playwright()))
        logger.info("Playwright stories scheduler avviato")

    # Avvia alert checker (ogni 30 minuti, indipendente da Instagram)
    from agents.alert_checker import start_alert_scheduler
    tasks.append(asyncio.create_task(
        start_alert_scheduler(_alerts, settings)
    ))
    logger.info("Alert checker avviato (ogni 30 minuti)")

    yield

    for t in tasks:
        t.cancel()
    logger.info("WatchScanner API in arresto")


app = FastAPI(
    title="WatchScanner API",
    description="Sistema agentico per trovare il miglior prezzo su orologi di lusso",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "WatchScanner API",
        "version": "1.0.0",
        "mock_mode": settings.mock_mode,
        "docs": "/docs",
    }


@app.post("/scan", response_model=ScanResult)
async def scan_watch(query: WatchQuery):
    """
    Avvia una scansione completa per una referenza.
    Tutti gli agenti girano in parallelo e i risultati vengono aggregati.

    Esempio: POST /scan {"reference": "116610LN"}
    """
    if not query.reference.strip():
        raise HTTPException(status_code=400, detail="Reference non può essere vuota")
    result = await run_scan(query)

    # Auto-save snapshot + seed history if first time
    if result.listings:
        try:
            from analytics.market_engine import compute_market_stats
            from analytics.price_history import save_snapshot, seed_history_if_empty
            stats = compute_market_stats(result.listings)
            if stats.get("sample_size", 0) > 0:
                seeded = seed_history_if_empty(query.reference, stats["median_price"])
                if seeded:
                    logger.info(f"Storico sintetico generato: {seeded} mesi per {query.reference}")
                save_snapshot(query.reference, stats)
        except Exception as e:
            logger.debug(f"Snapshot save error: {e}")

    return result


@app.get("/agents/status", response_model=list[AgentStatus])
async def agents_status():
    """Stato di salute di tutti gli agenti."""
    return get_agents_status()


@app.post("/alerts", response_model=Alert)
async def create_alert(config: AlertConfig):
    """
    Crea un alert per una referenza sotto un certo prezzo.
    Quando trovata un'offerta sotto max_price, notifica via email/Telegram.
    """
    alert_id = str(uuid.uuid4())[:8]
    alert = Alert(
        alert_id=alert_id,
        config=config,
        created_at=datetime.now(),
        active=True,
    )
    _alerts[alert_id] = alert
    logger.info(f"Alert creato: {alert_id} | ref={config.reference} | max={config.max_price}€")
    return alert


@app.get("/alerts", response_model=list[Alert])
async def list_alerts():
    """Lista tutti gli alert attivi."""
    return list(_alerts.values())


@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert non trovato")
    del _alerts[alert_id]
    return {"deleted": alert_id}


@app.get("/discovery/status")
async def discovery_status():
    """Stato corrente della discovery e statistiche DB reseller."""
    from agents.discovery.orchestrator import get_state
    return get_state()


@app.post("/discovery/start")
async def start_discovery(background_tasks: BackgroundTasks):
    """
    Lancia manualmente la discovery su Instagram + Facebook + TikTok.
    Gira in background, controlla lo stato su GET /discovery/status.
    """
    from agents.discovery.orchestrator import get_state, run_full_discovery
    if get_state()["running"]:
        raise HTTPException(409, "Discovery già in esecuzione")

    background_tasks.add_task(
        run_full_discovery,
        settings.instagram_username,
        settings.instagram_password,
    )
    return {"status": "avviata", "check_status": "/discovery/status"}


@app.get("/resellers")
async def get_resellers(platform: str = None, min_score: int = 3):
    """Lista reseller scoperti, filtrabile per piattaforma e score minimo."""
    from agents.discovery.resellers_db import get_all_resellers, get_stats
    return {
        "stats": get_stats(),
        "resellers": get_all_resellers(min_score=min_score, platform=platform),
    }


@app.post("/analyze/{reference}")
async def analyze_reference_endpoint(reference: str):
    """Analizza una referenza: lancia scan + calcola market stats + deal scores."""
    reference = reference.strip()
    if not reference:
        raise HTTPException(status_code=400, detail="Reference non può essere vuota")

    logger.info(f"Avvio analisi referenza: {reference}")

    # 1. Lancia scan via orchestrator
    query = WatchQuery(reference=reference)
    scan_result = await run_scan(query)

    # 2. Calcola market stats
    market_stats = compute_market_stats(scan_result.listings)

    # 3. Salva snapshot storico
    if market_stats.get("sample_size", 0) > 0:
        saved = save_snapshot(reference, market_stats)
        logger.info(f"Snapshot storico {'salvato' if saved else 'già presente oggi'} per {reference}")

    # 4. Score tutti i listing
    scored_listings = score_all_listings(scan_result.listings, market_stats)

    # 5. Investment score
    investment = compute_investment_score(reference, market_stats, len(scan_result.listings))

    return {
        "reference": reference,
        "scan_id": scan_result.scan_id,
        "market_stats": market_stats,
        "investment": investment,
        "listings": scored_listings,
        "best_deal": scored_listings[0] if scored_listings else None,
        "total_found": scan_result.total_found,
        "agents_used": scan_result.agents_used,
        "duration_seconds": scan_result.duration_seconds,
        "analyzed_at": scan_result.scanned_at.isoformat(),
    }


@app.get("/market/{reference}")
async def get_market_stats(reference: str):
    """Market stats dalla cache o dal DB storico."""
    reference = reference.strip()
    from analytics.recommender import _cache as _rec_cache
    if reference in _rec_cache:
        cached = _rec_cache[reference].get("result", {})
        if cached:
            return {
                "reference": reference,
                "market_stats": cached.get("market_stats"),
                "investment": cached.get("investment"),
                "source": "cache",
            }

    # Fallback: recupera storico dal DB e ritorna l'ultimo snapshot
    history = get_history(reference, days=30)
    if not history:
        raise HTTPException(status_code=404, detail=f"Nessun dato di mercato trovato per {reference}. Esegui prima POST /analyze/{reference}")

    latest = history[-1]
    return {
        "reference": reference,
        "market_stats": latest,
        "source": "price_history_db",
        "snapshots_available": len(history),
    }


@app.get("/price-history/{reference}")
async def get_price_history(reference: str, days: int = 30):
    """Storico prezzi per una referenza."""
    reference = reference.strip()
    if days < 1 or days > 7300:
        raise HTTPException(status_code=400, detail="days deve essere tra 1 e 7300")

    history = get_history(reference, days=days)
    if not history:
        raise HTTPException(status_code=404, detail=f"Nessuno storico trovato per {reference}")

    return {
        "reference": reference,
        "days": days,
        "snapshots": history,
        "total": len(history),
    }


@app.get("/best-deals")
async def get_best_deals(min_discount: float = 0.05):
    """Listing con is_best_deal=True dalla cache recente."""
    from analytics.recommender import _cache as _rec_cache
    import time

    CACHE_TTL = 600
    best = []
    for reference, entry in _rec_cache.items():
        if (time.time() - entry.get("timestamp", 0)) > CACHE_TTL:
            continue
        result = entry.get("result", {})
        for listing in result.get("best_listings", []):
            if listing.get("is_best_deal") and listing.get("discount_pct", 0) >= min_discount:
                best.append({**listing, "reference": reference})

    best.sort(key=lambda x: x.get("deal_score", 0), reverse=True)
    return {
        "count": len(best),
        "min_discount": min_discount,
        "deals": best,
    }


@app.get("/recommendations")
async def get_recommendations_endpoint():
    """Top 3 referenze da comprare ora, basate sulla cache."""
    import time
    from analytics.recommender import _cache as _rec_cache

    CACHE_TTL = 600
    all_scan_results = []
    for reference, entry in _rec_cache.items():
        if (time.time() - entry.get("timestamp", 0)) > CACHE_TTL:
            continue
        result = entry.get("result", {})
        listings_raw = result.get("best_listings", [])
        if listings_raw:
            all_scan_results.append({"reference": reference, "listings": listings_raw})

    if not all_scan_results:
        return {
            "message": "Nessun dato in cache. Esegui prima POST /analyze/{reference} per alcune referenze.",
            "recommendations": [],
        }

    recommendations = await _get_recommendations(all_scan_results)
    _recommendations_cache["last_updated"] = datetime.now().isoformat()
    _recommendations_cache["data"] = recommendations

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "last_updated": _recommendations_cache.get("last_updated"),
    }


@app.post("/stories/setup")
async def setup_stories_auth(username: str, password: str):
    """
    Inizializza la sessione browser per lo scraping delle stories.
    Da chiamare una volta sola. Apre un browser Chrome visibile per il login.
    """
    from scrapers.stories.capture import save_auth_state, has_valid_auth
    if has_valid_auth():
        return {"status": "auth_already_present", "message": "Sessione già presente"}
    success = await save_auth_state(username, password)
    if success:
        return {"status": "ok", "message": "Login completato, sessione salvata"}
    raise HTTPException(status_code=400, detail="Login fallito — controlla credenziali o risolvi challenge")


@app.get("/stories/status")
async def stories_status():
    """Stato del sistema stories."""
    from scrapers.stories.capture import has_valid_auth, AUTH_STATE_FILE, SCREENSHOTS_DIR
    from scrapers.stories.storage import get_recent_stories
    recent = get_recent_stories(hours=48)
    return {
        "auth_ready": has_valid_auth(),
        "auth_file": str(AUTH_STATE_FILE),
        "recent_listings_48h": len(recent),
        "screenshots_dir": str(SCREENSHOTS_DIR),
    }


@app.post("/stories/run")
async def run_stories_now(accounts: list[str] | None = None):
    """Lancia manualmente un run della pipeline stories."""
    from scrapers.stories.pipeline import run_stories_pipeline
    results = await run_stories_pipeline(accounts=accounts)
    return {"listings_found": len(results), "results": results[:10]}


@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": settings.mock_mode}


@app.get("/catalog")
async def get_catalog(brand: str | None = None, search: str | None = None):
    """Catalogo orologi con immagini per ricerca visuale."""
    import json
    from pathlib import Path
    catalog_path = Path(__file__).parent / "catalog" / "watches.json"
    watches = json.loads(catalog_path.read_text())

    if brand:
        watches = [w for w in watches if w["brand"].lower() == brand.lower()]
    if search:
        s = search.lower()
        watches = [w for w in watches if
                   s in w["reference"].lower() or
                   s in w["model"].lower() or
                   s in w["brand"].lower() or
                   s in w["canonical_name"].lower()]

    brands = sorted(set(w["brand"] for w in json.loads(catalog_path.read_text())))
    return {"watches": watches, "total": len(watches), "brands": brands}


@app.get("/catalog/{watch_id}")
async def get_catalog_item(watch_id: str):
    """Dettaglio singolo orologio dal catalogo."""
    import json
    from pathlib import Path
    catalog_path = Path(__file__).parent / "catalog" / "watches.json"
    watches = json.loads(catalog_path.read_text())
    watch = next((w for w in watches if w["id"] == watch_id), None)
    if not watch:
        raise HTTPException(status_code=404, detail="Orologio non trovato nel catalogo")
    return watch


@app.post("/identify")
async def identify_watch_from_image(file: UploadFile = File(...)):
    """
    Identifica un orologio da una foto.
    Usa Claude Vision per riconoscere brand, modello e referenza.
    """
    import anthropic

    # Leggi immagine e converti in base64
    image_data = await file.read()
    image_b64 = base64.b64encode(image_data).decode("utf-8")

    # Determina media type
    content_type = file.content_type or "image/jpeg"
    if content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        content_type = "image/jpeg"

    try:
        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": content_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Analizza questa foto di un orologio e rispondi SOLO con un JSON valido (niente altro):
{
  "brand": "nome del brand (es. Rolex, Patek Philippe, Omega)",
  "model": "nome del modello (es. Submariner, Nautilus, Speedmaster)",
  "reference": "codice referenza se visibile (es. 116610LN, 5711/1A) oppure null",
  "year_estimate": "anno o range stimato (es. 2015-2020) oppure null",
  "confidence": 0.0-1.0,
  "notes": "altre info utili in max 20 parole"
}
Se non riesci a identificare un orologio, usa brand: null, confidence: 0."""
                        }
                    ],
                }
            ],
        )

        import json
        raw = message.content[0].text.strip()
        # Estrai JSON dalla risposta
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        result = json.loads(raw)

        return {
            "identified": result.get("confidence", 0) > 0.3,
            "brand": result.get("brand"),
            "model": result.get("model"),
            "reference": result.get("reference"),
            "year_estimate": result.get("year_estimate"),
            "confidence": result.get("confidence", 0),
            "notes": result.get("notes"),
        }

    except Exception as e:
        logger.error(f"Identify error: {e}")
        raise HTTPException(status_code=500, detail=f"Errore identificazione: {str(e)}")
