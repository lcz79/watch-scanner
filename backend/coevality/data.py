"""
Dati di coevità — curati da fonti autorevoli, con livello di confidenza.
Pilota: Rolex Daytona "Zenith" ref. 16520 (produzione 1988-2000).

Fonti principali:
  - Blackbird Watch Manual — "The Rolex Daytona Reference 16520"
  - Bob's Watches — Rolex Serial Numbers & Production Dates

NB: la coevità funziona sui Rolex con SERIALE SEQUENZIALE (lettera + cifre),
in uso fino a ~2010. I dati sono il consenso dei collezionisti: il seriale dà
un anno con tolleranza di ±1-2 anni (i componenti potevano essere a magazzino).
"""

SOURCES = {
    "blackbird": {
        "name": "Blackbird Watch Manual — Rolex Daytona 16520",
        "url": "https://www.blackbird-watchmanual.com/manual/icons/the-rolex-daytona-reference-16520/",
    },
    "bobs": {
        "name": "Bob's Watches — Rolex Serial Numbers",
        "url": "https://www.bobswatches.com/rolex-serial-numbers",
    },
    "iws": {
        "name": "Italian Watch Spotter — Guida ai Daytona vintage 4 cifre",
        "url": "https://italianwatchspotter.com/vintage-rolex-daytonas-guide/?lang=en",
    },
    "goldammer": {
        "name": "Goldammer — Reference Guide: early Rolex Daytona (1963-88)",
        "url": "https://goldammer.me/blogs/articles/reference-guide-rolex-daytona",
    },
    "subref": {
        "name": "Professional Watches — Submariner Reference Guide",
        "url": "https://professionalwatches.com/rolex-submariner-reference-guide/",
    },
    "mono_sub": {
        "name": "Monochrome — Submariner, le referenze a 5 cifre",
        "url": "https://monochrome-watches.com/rolex-submariner-history-part-3-the-5-digit-references/",
    },
    "gmt_fratello": {
        "name": "Fratello — Rolex GMT-Master History",
        "url": "https://www.fratellowatches.com/fasten-your-seatbelts-rolex-gmt-master-history/",
    },
    "gmt_wind": {
        "name": "Wind Vintage — Collector's Guide: GMT-Master 1675",
        "url": "https://www.windvintage.com/blog/collectors-guide-the-rolex-gmt-master-reference-1675-in-steel",
    },
    "mono_explorer": {
        "name": "Monochrome — History of the Rolex Explorer",
        "url": "https://monochrome-watches.com/history-rolex-explorer-from-1953-36mm-1016-14270-114270-214270-124270-in-depth-review/",
    },
    "mono_explorer2": {
        "name": "Monochrome — History of the Rolex Explorer II",
        "url": "https://monochrome-watches.com/history-rolex-explorer-ii-adventure-watch-gmt-1655-16550-16570-216570-226570-in-depth/",
    },
    "mono_dj": {
        "name": "Monochrome — The History of the Rolex Datejust",
        "url": "https://monochrome-watches.com/rolex-datejust-complete-history/",
    },
    "mono_milgauss": {
        "name": "Monochrome — The Complete History of the Rolex Milgauss",
        "url": "https://monochrome-watches.com/history-rolex-milgauss-collection-in-depth-review/",
    },
}

# --- Seriale (lettera iniziale) → anno di produzione (range, consenso) --------
# Rolex passò ai prefissi-lettera nel 1987 (R, L, E, X = "ROLEX" senza la O...).
SERIAL_YEAR: dict[str, tuple[int, int]] = {
    "R": (1987, 1988),
    "L": (1988, 1990),
    "E": (1990, 1991),
    "X": (1991, 1991),
    "N": (1991, 1991),
    "C": (1992, 1992),
    "S": (1993, 1994),
    "W": (1994, 1995),
    "T": (1995, 1996),
    "U": (1997, 1998),
    "A": (1998, 1999),
    "P": (2000, 2000),
    "K": (2000, 2001),
    # Anni 2000 (per referenze come 116520, fino ai seriali casuali ~2010)
    "Y": (2002, 2003),
    "F": (2003, 2004),
    "D": (2005, 2006),
    "Z": (2006, 2007),
    "M": (2007, 2008),
    "V": (2008, 2009),
    "G": (2010, 2010),
}

# Lettere mai usate da Rolex su orologi (riservate a Tudor o non emesse).
SERIAL_NEVER_USED = set("BIJOQ")

