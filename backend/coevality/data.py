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
}

# Lettere mai usate da Rolex su orologi (riservate a Tudor o non emesse).
SERIAL_NEVER_USED = set("BIJOQ")


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
}
