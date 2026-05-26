"""
Calendario aste mondiali di orologi di lusso 2025-2026.
Dati aggiornati a conoscenza maggio 2026.

_LIVE_UPCOMING_CACHE: viene popolato dallo scheduler live con dati reali dai siti.
"""

# Cache in memoria per i dati live scrappati dallo scheduler
_LIVE_UPCOMING_CACHE: list[dict] = []

UPCOMING_AUCTIONS_2025_2026 = [
    # =========================================================================
    # PHILLIPS
    # =========================================================================
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XVIII",
        "location": "Geneva",
        "date": "2025-05-10",
        "preview_date": "2025-05-08",
        "url": "https://www.phillipswatches.com/auction/GVA18/",
        "catalog_url": "https://www.phillipswatches.com/auction/GVA18/",
        "focus": "Vintage Rolex, Patek Philippe rare, F.P. Journe",
        "highlights": [
            "Daytona Paul Newman referenze storiche",
            "Patek Philippe in platino",
            "Collezione privata europea",
        ],
    },
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XVI",
        "location": "Hong Kong",
        "date": "2025-07-12",
        "preview_date": "2025-07-10",
        "url": "https://www.phillipswatches.com/auction/HK16/",
        "catalog_url": "https://www.phillipswatches.com/auction/HK16/",
        "focus": "Richard Mille, AP Royal Oak, mercato asiatico",
        "highlights": [
            "Richard Mille Tourbillon edizioni speciali",
            "Audemars Piguet Royal Oak A-series",
        ],
    },
    {
        "house": "Phillips",
        "sale_name": "New York Watch Auction",
        "location": "New York",
        "date": "2025-06-11",
        "preview_date": "2025-06-09",
        "url": "https://www.phillipswatches.com/auction/NY202506/",
        "catalog_url": "https://www.phillipswatches.com/auction/NY202506/",
        "focus": "Orologi americani, Rolex sportivi, Omega vintage",
        "highlights": [
            "Speedmaster da collezione",
            "Rolex Submariner e GMT Master vintage",
        ],
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XIX",
        "location": "Geneva",
        "date": "2025-11-08",
        "preview_date": "2025-11-06",
        "url": "https://www.phillipswatches.com/auction/GVA19/",
        "catalog_url": "https://www.phillipswatches.com/auction/GVA19/",
        "focus": "Alta orologeria svizzera, record attesi",
        "highlights": [
            "Patek Philippe Grand Complications",
            "F.P. Journe edizioni in oro",
            "Rolex Daytona vintage",
        ],
    },

    # =========================================================================
    # CHRISTIE'S
    # =========================================================================
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-05-12",
        "preview_date": "2025-05-10",
        "url": "https://www.christies.com/en/auction/important-watches-25783/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-25783/",
        "focus": "Patek Philippe, Vacheron Constantin, complicazioni rare",
        "highlights": [
            "Patek Philippe Ref. 2499 e precedenti",
            "Vacheron Constantin edizioni speciali",
        ],
    },
    {
        "house": "Christie's",
        "sale_name": "Watches Online",
        "location": "Online",
        "date": "2025-06-25",
        "preview_date": None,
        "url": "https://www.christies.com/en/auction/watches-online-25900/",
        "catalog_url": "https://www.christies.com/en/auction/watches-online-25900/",
        "focus": "Orologi lusso accessibili, acciaio sportivo",
        "highlights": [],
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches New York",
        "location": "New York",
        "date": "2025-12-10",
        "preview_date": "2025-12-08",
        "url": "https://www.christies.com/en/auction/important-watches-new-york-26100/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-new-york-26100/",
        "focus": "Collezioni americane, Rolex, Omega, Cartier vintage",
        "highlights": [
            "Rolex Daytona Paul Newman referenze",
            "Cartier vintage anni '70",
        ],
    },

    # =========================================================================
    # SOTHEBY'S
    # =========================================================================
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-05-13",
        "preview_date": "2025-05-11",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches",
        "focus": "Orologi sportivi rari, vintage Rolex e Patek",
        "highlights": [
            "Patek Philippe Nautilus edizioni rare",
            "Rolex Submariner vintage anni '50",
        ],
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches New York",
        "location": "New York",
        "date": "2025-06-18",
        "preview_date": "2025-06-16",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-new-york",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-new-york",
        "focus": "Collezioni private, Richard Mille, AP",
        "highlights": [],
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Hong Kong",
        "location": "Hong Kong",
        "date": "2025-10-08",
        "preview_date": "2025-10-06",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-hong-kong",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-hong-kong",
        "focus": "Orologi luxury Asia, edizioni speciali asiatiche",
        "highlights": [],
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-11-10",
        "preview_date": "2025-11-08",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-november",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-november",
        "focus": "Alta orologeria, records attesi",
        "highlights": [
            "Grandi complicazioni Patek Philippe",
            "F.P. Journe in metalli pregiati",
        ],
    },

    # =========================================================================
    # ANTIQUORUM
    # =========================================================================
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2025-05-11",
        "preview_date": "2025-05-09",
        "url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "catalog_url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "focus": "Vintage svizzero, Rolex anni '50-'70, complicazioni classiche",
        "highlights": [
            "Rolex Submariner e GMT Master prima generazione",
            "Patek Philippe vintage anni '60",
        ],
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Watches",
        "location": "Geneva",
        "date": "2025-11-08",
        "preview_date": "2025-11-06",
        "url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "catalog_url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "focus": "Orologi vintage e moderni, aste serali",
        "highlights": [],
    },

    # =========================================================================
    # BONHAMS
    # =========================================================================
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2025-04-29",
        "preview_date": "2025-04-27",
        "url": "https://www.bonhams.com/auctions/",
        "catalog_url": "https://www.bonhams.com/auctions/",
        "focus": "Orologi britannici, collezioni europee",
        "highlights": [
            "Cronografi vintage inglesi",
            "Rolex acciaio sportivi",
        ],
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2025-09-16",
        "preview_date": "2025-09-14",
        "url": "https://www.bonhams.com/auctions/",
        "catalog_url": "https://www.bonhams.com/auctions/",
        "focus": "Orologi da collezione, accesso al mercato europeo",
        "highlights": [],
    },

    # =========================================================================
    # ARTCURIAL
    # =========================================================================
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige",
        "location": "Paris",
        "date": "2025-06-10",
        "preview_date": "2025-06-08",
        "url": "https://www.artcurial.com/en/watches",
        "catalog_url": "https://www.artcurial.com/en/watches",
        "focus": "Cartier vintage, orologi francesi, mercato europeo",
        "highlights": [
            "Cartier vintage anni '60-'70",
            "Chronographes français rarissimi",
        ],
    },
    {
        "house": "Artcurial",
        "sale_name": "Automobiles et Montres de Prestige",
        "location": "Paris",
        "date": "2025-12-09",
        "preview_date": "2025-12-07",
        "url": "https://www.artcurial.com/en/watches",
        "catalog_url": "https://www.artcurial.com/en/watches",
        "focus": "Cartier, Patek Philippe, mercato invernale parigino",
        "highlights": [],
    },

    # =========================================================================
    # 2026 — calendari confermati / attesi
    # =========================================================================

    # Phillips Spring Geneva 2026
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XX",
        "location": "Geneva",
        "date": "2026-05-09",
        "preview_date": "2026-05-07",
        "url": "https://www.phillipswatches.com/auctions/",
        "catalog_url": "",
        "focus": "Asta principale spring Geneva 2026",
        "highlights": [],
    },
    # Phillips Hong Kong 2026
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XVII",
        "location": "Hong Kong",
        "date": "2026-07-11",
        "preview_date": "2026-07-09",
        "url": "https://www.phillipswatches.com/auctions/",
        "catalog_url": "",
        "focus": "Mercato asiatico, Richard Mille, AP Royal Oak",
        "highlights": [],
    },
    # Phillips Autumn Geneva 2026
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XXI",
        "location": "Geneva",
        "date": "2026-11-07",
        "preview_date": "2026-11-05",
        "url": "https://www.phillipswatches.com/auctions/",
        "catalog_url": "",
        "focus": "Asta autunnale Geneva 2026, alta orologeria",
        "highlights": [],
    },

    # Christie's Spring Geneva 2026
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-05-11",
        "preview_date": "2026-05-09",
        "url": "https://www.christies.com/en/calendar",
        "catalog_url": "",
        "focus": "Alta orologeria primavera 2026",
        "highlights": [],
    },
    # Christie's Autumn Geneva 2026
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-11-09",
        "preview_date": "2026-11-07",
        "url": "https://www.christies.com/en/calendar",
        "catalog_url": "",
        "focus": "Alta orologeria autunno 2026",
        "highlights": [],
    },
    # Christie's New York 2026
    {
        "house": "Christie's",
        "sale_name": "Important Watches New York",
        "location": "New York",
        "date": "2026-12-09",
        "preview_date": "2026-12-07",
        "url": "https://www.christies.com/en/calendar",
        "catalog_url": "",
        "focus": "Collezioni americane, mercato invernale 2026",
        "highlights": [],
    },

    # Sotheby's Spring Geneva 2026
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-05-12",
        "preview_date": "2026-05-10",
        "url": "https://www.sothebys.com/en/calendar",
        "catalog_url": "",
        "focus": "Asta Geneva spring 2026",
        "highlights": [],
    },
    # Sotheby's Hong Kong 2026
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Hong Kong",
        "location": "Hong Kong",
        "date": "2026-10-07",
        "preview_date": "2026-10-05",
        "url": "https://www.sothebys.com/en/calendar",
        "catalog_url": "",
        "focus": "Mercato asiatico, edizioni speciali",
        "highlights": [],
    },
    # Sotheby's Autumn Geneva 2026
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-11-10",
        "preview_date": "2026-11-08",
        "url": "https://www.sothebys.com/en/calendar",
        "catalog_url": "",
        "focus": "Alta orologeria autunno 2026",
        "highlights": [],
    },

    # Antiquorum May 2026
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2026-05-10",
        "preview_date": "2026-05-08",
        "url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "catalog_url": "",
        "focus": "Vintage svizzero, complicazioni classiche",
        "highlights": [],
    },
    # Antiquorum November 2026
    {
        "house": "Antiquorum",
        "sale_name": "Important Watches",
        "location": "Geneva",
        "date": "2026-11-08",
        "preview_date": "2026-11-06",
        "url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "catalog_url": "",
        "focus": "Orologi vintage e moderni",
        "highlights": [],
    },

    # Bonhams Spring London 2026
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2026-04-28",
        "preview_date": "2026-04-26",
        "url": "https://www.bonhams.com/auctions/",
        "catalog_url": "",
        "focus": "Orologi britannici, collezioni europee",
        "highlights": [],
    },
    # Bonhams Autumn London 2026
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2026-09-15",
        "preview_date": "2026-09-13",
        "url": "https://www.bonhams.com/auctions/",
        "catalog_url": "",
        "focus": "Orologi da collezione",
        "highlights": [],
    },

    # Artcurial Paris June 2026
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige",
        "location": "Paris",
        "date": "2026-06-09",
        "preview_date": "2026-06-07",
        "url": "https://www.artcurial.com/en/watches",
        "catalog_url": "",
        "focus": "Cartier vintage, orologi francesi",
        "highlights": [],
    },
    # Artcurial Paris December 2026
    {
        "house": "Artcurial",
        "sale_name": "Automobiles et Montres de Prestige",
        "location": "Paris",
        "date": "2026-12-08",
        "preview_date": "2026-12-06",
        "url": "https://www.artcurial.com/en/watches",
        "catalog_url": "",
        "focus": "Cartier, Patek Philippe, mercato invernale parigino",
        "highlights": [],
    },
]


