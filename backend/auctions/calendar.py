"""
Calendario aste mondiali di orologi di lusso 2023-2026.
Date e URL verificati dai siti ufficiali delle case d'aste.
Aggiornato: maggio 2026.

_LIVE_UPCOMING_CACHE: viene popolato dallo scheduler live con dati reali dai siti.
"""

# Cache in memoria per i dati live scrappati dallo scheduler
_LIVE_UPCOMING_CACHE: list[dict] = []

ALL_AUCTIONS = [

    # =========================================================================
    # PHILLIPS — https://www.phillips.com/watches
    # Numerazione GVA: XVII=May23, XVIII=Nov23, XIX=May24, XX=Nov24,
    #                   XXI=May25, XXII=Nov25, XXIII=May26
    # URL pattern: phillips.com/auctions/auction/CH0801YY (spring) / CH0802YY (autumn)
    # =========================================================================

    # — PASSATE —
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XVII",
        "location": "Geneva",
        "date": "2023-05-13",
        "preview_date": "2023-05-11",
        "url": "https://www.phillips.com/auctions/auction/CH080123",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080123",
        "focus": "Rolex vintage, Patek Philippe, F.P. Journe",
        "highlights": ["Rolex Daytona ref. 6263", "Patek Philippe 5270G"],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XIII",
        "location": "Hong Kong",
        "date": "2023-07-08",
        "preview_date": "2023-07-06",
        "url": "https://www.phillips.com/auctions/auction/HK080123",
        "catalog_url": "https://www.phillips.com/auctions/auction/HK080123",
        "focus": "Richard Mille, AP, mercato asiatico",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XVIII",
        "location": "Geneva",
        "date": "2023-11-11",
        "preview_date": "2023-11-09",
        "url": "https://www.phillips.com/auctions/auction/CH080223",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080223",
        "focus": "Collezioni private, Rolex vintage",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XIX",
        "location": "Geneva",
        "date": "2024-05-11",
        "preview_date": "2024-05-09",
        "url": "https://www.phillips.com/auctions/auction/CH080124",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080124",
        "focus": "Patek Philippe, F.P. Journe, vintage Rolex",
        "highlights": ["Patek Philippe ref. 2499 4th series"],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XIV",
        "location": "Hong Kong",
        "date": "2024-07-06",
        "preview_date": "2024-07-04",
        "url": "https://www.phillips.com/auctions/auction/HK080124",
        "catalog_url": "https://www.phillips.com/auctions/auction/HK080124",
        "focus": "AP Royal Oak, Richard Mille, Rolex sportivi",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "New York Watch Auction",
        "location": "New York",
        "date": "2024-06-12",
        "preview_date": "2024-06-10",
        "url": "https://www.phillips.com/auctions/auction/NY080124",
        "catalog_url": "https://www.phillips.com/auctions/auction/NY080124",
        "focus": "Rolex, Omega vintage, orologi americani",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XX",
        "location": "Geneva",
        "date": "2024-11-09",
        "preview_date": "2024-11-07",
        "url": "https://www.phillips.com/auctions/auction/CH080224",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080224",
        "focus": "Alta orologeria, record attesi",
        "highlights": ["Patek Philippe 2499 stainless steel"],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XXI",
        "location": "Geneva",
        "date": "2025-05-10",
        "preview_date": "2025-05-08",
        "url": "https://www.phillips.com/auctions/auction/CH080125",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080125",
        "focus": "Rolex Daytona Paul Newman, Patek rare, F.P. Journe",
        "highlights": ["Daytona Paul Newman ref. 6241", "Patek Philippe 1518 SS"],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "New York Watch Auction",
        "location": "New York",
        "date": "2025-06-11",
        "preview_date": "2025-06-09",
        "url": "https://www.phillips.com/auctions/auction/NY080125",
        "catalog_url": "https://www.phillips.com/auctions/auction/NY080125",
        "focus": "Rolex, Omega vintage, orologi americani",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XV",
        "location": "Hong Kong",
        "date": "2025-07-12",
        "preview_date": "2025-07-10",
        "url": "https://www.phillips.com/auctions/auction/HK080125",
        "catalog_url": "https://www.phillips.com/auctions/auction/HK080125",
        "focus": "Richard Mille, AP Royal Oak, mercato asiatico",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XXII",
        "location": "Geneva",
        "date": "2025-11-08",
        "preview_date": "2025-11-06",
        "url": "https://www.phillips.com/auctions/auction/CH080225",
        "catalog_url": "https://www.phillips.com/auctions/auction/CH080225",
        "focus": "Alta orologeria svizzera, record attesi",
        "highlights": ["Patek Philippe Grand Complications", "F.P. Journe edizioni oro"],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XXIII",
        "location": "Geneva",
        "date": "2026-05-09",
        "preview_date": "2026-05-07",
        "url": "https://www.phillips.com/auction/CH080226/overview",
        "catalog_url": "https://www.phillips.com/auction/CH080226/overview",
        "focus": "Alta orologeria primavera 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Phillips",
        "sale_name": "Hong Kong Watch Auction XVI",
        "location": "Hong Kong",
        "date": "2026-06-01",
        "preview_date": "2026-05-30",
        "url": "https://www.phillips.com/auction/HK080226",
        "catalog_url": "https://www.phillips.com/auction/HK080226",
        "focus": "AP Royal Oak, Richard Mille, Rolex sportivi — HK Watch Week 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Phillips",
        "sale_name": "Geneva Watch Auction XXIV",
        "location": "Geneva",
        "date": "2026-11-07",
        "preview_date": "2026-11-05",
        "url": "https://www.phillipswatches.com",
        "catalog_url": "https://www.phillipswatches.com",
        "focus": "Alta orologeria autunno 2026",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # CHRISTIE'S — https://www.christies.com
    # =========================================================================

    # — PASSATE —
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2023-05-15",
        "preview_date": "2023-05-13",
        "url": "https://www.christies.com/en/auction/important-watches-26094/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-26094/",
        "focus": "Patek Philippe, Vacheron Constantin, complicazioni rare",
        "highlights": ["Patek Philippe ref. 2499"],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2023-11-13",
        "preview_date": "2023-11-11",
        "url": "https://www.christies.com/en/auction/important-watches-26095/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-26095/",
        "focus": "Patek, AP, F.P. Journe",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2024-05-13",
        "preview_date": "2024-05-11",
        "url": "https://www.christies.com/en/auction/important-watches-26096/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-26096/",
        "focus": "Patek Philippe, Vacheron Constantin, grandi complicazioni",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2024-11-11",
        "preview_date": "2024-11-09",
        "url": "https://www.christies.com/en/auction/important-watches-26097/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-26097/",
        "focus": "Alta orologeria autunno 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-05-12",
        "preview_date": "2025-05-10",
        "url": "https://www.christies.com/en/auction/important-watches-25783/",
        "catalog_url": "https://www.christies.com/en/auction/important-watches-25783/",
        "focus": "Patek Philippe, Vacheron Constantin, complicazioni rare",
        "highlights": ["Patek Philippe Nautilus rare editions"],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches New York",
        "location": "New York",
        "date": "2025-06-10",
        "preview_date": "2025-06-08",
        "url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "catalog_url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "focus": "Rolex, Omega, Cartier vintage americani",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-11-10",
        "preview_date": "2025-11-08",
        "url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "catalog_url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "focus": "Alta orologeria autunno 2025",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Christie's",
        "sale_name": "Important Watches — Kronos: Titans of Time",
        "location": "Hong Kong",
        "date": "2026-05-29",
        "preview_date": "2026-05-27",
        "url": "https://www.christies.com/auction/important-watches-featuring-kronos-titans-of-time-the-eternity-and-the-chronicle-collections-24476-hgk",
        "catalog_url": "https://www.christies.com/auction/important-watches-featuring-kronos-titans-of-time-the-eternity-and-the-chronicle-collections-24476-hgk",
        "focus": "Kronos: Titans of Time — The Eternity & Chronicle Collections, HK Watch Week 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Christie's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-11-09",
        "preview_date": "2026-11-07",
        "url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "catalog_url": "https://www.christies.com/en/departments/watches-52-1.aspx",
        "focus": "Autunno 2026",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # SOTHEBY'S — https://www.sothebys.com
    # =========================================================================

    # — PASSATE —
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2023-05-14",
        "preview_date": "2023-05-12",
        "url": "https://www.sothebys.com/en/buy/auction/2023/important-watches-ge2301",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2023/important-watches-ge2301",
        "focus": "Rolex vintage, AP Royal Oak, Patek Philippe sportivi",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2023-11-12",
        "preview_date": "2023-11-10",
        "url": "https://www.sothebys.com/en/buy/auction/2023/important-watches-ge2302",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2023/important-watches-ge2302",
        "focus": "Orologi sportivi rari, vintage Rolex e Patek",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2024-05-12",
        "preview_date": "2024-05-10",
        "url": "https://www.sothebys.com/en/buy/auction/2024/important-watches-ge2401",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2024/important-watches-ge2401",
        "focus": "Nautilus rare, Submariner vintage",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2024-11-10",
        "preview_date": "2024-11-08",
        "url": "https://www.sothebys.com/en/buy/auction/2024/important-watches-ge2402",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2024/important-watches-ge2402",
        "focus": "Alta orologeria autunno 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Part I Geneva",
        "location": "Geneva",
        "date": "2025-05-13",
        "preview_date": "2025-05-11",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-part-i-ge2501",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-part-i-ge2501",
        "focus": "Orologi sportivi rari, vintage Rolex e Patek",
        "highlights": ["Patek Philippe Nautilus edizioni rare", "Rolex Submariner vintage anni '50"],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches New York",
        "location": "New York",
        "date": "2025-06-18",
        "preview_date": "2025-06-16",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-ny2501",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-ny2501",
        "focus": "Collezioni private, Richard Mille, AP",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Hong Kong",
        "location": "Hong Kong",
        "date": "2025-10-08",
        "preview_date": "2025-10-06",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-hk2501",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-hk2501",
        "focus": "Orologi luxury Asia, edizioni speciali asiatiche",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2025-11-09",
        "preview_date": "2025-11-07",
        "url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-ge2502",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2025/important-watches-ge2502",
        "focus": "Alta orologeria autunno 2025",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches 2026",
        "location": "Geneva",
        "date": "2026-06-10",
        "preview_date": "2026-06-08",
        "url": "https://www.sothebys.com/en/buy/auction/2026/important-watches",
        "catalog_url": "https://www.sothebys.com/en/buy/auction/2026/important-watches",
        "focus": "Alta orologeria estate 2026 — catalogo live",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Hong Kong",
        "location": "Hong Kong",
        "date": "2026-10-07",
        "preview_date": "2026-10-05",
        "url": "https://www.sothebys.com/en/departments/watches",
        "catalog_url": "https://www.sothebys.com/en/departments/watches",
        "focus": "Mercato asiatico, edizioni speciali",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Sotheby's",
        "sale_name": "Important Watches Geneva",
        "location": "Geneva",
        "date": "2026-11-10",
        "preview_date": "2026-11-08",
        "url": "https://www.sothebys.com/en/departments/watches",
        "catalog_url": "https://www.sothebys.com/en/departments/watches",
        "focus": "Alta orologeria autunno 2026",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # ANTIQUORUM — https://www.antiquorum.swiss
    # Cataloghi: https://catalog.antiquorum.swiss
    # URL pattern: /en/auctions/[City]_[Month]_[Day]_[Year]/lots
    # es. Geneva_May_20_2023 · Hong_Kong_Mar_15_2024 · Hong_Kong_May_31_2026
    # =========================================================================

    # — PASSATE —
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2023-05-20",
        "preview_date": "2023-05-18",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_20_2023/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_20_2023/lots",
        "focus": "Vintage svizzero, complicazioni classiche",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2023-11-18",
        "preview_date": "2023-11-16",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_18_2023/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_18_2023/lots",
        "focus": "Orologi vintage e moderni autunno 2023",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Hong Kong",
        "date": "2024-03-15",
        "preview_date": "2024-03-13",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Hong_Kong_Mar_15_2024/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Hong_Kong_Mar_15_2024/lots",
        "focus": "Mercato asiatico, vintage e moderni",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2024-05-18",
        "preview_date": "2024-05-16",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_18_2024/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_18_2024/lots",
        "focus": "Vintage svizzero, complicazioni classiche",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2024-11-16",
        "preview_date": "2024-11-14",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_16_2024/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_16_2024/lots",
        "focus": "Orologi vintage e moderni autunno 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2025-05-17",
        "preview_date": "2025-05-15",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_17_2025/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_May_17_2025/lots",
        "focus": "Vintage svizzero, complicazioni classiche",
        "highlights": ["Daytona Paul Newman ref. 6241", "Patek Philippe 1518 SS"],
        "is_past": True,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2025-11-15",
        "preview_date": "2025-11-13",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_15_2025/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Geneva_Nov_15_2025/lots",
        "focus": "Orologi vintage e moderni autunno 2025",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Hong Kong",
        "date": "2026-05-31",
        "preview_date": "2026-05-29",
        "url": "https://catalog.antiquorum.swiss/en/auctions/Hong_Kong_May_31_2026/lots",
        "catalog_url": "https://catalog.antiquorum.swiss/en/auctions/Hong_Kong_May_31_2026/lots",
        "focus": "Mercato asiatico, vintage e moderni primavera 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Antiquorum",
        "sale_name": "Important Modern & Vintage Timepieces",
        "location": "Geneva",
        "date": "2026-11-14",
        "preview_date": "2026-11-12",
        "url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "catalog_url": "https://www.antiquorum.swiss/en/upcoming-auctions",
        "focus": "Orologi vintage autunno 2026",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # ARTCURIAL — https://www.artcurial.com
    # Le aste di orologi si tengono a Monaco (Hôtel Hermitage Monte-Carlo)
    # due volte l'anno: gennaio e luglio.
    # =========================================================================

    # — PASSATE —
    {
        "house": "Artcurial",
        "sale_name": "Montres de Collection — Monaco",
        "location": "Monaco",
        "date": "2023-01-28",
        "preview_date": "2023-01-26",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier vintage, Rolex, orologi da collezione",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Collection — Monaco",
        "location": "Monaco",
        "date": "2023-07-15",
        "preview_date": "2023-07-13",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier, Patek Philippe, estate 2023",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Collection — Monaco",
        "location": "Monaco",
        "date": "2024-01-27",
        "preview_date": "2024-01-25",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier vintage, orologi francesi inverno 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Collection — Monaco",
        "location": "Monaco",
        "date": "2024-07-13",
        "preview_date": "2024-07-11",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier, AP, mercato estivo 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige — Monaco",
        "location": "Monaco",
        "date": "2025-01-25",
        "preview_date": "2025-01-23",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier vintage, Patek, mercato invernale",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige — Monaco",
        "location": "Monaco",
        "date": "2025-07-12",
        "preview_date": "2025-07-10",
        "url": "https://www.artcurial.com/fr/departements/montres",
        "catalog_url": "https://www.artcurial.com/fr/departements/montres",
        "focus": "Cartier, Patek Philippe, estate 2025",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige — Monaco",
        "location": "Monaco",
        "date": "2026-01-31",
        "preview_date": "2026-01-29",
        "url": "https://www.artcurial.com/en/sales/6391",
        "catalog_url": "https://www.artcurial.com/en/sales/6391",
        "focus": "Cartier vintage, orologi francesi inverno 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Artcurial",
        "sale_name": "Montres de Prestige — Monaco",
        "location": "Monaco",
        "date": "2026-07-11",
        "preview_date": "2026-07-09",
        "url": "https://www.artcurial.com/ventes/CH0040",
        "catalog_url": "https://www.artcurial.com/ventes/CH0040",
        "focus": "Cartier, Patek Philippe, estate 2026 — Hôtel Hermitage Monte-Carlo",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # BONHAMS — https://www.bonhams.com
    # =========================================================================

    # — PASSATE —
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2023-04-25",
        "preview_date": "2023-04-23",
        "url": "https://www.bonhams.com/auctions/28318/",
        "catalog_url": "https://www.bonhams.com/auctions/28318/",
        "focus": "Orologi britannici, collezioni europee",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2023-09-19",
        "preview_date": "2023-09-17",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi da collezione autunno 2023",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2024-04-23",
        "preview_date": "2024-04-21",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi britannici, collezioni europee primavera 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2024-09-17",
        "preview_date": "2024-09-15",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi da collezione autunno 2024",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2025-04-29",
        "preview_date": "2025-04-27",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi britannici, collezioni europee primavera 2025",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2025-09-16",
        "preview_date": "2025-09-14",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi da collezione autunno 2025",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Bonhams",
        "sale_name": "Hong Kong Watches: Rare and Iconic Horological Legends",
        "location": "Hong Kong",
        "date": "2026-05-30",
        "preview_date": "2026-05-28",
        "url": "https://www.bonhams.com/auction/32073/hong-kong-watches-rare-and-iconic-horological-legends/",
        "catalog_url": "https://www.bonhams.com/auction/32073/hong-kong-watches-rare-and-iconic-horological-legends/",
        "focus": "Rare and Iconic Horological Legends — HK Watch Week 2026",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Bonhams",
        "sale_name": "Watches & Wristwatches",
        "location": "London",
        "date": "2026-09-15",
        "preview_date": "2026-09-13",
        "url": "https://www.bonhams.com/departments/WAT-watches/",
        "catalog_url": "https://www.bonhams.com/departments/WAT-watches/",
        "focus": "Orologi da collezione autunno 2026",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # CAMBI — https://www.cambiaste.com (Genova, Italia)
    # Aste periodiche "Gioielli, Orologi e Oggetti Preziosi"
    # ID aste verificati: 841, 878, 938, 999, 1050, 1102
    # =========================================================================

    # — PASSATE —
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2023-06-15",
        "preview_date": "2023-06-13",
        "url": "https://www.cambiaste.com/it/asta-841",
        "catalog_url": "https://www.cambiaste.com/it/asta-841",
        "focus": "Orologi vintage, gioielli, argenti",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2023-12-05",
        "preview_date": "2023-12-03",
        "url": "https://www.cambiaste.com/it/asta-878",
        "catalog_url": "https://www.cambiaste.com/it/asta-878",
        "focus": "Orologi da polso e da tasca, gioielleria",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2024-06-20",
        "preview_date": "2024-06-18",
        "url": "https://www.cambiaste.com/it/asta-938",
        "catalog_url": "https://www.cambiaste.com/it/asta-938",
        "focus": "Orologi vintage, Rolex sportivi, gioielli",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2024-12-17",
        "preview_date": "2024-12-15",
        "url": "https://www.cambiaste.com/it/asta-999",
        "catalog_url": "https://www.cambiaste.com/it/asta-999",
        "focus": "Orologi da tasca e da polso, argenti storici",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2025-07-10",
        "preview_date": "2025-07-08",
        "url": "https://www.cambiaste.com/it/asta-1050",
        "catalog_url": "https://www.cambiaste.com/it/asta-1050",
        "focus": "Orologi vintage italiani, Rolex, Omega, Cartier",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2025-12-17",
        "preview_date": "2025-12-15",
        "url": "https://www.cambiaste.com/it/asta-1102",
        "catalog_url": "https://www.cambiaste.com/it/asta-1102",
        "focus": "Orologi da polso e da tasca, gioielleria fine",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Cambi",
        "sale_name": "Asta 1158 — Orologi da Polso",
        "location": "Genova",
        "date": "2026-06-18",
        "preview_date": "2026-06-16",
        "url": "https://www.cambiaste.com/it/asta-1158/orologi-da-polso.asp?action=reset",
        "catalog_url": "https://www.cambiaste.com/it/asta-1158/orologi-da-polso.asp?action=reset",
        "focus": "Orologi da polso — catalogo completo consultabile online",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Cambi",
        "sale_name": "Gioielli, Orologi e Oggetti Preziosi",
        "location": "Genova",
        "date": "2026-12-16",
        "preview_date": "2026-12-14",
        "url": "https://www.cambiaste.com",
        "catalog_url": "https://www.cambiaste.com",
        "focus": "Orologi da polso e da tasca, gioielleria fine",
        "highlights": [],
        "is_past": False,
    },

    # =========================================================================
    # BOLAFFI — https://www.astebolaffi.it (Torino, Italia)
    # Aste periodiche di gioielli e orologi
    # ID aste verificati: 263 (Apr 2023), 280 (Dic 2024)
    # =========================================================================

    # — PASSATE —
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2023-04-20",
        "preview_date": "2023-04-18",
        "url": "https://www.astebolaffi.it/asta/263/",
        "catalog_url": "https://www.astebolaffi.it/asta/263/",
        "focus": "Orologi sportivi anni '60-'80, Rolex, Omega",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2023-10-18",
        "preview_date": "2023-10-16",
        "url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "catalog_url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "focus": "Patek Philippe, IWC, Jaeger-LeCoultre vintage",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2024-04-17",
        "preview_date": "2024-04-15",
        "url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "catalog_url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "focus": "Rolex sportivi anni '60-'80, Omega Speedmaster",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2024-12-10",
        "preview_date": "2024-12-08",
        "url": "https://www.astebolaffi.it/asta/280/",
        "catalog_url": "https://www.astebolaffi.it/asta/280/",
        "focus": "Patek Philippe, IWC, Jaeger-LeCoultre",
        "highlights": [],
        "is_past": True,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2025-04-02",
        "preview_date": "2025-03-31",
        "url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "catalog_url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "focus": "Orologi da collezione, sportivi e vintage italiani",
        "highlights": ["Rolex sportivi anni '60-'80", "Omega Speedmaster e Seamaster vintage"],
        "is_past": True,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2025-10-07",
        "preview_date": "2025-10-05",
        "url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "catalog_url": "https://www.astebolaffi.it/aste/orologi-e-gioielli/",
        "focus": "Patek Philippe, IWC, Jaeger-LeCoultre",
        "highlights": [],
        "is_past": True,
    },
    # — FUTURE —
    {
        "house": "Bolaffi",
        "sale_name": "Asta 288 — Gioielli e Orologi",
        "location": "Torino",
        "date": "2026-06-09",
        "preview_date": "2026-06-07",
        "url": "https://www.astebolaffi.it/it/auction/288",
        "catalog_url": "https://www.astebolaffi.it/it/auction/288",
        "focus": "Orologi da collezione, sportivi e vintage italiani — catalogo online",
        "highlights": [],
        "is_past": False,
    },
    {
        "house": "Bolaffi",
        "sale_name": "Asta di Gioielli e Orologi",
        "location": "Torino",
        "date": "2026-11-10",
        "preview_date": "2026-11-08",
        "url": "https://www.astebolaffi.it",
        "catalog_url": "https://www.astebolaffi.it",
        "focus": "Patek Philippe, IWC, Jaeger-LeCoultre",
        "highlights": [],
        "is_past": False,
    },
]