# --- Seriale NUMERICO (pre-1987) → anno: (seriale iniziale, anno) ordinati ----
# Per i Daytona vintage (6239/6263/6265). Fonte: Bob's Watches.
# NB: nel 1976-77 Rolex saltò da ~4,15M a ~5,0M (range 4,3-4,8M riservato ai
# ricambi di servizio). Tolleranza ±1-2 anni.
NUMERIC_SERIAL: list[tuple[int, int]] = [
    (516000, 1960), (643000, 1961), (744000, 1962), (824000, 1963),
    (1008000, 1964), (1100000, 1965), (1200000, 1966), (1538000, 1967),
    (1752000, 1968), (1900000, 1969), (2241000, 1970), (2589000, 1971),
    (2890000, 1972), (3200000, 1973), (3567000, 1974), (3862000, 1975),
    (4115000, 1976), (5000000, 1977), (5400000, 1978), (5737000, 1979),
    (6434000, 1980), (6850000, 1981), (7100000, 1982), (7400000, 1983),
    (8070000, 1984), (8614000, 1985), (8900000, 1986), (9400000, 1987),
]


def _v(label, description, yf, yt, conf):
    return {"label": label, "description": description,
            "year_from": yf, "year_to": yt, "confidence": conf}


# --- Componenti per referenza -------------------------------------------------
REFERENCES: dict[str, dict] = {
    "16520": {
        "model": "Rolex Cosmograph Daytona \"Zenith\"",
        "production_from": 1988,
        "production_to": 2000,
        "components": [
            {
                "component": "Quadrante",
                "icon": "radio_button_checked",
                "sources": ["blackbird"],
                "note": "I 'Mark' del quadrante sono il dato di coevità più studiato del 16520.",
                "variants": [
                    _v("Mark 1 — Floating", "Quadrante Singer con 'Cosmograph' staccato (floating). Tritio.", 1988, 1988, "alta"),
                    _v("Mark 2 — Quattro righe", "Testo a quattro righe, omette 'Officially Certified'. Configurazione rara. Tritio.", 1989, 1990, "alta"),
                    _v("Mark 3 — Inverted 6", "Il 6 del contatore in basso è invertito (sembra un 9 al polso). Tritio.", 1990, 1993, "alta"),
                    _v("Mark 4", "Cifra 6 corretta, font più marcato e moderno. Possibili quadranti 'Patrizzi'/tropical (anelli contatori bruniti). Tritio.", 1993, 1998, "alta"),
                    _v("Luminova — Swiss Made", "Passaggio da tritio a Luminova: marcatura 'Swiss Made' al posto di 'T Swiss Made T'.", 1998, 2000, "alta"),
                ],
            },
            {
                "component": "Ghiera (scala tachimetrica)",
                "icon": "lens",
                "sources": ["blackbird"],
                "note": None,
                "variants": [
                    _v("Scala 200 unità", "Ghiera transitoria, scala per 200 unità, 'unit per hour' a ore 3.", 1988, 1988, "alta"),
                    _v("Scala 400 (250/225)", "Scala per 400 unità con indicazioni 250 e 225, 'units per hour' a ore 1.", 1989, 1990, "alta"),
                    _v("Scala 400 (240)", "Marcatura per 400 unità cambiata in 240.", 1990, 2000, "alta"),
                ],
            },
            {
                "component": "Bracciale",
                "icon": "watch",
                "sources": ["blackbird"],
                "note": "Riferimento e finitura del bracciale Oyster.",
                "variants": [
                    _v("78360", "Finitura interamente spazzolata.", 1988, 1991, "alta"),
                    _v("78390", "Maglie centrali lucide.", 1991, 1998, "alta"),
                    _v("78390A — SEL", "Terminali solidi (Solid End Links).", 1998, 2000, "alta"),
                ],
            },
            {
                "component": "Terminali (end links)",
                "icon": "link",
                "sources": ["blackbird"],
                "note": "Coerenti col bracciale dell'anno.",
                "variants": [
                    _v("Terminali cavi (hollow)", "Terminali stampati/cavi, tipici dei bracciali 78360/78390.", 1988, 1998, "media"),
                    _v("Terminali solidi (SEL)", "Solid End Links, introdotti col 78390A.", 1998, 2000, "alta"),
                ],
            },
            {
                "component": "Materiale luminescente",
                "icon": "light_mode",
                "sources": ["blackbird"],
                "note": None,
                "variants": [
                    _v("Tritio — 'T Swiss Made T'", "Indici e lancette al tritio; dicitura 'T Swiss Made T' sul quadrante.", 1988, 1998, "alta"),
                    _v("Luminova — 'Swiss Made'", "Passaggio a Luminova; dicitura 'Swiss Made'.", 1998, 2000, "alta"),
                ],
            },
            {
                "component": "Calibro",
                "icon": "settings",
                "sources": ["blackbird"],
                "note": "Tutta la produzione 16520 monta lo stesso calibro.",
                "variants": [
                    _v("Cal. 4030 (base Zenith El Primero 400)", "Oltre metà componenti sostituiti da Rolex; 28.800 alt/h, bilanciere Glucydur, spirale Breguet, senza datario.", 1988, 2000, "alta"),
                ],
            },
            {
                "component": "Fondello (marcatura interna)",
                "icon": "album",
                "sources": ["blackbird"],
                "note": "Stampigliatura interna del fondello.",
                "variants": [
                    _v("Interno 16500", "Fondello stampigliato internamente 16500.", 1988, 1999, "alta"),
                    _v("Interno 2100", "Fondello stampigliato internamente 2100 (ultima serie).", 2000, 2000, "media"),
                ],
            },
            {
                "component": "Garanzia / Documenti",
                "icon": "description",
                "sources": ["bobs"],
                "note": "Dato meno preciso per anno: verificare codici e datazione sul documento originale.",
                "variants": [
                    _v("Garanzia cartacea Rolex (era)", "Garanzia/punzonatura coerente con l'anno; sui primi esemplari spesso datata a foratura ('traforata'). Da verificare sul singolo documento.", 1988, 2000, "bassa"),
                ],
            },
            {
                "component": "Scatola e controscatola",
                "icon": "inventory_2",
                "sources": ["bobs"],
                "note": "Dato meno preciso per anno: il codice scatola va confrontato con esemplari coevi documentati.",
                "variants": [
                    _v("Set scatola era 16520", "Scatola/controscatola Rolex del periodo (es. box 'Daytona' con etichetta interna/codice). Da verificare il codice esatto per l'anno.", 1988, 2000, "bassa"),
                ],
            },
        ],
    },

    "6239": {
        "model": "Rolex Cosmograph Daytona ref. 6239",
        "production_from": 1963,
        "production_to": 1969,
        "components": [
            {"component": "Pulsanti (pushers)", "icon": "radio_button_unchecked", "sources": ["iws", "goldammer"], "note": "I 6239 hanno pulsanti a pompa, non a vite.",
             "variants": [_v("A pompa (pump)", "Pulsanti cronografici a pompa, non avvitati.", 1963, 1969, "alta")]},
            {"component": "Ghiera (scala tachimetrica)", "icon": "lens", "sources": ["iws", "goldammer"], "note": None,
             "variants": [_v("Acciaio, tachimetro inciso", "Ghiera in acciaio con scala tachimetrica incisa (varianti di base e 'exotic').", 1963, 1969, "alta")]},
            {"component": "Calibro", "icon": "settings", "sources": ["iws", "goldammer"], "note": None,
             "variants": [_v("Valjoux 72 (manuale)", "Cronografo a carica manuale Valjoux cal. 72.", 1963, 1969, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["iws", "goldammer"], "note": "I quadranti 'Paul Newman' (esotici, Singer) sono molto ricercati e coevi solo a una parte della produzione.",
             "variants": [
                 _v("Standard 'Cosmograph'", "Quadrante standard a tre contatori.", 1963, 1969, "alta"),
                 _v("Esotico 'Paul Newman'", "Quadrante esotico Singer (Art Déco), montato su parte della produzione.", 1965, 1969, "media"),
             ]},
            {"component": "Bracciale", "icon": "watch", "sources": ["iws"], "note": "Da verificare il riferimento e i terminali coevi.",
             "variants": [_v("Oyster rivettato / folded (7835/7836)", "Bracciali Oyster del periodo, spesso poi sostituiti con maglie solide.", 1963, 1969, "media")]},
        ],
    },

    "6263": {
        "model": "Rolex Cosmograph Daytona ref. 6263",
        "production_from": 1971,
        "production_to": 1988,
        "components": [
            {"component": "Pulsanti (pushers)", "icon": "radio_button_unchecked", "sources": ["iws", "goldammer"], "note": "Caratteristica chiave del 6263: pulsanti a vite.",
             "variants": [_v("A vite (screw-down)", "Pulsanti cronografici avvitati, cassa Oyster impermeabile.", 1971, 1988, "alta")]},
            {"component": "Ghiera (scala tachimetrica)", "icon": "lens", "sources": ["iws", "goldammer"], "note": "Il 6263 monta la ghiera acrilica nera (vs. acciaio del 6265).",
             "variants": [_v("Acrilica nera (plexi)", "Ghiera fissa in acrilico nero con scala tachimetrica.", 1971, 1988, "alta")]},
            {"component": "Calibro", "icon": "settings", "sources": ["iws", "goldammer"], "note": None,
             "variants": [_v("Valjoux 727 (manuale)", "Cronografo a carica manuale Valjoux cal. 727.", 1971, 1988, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["iws", "goldammer"], "note": "I 'Paul Newman' sul 6263 sono coevi alla prima parte della produzione.",
             "variants": [
                 _v("Standard 'Cosmograph'", "Quadrante standard a tre contatori.", 1971, 1988, "alta"),
                 _v("Esotico 'Paul Newman'", "Quadrante esotico, montato sui primi anni di produzione.", 1971, 1973, "media"),
             ]},
            {"component": "Bracciale", "icon": "watch", "sources": ["iws"], "note": "Verificare riferimento e terminali coevi all'anno.",
             "variants": [_v("Oyster (folded/solido del periodo)", "Bracciale Oyster coevo; primi esemplari folded, poi maglie solide.", 1971, 1988, "media")]},
        ],
    },

    "6265": {
        "model": "Rolex Cosmograph Daytona ref. 6265",
        "production_from": 1971,
        "production_to": 1988,
        "components": [
            {"component": "Pulsanti (pushers)", "icon": "radio_button_unchecked", "sources": ["iws", "goldammer"], "note": None,
             "variants": [_v("A vite (screw-down)", "Pulsanti cronografici avvitati, cassa Oyster.", 1971, 1988, "alta")]},
            {"component": "Ghiera (scala tachimetrica)", "icon": "lens", "sources": ["iws", "goldammer"], "note": "Il 6265 monta la ghiera in acciaio (vs. acrilica del 6263).",
             "variants": [_v("Acciaio inox, tachimetro inciso", "Ghiera in acciaio lucido con scala tachimetrica incisa.", 1971, 1988, "alta")]},
            {"component": "Calibro", "icon": "settings", "sources": ["iws", "goldammer"], "note": None,
             "variants": [_v("Valjoux 727 (manuale)", "Cronografo a carica manuale Valjoux cal. 727.", 1971, 1988, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["iws", "goldammer"], "note": None,
             "variants": [
                 _v("Standard 'Cosmograph'", "Quadrante standard a tre contatori.", 1971, 1988, "alta"),
                 _v("Esotico 'Paul Newman'", "Quadrante esotico dei primi anni di produzione.", 1971, 1973, "media"),
             ]},
            {"component": "Bracciale", "icon": "watch", "sources": ["iws"], "note": "Verificare riferimento e terminali coevi.",
             "variants": [_v("Oyster (folded/solido del periodo)", "Bracciale Oyster coevo all'anno.", 1971, 1988, "media")]},
        ],
    },

    "116520": {
        "model": "Rolex Cosmograph Daytona ref. 116520",
        "production_from": 2000,
        "production_to": 2016,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": "Primo Daytona con movimento di manifattura Rolex.",
             "variants": [_v("Cal. 4130 (manifattura Rolex, automatico)", "Cronografo automatico in-house, sostituisce il Zenith 4030.", 2000, 2016, "alta")]},
            {"component": "Ghiera (scala tachimetrica)", "icon": "lens", "sources": ["bobs"], "note": None,
             "variants": [_v("Acciaio, tachimetro inciso (400)", "Ghiera in acciaio con scala tachimetrica incisa per 400 unità.", 2000, 2016, "alta")]},
            {"component": "Bracciale", "icon": "watch", "sources": ["bobs"], "note": None,
             "variants": [_v("Oyster 78590 (SEL, Oysterlock)", "Bracciale Oyster a terminali solidi con fermaglio Oysterlock.", 2000, 2016, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["bobs"], "note": None,
             "variants": [_v("Super-LumiNova", "Indici e lancette a Super-LumiNova.", 2000, 2016, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["bobs"], "note": "Indici applicati; minori revisioni nel corso della produzione (proporzioni contatori, dettagli stampa).",
             "variants": [_v("Indici applicati (Super-LumiNova)", "Quadrante a indici applicati luminescenti; piccole revisioni grafiche nel tempo.", 2000, 2016, "media")]},
        ],
    },

    # ===================== SUBMARINER =====================
    "5513": {
        "model": "Rolex Submariner ref. 5513 (no-date)",
        "production_from": 1962, "production_to": 1989,
        "components": [
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["subref", "mono_sub"], "note": "Evoluzione gilt → matte → glossy con contorni in oro bianco.",
             "variants": [
                 _v("Gilt (dorato)", "Quadrante lucido con scritte dorate (prime serie).", 1962, 1967, "media"),
                 _v("Matte", "Quadrante opaco con stampa bianca.", 1967, 1984, "alta"),
                 _v("Glossy, contorni oro bianco", "Quadrante lucido con indici cerchiati in oro bianco (ultime serie).", 1984, 1989, "alta"),
             ]},
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 1520 / 1530 (automatico, no data)", "Movimento automatico senza datario.", 1962, 1989, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio per tutta la produzione.", 1962, 1989, "alta")]},
            {"component": "Ghiera (insert)", "icon": "lens", "sources": ["subref"], "note": "Insert graduata 60'; varianti di stampa nel tempo.",
             "variants": [_v("Insert graduata in alluminio", "Lunetta girevole con insert graduata.", 1962, 1989, "media")]},
        ],
    },
    "1680": {
        "model": "Rolex Submariner Date ref. 1680",
        "production_from": 1969, "production_to": 1980,
        "components": [
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["subref", "mono_sub"], "note": "Il 'Red Submariner' (scritta rossa) è coevo solo alle prime serie.",
             "variants": [
                 _v("Red Submariner (scritta rossa)", "Scritta 'Submariner' in rosso, prime serie.", 1969, 1975, "media"),
                 _v("Scritta bianca", "Scritta 'Submariner' in bianco (serie successive).", 1975, 1980, "alta"),
             ]},
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 1575 (automatico, data)", "Primo Submariner con datario.", 1969, 1980, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1969, 1980, "alta")]},
        ],
    },
    "16800": {
        "model": "Rolex Submariner Date ref. 16800 (transitional)",
        "production_from": 1979, "production_to": 1988,
        "components": [
            {"component": "Cristallo", "icon": "crop_square", "sources": ["subref", "mono_sub"], "note": None,
             "variants": [_v("Zaffiro", "Introduce il vetro zaffiro e l'impermeabilità a 300 m.", 1979, 1988, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["subref", "mono_sub"], "note": "Da matte a glossy con contorni in oro bianco.",
             "variants": [
                 _v("Matte", "Quadrante opaco (prime serie).", 1979, 1984, "media"),
                 _v("Glossy, contorni oro bianco", "Quadrante lucido con indici cerchiati in oro bianco.", 1984, 1988, "alta"),
             ]},
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 3035 (automatico, quickset)", "Datario a regolazione rapida.", 1979, 1988, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1979, 1988, "alta")]},
        ],
    },
    "16610": {
        "model": "Rolex Submariner Date ref. 16610",
        "production_from": 1988, "production_to": 2010,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 3135 (automatico)", "Movimento automatico con datario.", 1988, 2010, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref", "mono_sub"], "note": "Transizione tritio → Luminova → Super-LumiNova; cambia la dicitura sul quadrante.",
             "variants": [
                 _v("Tritio — 'SWISS - T<25'", "Indici al tritio; dicitura 'T<25'.", 1988, 1998, "alta"),
                 _v("Luminova — 'SWISS'", "Breve fase Luminova; dicitura 'SWISS' soltanto.", 1998, 2000, "media"),
                 _v("Super-LumiNova — 'SWISS MADE'", "Super-LumiNova; dicitura 'SWISS MADE'.", 2000, 2010, "alta"),
             ]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["subref"], "note": None,
             "variants": [_v("Glossy, contorni oro bianco", "Quadrante lucido con indici cerchiati in oro bianco.", 1988, 2010, "alta")]},
            {"component": "Bracciale", "icon": "watch", "sources": ["subref"], "note": "Terminali solidi (SEL) introdotti nelle serie più recenti.",
             "variants": [
                 _v("Oyster terminali cavi", "Bracciale Oyster con terminali stampati (prime serie).", 1988, 2003, "media"),
                 _v("Oyster SEL (terminali solidi)", "Terminali solidi, fermaglio Oysterlock.", 2003, 2010, "media"),
             ]},
        ],
    },

    # ===================== GMT-MASTER =====================
    "1675": {
        "model": "Rolex GMT-Master ref. 1675",
        "production_from": 1959, "production_to": 1980,
        "components": [
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["gmt_fratello", "gmt_wind"], "note": "Da gilt a matte attorno al 1966.",
             "variants": [
                 _v("Gilt (dorato)", "Quadrante lucido con scritte dorate (prime serie).", 1959, 1966, "media"),
                 _v("Matte", "Quadrante opaco con stampa bianca.", 1966, 1980, "alta"),
             ]},
            {"component": "Crown guards (protezioni corona)", "icon": "shield", "sources": ["gmt_wind"], "note": "Le 'PCG' (pointed crown guards) sono coeve solo alle prime serie.",
             "variants": [
                 _v("PCG — pointed crown guards", "Protezioni corona appuntite (prime serie).", 1959, 1966, "media"),
                 _v("Protezioni arrotondate", "Protezioni corona arrotondate (serie successive).", 1966, 1980, "alta"),
             ]},
            {"component": "Ghiera (insert)", "icon": "lens", "sources": ["gmt_fratello"], "note": "Insert 24h 'Pepsi'; primissime serie con ghiera in bachelite.",
             "variants": [
                 _v("Insert bachelite", "Ghiera in bachelite (primissime serie).", 1959, 1960, "bassa"),
                 _v("Insert alluminio 'Pepsi'", "Insert 24h in alluminio rosso/blu.", 1960, 1980, "alta"),
             ]},
            {"component": "Calibro", "icon": "settings", "sources": ["gmt_fratello"], "note": None,
             "variants": [_v("Cal. 1565 / 1575 (automatico, GMT)", "Movimento automatico con lancetta 24h.", 1959, 1980, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["gmt_fratello"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1959, 1980, "alta")]},
        ],
    },
    "16750": {
        "model": "Rolex GMT-Master ref. 16750 (transitional)",
        "production_from": 1981, "production_to": 1988,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["gmt_fratello"], "note": None,
             "variants": [_v("Cal. 3075 (automatico, quickset)", "Introduce il datario a regolazione rapida.", 1981, 1988, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["gmt_fratello"], "note": "Da matte a glossy con indici in oro bianco (~1986).",
             "variants": [
                 _v("Matte", "Quadrante opaco con indici stampati.", 1981, 1986, "media"),
                 _v("Glossy, indici oro bianco", "Quadrante lucido con indici cerchiati in oro bianco.", 1986, 1988, "alta"),
             ]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["gmt_fratello"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1981, 1988, "alta")]},
        ],
    },
    "16710": {
        "model": "Rolex GMT-Master II ref. 16710",
        "production_from": 1989, "production_to": 2007,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["gmt_fratello", "bobs"], "note": "Ultime serie con cal. 3186.",
             "variants": [
                 _v("Cal. 3185 (automatico, GMT II)", "Movimento GMT-Master II.", 1989, 2005, "alta"),
                 _v("Cal. 3186", "Aggiornamento di movimento nelle ultime serie.", 2005, 2007, "media"),
             ]},
            {"component": "Ghiera (insert)", "icon": "lens", "sources": ["gmt_fratello"], "note": "Disponibile con insert Pepsi, Coke o nera (a seconda della configurazione).",
             "variants": [_v("Insert 'Pepsi' / 'Coke' / nera", "Insert 24h bicolore (rosso/blu o rosso/nero) o nera.", 1989, 2007, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["gmt_fratello"], "note": "Transizione tritio → Super-LumiNova.",
             "variants": [
                 _v("Tritio — 'SWISS - T<25'", "Indici al tritio; dicitura 'T<25'.", 1989, 1998, "alta"),
                 _v("Super-LumiNova — 'SWISS MADE'", "Super-LumiNova; dicitura 'SWISS MADE'.", 1999, 2007, "alta"),
             ]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["gmt_fratello"], "note": None,
             "variants": [_v("Glossy, indici oro bianco", "Quadrante lucido con indici cerchiati in oro bianco.", 1989, 2007, "alta")]},
        ],
    },

    # ===================== EXPLORER I =====================
    "1016": {
        "model": "Rolex Explorer ref. 1016", "production_from": 1963, "production_to": 1989,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Cal. 1560 / 1570 (automatico)", "Movimento automatico a 3-6-9.", 1963, 1989, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["mono_explorer"], "note": "Da gilt a matte attorno al 1966-67.",
             "variants": [_v("Gilt (dorato)", "Quadrante lucido con scritte dorate.", 1963, 1967, "media"),
                          _v("Matte", "Quadrante opaco con stampa bianca.", 1967, 1989, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico bombato.", 1963, 1989, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1963, 1989, "alta")]},
        ],
    },
    "14270": {
        "model": "Rolex Explorer ref. 14270", "production_from": 1989, "production_to": 2001,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Cal. 3000 (automatico)", "Movimento automatico, 28.800 alt/h.", 1989, 2001, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Zaffiro", "Vetro zaffiro, indici applicati con contorni oro bianco.", 1989, 2001, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_explorer"], "note": "Transizione tritio → Luminova attorno al 1998.",
             "variants": [_v("Tritio — 'SWISS - T<25'", "Indici al tritio.", 1989, 1998, "alta"),
                          _v("Luminova — 'SWISS'/'SWISS MADE'", "Passaggio a Luminova/Super-LumiNova.", 1998, 2001, "media")]},
        ],
    },
    "114270": {
        "model": "Rolex Explorer ref. 114270", "production_from": 2001, "production_to": 2010,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Cal. 3130 (automatico)", "Movimento automatico.", 2001, 2010, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_explorer"], "note": None,
             "variants": [_v("Super-LumiNova", "Indici a Super-LumiNova; 'SWISS MADE'.", 2001, 2010, "alta")]},
        ],
    },

    # ===================== EXPLORER II =====================
    "1655": {
        "model": "Rolex Explorer II ref. 1655 ('Freccione')", "production_from": 1971, "production_to": 1985,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_explorer2"], "note": None,
             "variants": [_v("Cal. 1575 (24h non indipendente)", "Lancetta 24h fissa, non regolabile separatamente.", 1971, 1985, "alta")]},
            {"component": "Lancetta 24h", "icon": "schedule", "sources": ["mono_explorer2"], "note": "La grande lancetta 24h arancione ('Freccione') è la firma del 1655.",
             "variants": [_v("Arancione a freccia ('Freccione')", "Lancetta 24h arancione a punta di freccia.", 1971, 1985, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_explorer2"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1971, 1985, "alta")]},
        ],
    },
    "16570": {
        "model": "Rolex Explorer II ref. 16570", "production_from": 1989, "production_to": 2010,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_explorer2"], "note": "Ultime serie con cal. 3186.",
             "variants": [_v("Cal. 3185 (GMT indipendente)", "Lancetta 24h regolabile separatamente.", 1989, 2007, "alta"),
                          _v("Cal. 3186", "Aggiornamento di movimento (ultime serie).", 2007, 2010, "media")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["mono_explorer2"], "note": "Disponibile nero o bianco ('Polar').",
             "variants": [_v("Nero o Bianco 'Polar'", "Quadrante nero o bianco a indici applicati.", 1989, 2010, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_explorer2"], "note": "Transizione tritio → Super-LumiNova ~1998-2000.",
             "variants": [_v("Tritio — 'SWISS - T<25'", "Indici al tritio.", 1989, 1998, "alta"),
                          _v("Super-LumiNova — 'SWISS MADE'", "Super-LumiNova.", 2000, 2010, "alta")]},
        ],
    },

    # ===================== SEA-DWELLER =====================
    "1665": {
        "model": "Rolex Sea-Dweller ref. 1665 ('Double Red'/'Great White')", "production_from": 1967, "production_to": 1983,
        "components": [
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["subref"], "note": "Il 'Double Red Sea-Dweller' (doppia scritta rossa) è coevo alle prime serie.",
             "variants": [_v("Double Red (DRSD)", "Doppia riga di testo rossa 'Sea-Dweller / Submariner 2000'.", 1967, 1977, "media"),
                          _v("Great White (scritta bianca)", "Testo tutto bianco (serie successive).", 1977, 1983, "media")]},
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 1575 (automatico, data)", "Movimento automatico con datario.", 1967, 1983, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref"], "note": None,
             "variants": [_v("Tritio", "Indici e lancette al tritio.", 1967, 1983, "alta")]},
        ],
    },
    "16600": {
        "model": "Rolex Sea-Dweller ref. 16600", "production_from": 1988, "production_to": 2008,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["subref"], "note": None,
             "variants": [_v("Cal. 3135 (automatico)", "Movimento automatico con datario.", 1988, 2008, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["subref"], "note": "Transizione tritio → Super-LumiNova ~1998-2000.",
             "variants": [_v("Tritio — 'SWISS - T<25'", "Indici al tritio.", 1988, 1998, "alta"),
                          _v("Super-LumiNova — 'SWISS MADE'", "Super-LumiNova.", 2000, 2008, "alta")]},
        ],
    },

    # ===================== DATEJUST =====================
    "1601": {
        "model": "Rolex Datejust ref. 1601", "production_from": 1959, "production_to": 1977,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_dj"], "note": None,
             "variants": [_v("Cal. 1565 / 1575 (automatico, data)", "Movimento automatico; il 1575 aggiunge quickset/hacking sulle serie tarde.", 1959, 1977, "alta")]},
            {"component": "Quadrante", "icon": "radio_button_checked", "sources": ["mono_dj"], "note": "Da gilt a matte attorno al 1966-67.",
             "variants": [_v("Gilt (dorato)", "Quadrante con scritte dorate (prime serie).", 1959, 1967, "media"),
                          _v("Matte", "Quadrante opaco (serie successive).", 1967, 1977, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["mono_dj"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico con lente ciclope sulla data.", 1959, 1977, "alta")]},
        ],
    },
    "16234": {
        "model": "Rolex Datejust ref. 16234", "production_from": 1988, "production_to": 2009,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_dj"], "note": None,
             "variants": [_v("Cal. 3135 (automatico)", "Movimento automatico con datario quickset.", 1988, 2009, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["mono_dj"], "note": None,
             "variants": [_v("Zaffiro", "Vetro zaffiro con lente ciclope.", 1988, 2009, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_dj"], "note": "Transizione tritio → Super-LumiNova ~1998-2000.",
             "variants": [_v("Tritio — 'SWISS - T<25'", "Indici al tritio.", 1988, 1998, "media"),
                          _v("Super-LumiNova — 'SWISS MADE'", "Super-LumiNova.", 2000, 2009, "media")]},
        ],
    },

    # ===================== DAY-DATE (PRESIDENT) =====================
    "1803": {
        "model": "Rolex Day-Date 'President' ref. 1803", "production_from": 1958, "production_to": 1978,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": None,
             "variants": [_v("Cal. 1555 / 1556 (automatico)", "Movimento automatico con giorno e data.", 1958, 1978, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["bobs"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico con lente ciclope.", 1958, 1978, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["bobs"], "note": None,
             "variants": [_v("Tritio", "Indici al tritio (sulle versioni luminescenti).", 1958, 1978, "media")]},
        ],
    },
    "18038": {
        "model": "Rolex Day-Date 'President' ref. 18038", "production_from": 1977, "production_to": 1988,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": None,
             "variants": [_v("Cal. 3055 (automatico, quickset)", "Datario rapido, 28.800 alt/h.", 1977, 1988, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["bobs"], "note": None,
             "variants": [_v("Zaffiro", "Prima serie Day-Date con vetro zaffiro.", 1977, 1988, "alta")]},
        ],
    },

    # ===================== AIR-KING =====================
    "5500": {
        "model": "Rolex Air-King ref. 5500", "production_from": 1957, "production_to": 1989,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": "Cal. 1530 sulle prime serie, poi 1520.",
             "variants": [_v("Cal. 1530 (prime serie)", "Movimento automatico iniziale.", 1957, 1965, "media"),
                          _v("Cal. 1520", "Movimento automatico successivo.", 1965, 1989, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["bobs"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico bombato.", 1957, 1989, "alta")]},
        ],
    },
    "14000": {
        "model": "Rolex Air-King ref. 14000", "production_from": 1989, "production_to": 2000,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": None,
             "variants": [_v("Cal. 3000 (automatico)", "Movimento automatico, 28.800 alt/h.", 1989, 2000, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["bobs"], "note": None,
             "variants": [_v("Zaffiro", "Vetro zaffiro.", 1989, 2000, "alta")]},
        ],
    },

    # ===================== MILGAUSS =====================
    "1019": {
        "model": "Rolex Milgauss ref. 1019", "production_from": 1963, "production_to": 1988,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_milgauss"], "note": None,
             "variants": [_v("Cal. 1580 (automatico, antimagnetico)", "Movimento schermato contro i campi magnetici.", 1963, 1988, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["mono_milgauss"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico.", 1963, 1988, "alta")]},
        ],
    },
    "116400": {
        "model": "Rolex Milgauss ref. 116400 / 116400GV", "production_from": 2007, "production_to": 2023,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["mono_milgauss"], "note": None,
             "variants": [_v("Cal. 3131 (automatico, antimagnetico)", "Movimento antimagnetico con lancetta dei secondi a fulmine.", 2007, 2023, "alta")]},
            {"component": "Cristallo / Quadrante", "icon": "crop_square", "sources": ["mono_milgauss"], "note": "La versione 'GV' ha il vetro zaffiro verde.",
             "variants": [_v("Zaffiro (GV verde sulla 116400GV)", "Vetro zaffiro; verde sulla variante GV.", 2007, 2023, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["mono_milgauss"], "note": None,
             "variants": [_v("Super-LumiNova / Chromalight", "Indici luminescenti moderni.", 2007, 2023, "media")]},
        ],
    },

    # ===================== ALTRE FAMIGLIE (flagship) =====================
    "1002": {
        "model": "Rolex Oyster Perpetual ref. 1002", "production_from": 1958, "production_to": 1985,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": None,
             "variants": [_v("Cal. 1560 / 1570 (automatico)", "Movimento automatico senza datario.", 1958, 1985, "alta")]},
            {"component": "Cristallo", "icon": "crop_square", "sources": ["bobs"], "note": None,
             "variants": [_v("Acrilico (plexi)", "Vetro acrilico bombato.", 1958, 1985, "alta")]},
        ],
    },
    "16622": {
        "model": "Rolex Yacht-Master ref. 16622 (platino/acciaio)", "production_from": 1999, "production_to": 2012,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": None,
             "variants": [_v("Cal. 3135 (automatico)", "Movimento automatico con datario.", 1999, 2012, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["bobs"], "note": None,
             "variants": [_v("Super-LumiNova", "Indici a Super-LumiNova.", 1999, 2012, "media")]},
        ],
    },
    "326934": {
        "model": "Rolex Sky-Dweller ref. 326934", "production_from": 2012, "production_to": 2023,
        "components": [
            {"component": "Calibro", "icon": "settings", "sources": ["bobs"], "note": "Seriale moderno casuale: la datazione dal numero non è possibile.",
             "variants": [_v("Cal. 9001 (automatico, annual calendar GMT)", "Calendario annuale 'Saros' e secondo fuso.", 2012, 2023, "alta")]},
            {"component": "Materiale luminescente", "icon": "light_mode", "sources": ["bobs"], "note": None,
             "variants": [_v("Chromalight", "Luminescenza Chromalight blu.", 2012, 2023, "media")]},
        ],
    },
}