def get_upcoming_auctions(from_date: str | None = None) -> list[dict]:
    """
    Ritorna le aste in calendario a partire da from_date (ISO string).
    Mergia dati statici con dati live dal cache dello scheduler (se disponibili).
    Se from_date è None, usa oggi.
    """
    from datetime import date

    if from_date:
        try:
            ref = date.fromisoformat(from_date)
        except ValueError:
            ref = date.today()
    else:
        ref = date.today()

    # Dati statici filtrati per data
    static_upcoming = [
        a for a in UPCOMING_AUCTIONS_2025_2026
        if a.get("date") and _safe_date(a["date"]) >= ref
    ]

    # Merge con dati live (se presenti)
    if _LIVE_UPCOMING_CACHE:
        live_upcoming = [
            a for a in _LIVE_UPCOMING_CACHE
            if a.get("date") and _safe_date(a.get("date", "")) >= ref
        ]

        # Dedup: i dati live sovrascrivono quelli statici per (house, sale_name simile)
        # Mantieni solo i live che non sono già nei statici
        static_keys = {(a["house"], a["sale_name"][:20]) for a in static_upcoming}
        extra_live = [
            a for a in live_upcoming
            if (a.get("house", ""), a.get("sale_name", "")[:20]) not in static_keys
        ]

        # Aggiorna catalog_url nei statici se trovato nel live
        live_by_key = {
            (a.get("house", ""), a.get("sale_name", "")[:20]): a
            for a in live_upcoming
        }
        for item in static_upcoming:
            key = (item["house"], item["sale_name"][:20])
            if key in live_by_key and not item.get("catalog_url"):
                live_item = live_by_key[key]
                item["catalog_url"] = live_item.get("catalog_url") or live_item.get("url") or ""

        combined = static_upcoming + extra_live
    else:
        combined = static_upcoming

    combined.sort(key=lambda x: x.get("date", ""))
    return combined