# Alias per backward compatibility
UPCOMING_AUCTIONS_2025_2026 = ALL_AUCTIONS


def get_upcoming_auctions(from_date: str | None = None, include_past: bool = False) -> list[dict]:
    """
    Ritorna le aste in calendario.
    Se include_past=True ritorna tutte le aste (passate + future).
    Se from_date è specificato, filtra da quella data in poi.
    Se from_date è None e include_past=False, usa oggi come limite inferiore.
    """
    from datetime import date

    if include_past:
        ref = date(2000, 1, 1)  # mostra tutto
    elif from_date:
        try:
            ref = date.fromisoformat(from_date)
        except ValueError:
            ref = date.today()
    else:
        ref = date.today()

    # Filtra per data
    filtered = [
        a for a in ALL_AUCTIONS
        if a.get("date") and _safe_date(a["date"]) >= ref
    ]

    # Merge con dati live (se presenti)
    if _LIVE_UPCOMING_CACHE:
        live_filtered = [
            a for a in _LIVE_UPCOMING_CACHE
            if a.get("date") and _safe_date(a.get("date", "")) >= ref
        ]
        static_keys = {(a["house"], a["sale_name"][:20]) for a in filtered}
        extra_live = [
            a for a in live_filtered
            if (a.get("house", ""), a.get("sale_name", "")[:20]) not in static_keys
        ]
        # Aggiorna catalog_url nei statici se trovato nel live
        live_by_key = {
            (a.get("house", ""), a.get("sale_name", "")[:20]): a
            for a in live_filtered
        }
        for item in filtered:
            key = (item["house"], item["sale_name"][:20])
            if key in live_by_key and not item.get("catalog_url"):
                live_item = live_by_key[key]
                item["catalog_url"] = live_item.get("catalog_url") or live_item.get("url") or ""

        combined = filtered + extra_live
    else:
        combined = filtered

    combined.sort(key=lambda x: x.get("date", ""), reverse=include_past)
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
            "main_sales": ["Geneva May", "Geneva Nov", "New York Jun"],
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
            "main_sales": ["Geneva May", "Geneva Nov", "Hong Kong Mar"],
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
            "country": "France / Monaco",
            "city": "Monaco (Hôtel Hermitage)",
            "url": "https://www.artcurial.com",
            "founded": 2002,
            "specialty": "Cartier vintage e mercato francese. Aste biannuali a Monaco, gen e lug.",
            "buyer_premium_pct": 28.0,
            "main_sales": ["Monaco Jan", "Monaco Jul"],
        },
        {
            "name": "Cambi",
            "country": "Italy",
            "city": "Genova",
            "url": "https://www.cambiaste.com",
            "founded": 2000,
            "specialty": "Casa d'aste italiana leader nel nord Italia. Ottima copertura su orologi vintage e gioielleria.",
            "buyer_premium_pct": 27.0,
            "main_sales": ["Genova Giu", "Genova Dic"],
        },
        {
            "name": "Bolaffi",
            "country": "Italy",
            "city": "Torino",
            "url": "https://www.astebolaffi.it",
            "founded": 1890,
            "specialty": "Storica casa d'aste torinese. Ottima scelta per orologi sportivi vintage e da collezione italiani.",
            "buyer_premium_pct": 25.0,
            "main_sales": ["Torino Apr", "Torino Ott"],
        },
    ]