def _safe_date(date_str: str):
    """Parsa una data ISO senza lanciare eccezioni."""
    from datetime import date
    try:
        return date.fromisoformat(date_str[:10])
    except (ValueError, TypeError):
        return date(9999, 12, 31)


def get_auction_houses_info() -> list[dict]:
    """Informazioni di base sulle principali case d'aste."""
    return [
        {
            "name": "Phillips",
            "country": "Switzerland",
            "city": "Geneva",
            "url": "https://www.phillipswatches.com",
            "founded": 1796,
            "specialty": "Orologi contemporanei e vintage di altissimo livello. Record mondiali frequenti.",
            "buyer_premium_pct": 26.0,
            "main_sales": ["Spring Geneva", "Autumn Geneva", "Hong Kong", "New York"],
        },
        {
            "name": "Christie's",
            "country": "UK / Switzerland",
            "city": "London / Geneva",
            "url": "https://www.christies.com",
            "founded": 1766,
            "specialty": "Arte e orologi di lusso. Forte in Patek Philippe e grandi complicazioni.",
            "buyer_premium_pct": 26.0,
            "main_sales": ["Geneva May", "Geneva Nov", "New York Dec"],
        },
        {
            "name": "Sotheby's",
            "country": "UK / Switzerland",
            "city": "London / Geneva",
            "url": "https://www.sothebys.com",
            "founded": 1744,
            "specialty": "Orologi sportivi vintage e alta orologeria. Forte in Rolex e AP.",
            "buyer_premium_pct": 26.0,
            "main_sales": ["Geneva May", "Geneva Nov", "New York", "Hong Kong"],
        },
        {
            "name": "Antiquorum",
            "country": "Switzerland",
            "city": "Geneva",
            "url": "https://www.antiquorum.swiss",
            "founded": 1974,
            "specialty": "Specialista storico in orologeria svizzera vintage. Grande expertise tecnica.",
            "buyer_premium_pct": 26.0,
            "main_sales": ["Geneva May", "Geneva Nov"],
        },
        {
            "name": "Bonhams",
            "country": "UK",
            "city": "London",
            "url": "https://www.bonhams.com",
            "founded": 1793,
            "specialty": "Orologi britannici e europei. Commissioni competitive, ottima accessibilità.",
            "buyer_premium_pct": 26.0,
            "main_sales": ["London Apr", "London Sep"],
        },
        {
            "name": "Artcurial",
            "country": "France",
            "city": "Paris",
            "url": "https://www.artcurial.com",
            "founded": 2002,
            "specialty": "Cartier vintage e mercato parigino. Spesso trova lotti a prezzi competitivi.",
            "buyer_premium_pct": 28.0,
            "main_sales": ["Paris Jun", "Paris Dec"],
        },
    ]
