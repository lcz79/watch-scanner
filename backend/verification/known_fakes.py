"""
Database di falsi noti e pattern comuni per orologi di lusso.
Usato per cross-reference durante l'analisi di autenticità.
"""
from typing import Any

# Livelli di prevalenza:
# "very_common"  → tens of thousands in circulation
# "common"       → thousands
# "occasional"   → hundreds / limited batches
# "rare"         → known instances, niche market

KNOWN_FAKE_PATTERNS: dict[str, Any] = {

    # =========================================================================
    # ROLEX
    # =========================================================================
    "Rolex": {
        "Submariner": [
            {
                "id": "rolex-sub-001",
                "description": "Quadrante con font Arial invece di Helvetica",
                "identification": (
                    "Il testo 'ROLEX' e 'SUBMARINER DATE' in font Arial: "
                    "lettere leggermente più sottili, spaziatura maggiore. "
                    "Confrontare la larghezza della 'O' che in Helvetica è quasi circolare."
                ),
                "prevalence": "very_common",
                "origin": "China (Guangdong)",
                "price_range": "50–500€",
                "visual_tells": [
                    "Font del testo più sottile del normale",
                    "Spaziatura tra lettere leggermente maggiore",
                    "'O' di ROLEX leggermente ovale invece di circolare",
                ],
            },
            {
                "id": "rolex-sub-002",
                "description": "Lancetta dei secondi a scatti (movimento al quarzo)",
                "identification": (
                    "La lancetta dei secondi si muove a scatti di 1 secondo invece "
                    "del quasi-continuo 8 step/sec del calibro Rolex 3235."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "30–200€",
                "visual_tells": [
                    "Movimento a scatti della lancetta secondi",
                    "Orologio leggero (movimento al quarzo più leggero)",
                ],
            },
            {
                "id": "rolex-sub-003",
                "description": "Lunetta ceramica con colore non uniforme",
                "identification": (
                    "La ceramica dei falsi tende a perdere uniformità di colore "
                    "soprattutto ai bordi. La ceramica Rolex originale mantiene colore uniforme "
                    "anche con angolazioni di luce diverse."
                ),
                "prevalence": "common",
                "origin": "China (varie fabbriche)",
                "price_range": "200–2000€",
                "visual_tells": [
                    "Variazioni di colore sulla ceramica con luce radente",
                    "Testo sulla lunetta con leggere irregolarità di spessore",
                    "Triangolo ore 12 con luminova giallastra invece di bianca",
                ],
            },
            {
                "id": "rolex-sub-004",
                "description": "Magnificazione Cyclops inferiore a 2.5x",
                "identification": (
                    "Nei falsi la lente Cyclops ingrandisce meno di 2.5x. "
                    "Semplice test: la data deve apparire grande quanto l'apertura della finestra."
                ),
                "prevalence": "very_common",
                "origin": "Multiple",
                "price_range": "50–5000€",
                "visual_tells": [
                    "Data visibilmente piccola attraverso la lente",
                    "Data non riempie la finestra della lente",
                ],
            },
            {
                "id": "rolex-sub-005",
                "description": "Bracciale Oyster con maglie cave",
                "identification": (
                    "Le maglie cave producono un suono 'vuoto' quando battute "
                    "e il bracciale pesa meno dell'originale (~180g totale braccialet Oyster). "
                    "La finitura satinata/lucida può sembrare corretta ma le maglie si deformano."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "100–1000€",
                "visual_tells": [
                    "Peso del bracciale inferiore al normale",
                    "Suono metallico 'vuoto' alla percussione",
                    "Maglie che cedono leggermente alla pressione",
                ],
            },
            {
                "id": "rolex-sub-006",
                "description": "Clone di alta qualità 'Noob V11' o 'Clean Factory'",
                "identification": (
                    "Falsi di alta gamma (c. 500–2000€) che replicano anche la ceramica e "
                    "il movimento clone. Differenze: il testo sul fondello ha micro-errori tipografici, "
                    "il peso totale è leggermente inferiore (~130g vs ~155g), "
                    "il sapphire presenta un leggero alone anti-riflesso verde invece del viola."
                ),
                "prevalence": "occasional",
                "origin": "China (fabbriche specializzate)",
                "price_range": "500–2000€",
                "visual_tells": [
                    "Peso totale leggermente inferiore (~130g vs ~155g)",
                    "Anti-riflesso del cristallo verde invece di viola",
                    "Micro-errori tipografici sul fondello inciso",
                    "Olografia Rolex sul fondello assente o diversa",
                ],
            },
        ],

        "Daytona": [
            {
                "id": "rolex-day-001",
                "description": "Contatori cronografo non allineati",
                "identification": (
                    "Nei falsi Daytona i tre contatori presentano spesso piccole asimmetrie. "
                    "Test: traccia linee immaginarie che li collegano — devono essere perfettamente "
                    "allineate in verticale e orizzontale."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "100–2000€",
                "visual_tells": [
                    "Contatori con micro-asimmetrie visibili",
                    "Indici interni ai contatori mal centrati",
                ],
            },
            {
                "id": "rolex-day-002",
                "description": "Cronografo non funzionante o impreciso",
                "identification": (
                    "Nei falsi il cronografo spesso non funziona affatto, "
                    "o la lancetta centrale dei secondi non torna esattamente a 12 al reset."
                ),
                "prevalence": "common",
                "origin": "Multiple",
                "price_range": "50–500€",
                "visual_tells": [
                    "Lancetta centrale non torna a 12 dopo reset",
                    "Pulsanti con gioco laterale eccessivo",
                ],
            },
            {
                "id": "rolex-day-003",
                "description": "Scala tachimetrica con font errato",
                "identification": (
                    "La scala tachimetrica in ceramica Rolex usa font proprietario. "
                    "I falsi usano font standard con leggere differenze nella forma dei numeri "
                    "(in particolare il '6', '9' e '3')."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "200–3000€",
                "visual_tells": [
                    "Font numeri scala tachimetrica leggermente diverso",
                    "Colore ceramica non uniformemente nero profondo",
                ],
            },
        ],

        "GMT-Master II": [
            {
                "id": "rolex-gmt-001",
                "description": "Divisione colore lunetta Batman/Pepsi non netta",
                "identification": (
                    "La divisione tra i due colori della ceramica bicolore Rolex è "
                    "millimetrica e netta. Nei falsi c'è una sfumatura o una leggera "
                    "ondulazione alla giunzione dei due colori."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "100–3000€",
                "visual_tells": [
                    "Divisione colori sfumata invece di netta",
                    "Uno dei due colori leggermente sbiadito",
                    "Bordo del bi-colore non perfettamente a ore 6 e 12",
                ],
            },
            {
                "id": "rolex-gmt-002",
                "description": "Lancetta GMT senza lume funzionante",
                "identification": (
                    "La punta triangolare della lancetta GMT deve avere lume visibile al buio. "
                    "Nei falsi di bassa qualità il lume è assente o di colore verde errato."
                ),
                "prevalence": "common",
                "origin": "Multiple",
                "price_range": "50–300€",
                "visual_tells": [
                    "Punta GMT senza lume al buio",
                    "Lume verde fluorescente invece di bianco/crema",
                ],
            },
        ],

        "Datejust": [
            {
                "id": "rolex-dj-001",
                "description": "Quadrante con bracciale Jubilee cavo",
                "identification": (
                    "Il Datejust è il modello Rolex più falsificato in assoluto. "
                    "Il bracciale Jubilee falso ha maglie cave e un peso totale inferiore di 30-40g."
                ),
                "prevalence": "very_common",
                "origin": "China, Hong Kong",
                "price_range": "30–500€",
                "visual_tells": [
                    "Peso orologio inferiore al normale",
                    "Suono vuoto alle maglie del Jubilee",
                    "Chiusura Crownclasp senza scatti precisi",
                ],
            },
        ],
    },

    # =========================================================================
    # PATEK PHILIPPE
    # =========================================================================
    "Patek Philippe": {
        "Nautilus": [
            {
                "id": "pp-naut-001",
                "description": "Pattern quadrante senza rilievo orizzontale",
                "identification": (
                    "Il quadrante del Nautilus 5711 ha un pattern in rilievo che "
                    "cambia riflesso con l'angolazione. Nei falsi il pattern è stampato in piano "
                    "senza variazione di riflesso."
                ),
                "prevalence": "very_common",
                "origin": "China, Hong Kong",
                "price_range": "500–5000€",
                "visual_tells": [
                    "Pattern orizzontale piatto senza rilievo",
                    "Colore del quadrante non cambia con l'angolazione",
                    "Rifinitura cassa non con contrasto opaco/lucido netto",
                ],
            },
            {
                "id": "pp-naut-002",
                "description": "Viti lunetta ottagonale decorative non funzionali",
                "identification": (
                    "Le 8 viti sulla lunetta del Nautilus nell'originale sono funzionali "
                    "e tengono la lunetta alla cassa. Nei falsi sono spesso decorative. "
                    "Test: le viti originali sono esagonali con testa ben definita."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "200–10000€",
                "visual_tells": [
                    "Viti con testa che non mostra l'impronta esagonale netta",
                    "Viti non allineate perfettamente in verticale/orizzontale",
                ],
            },
            {
                "id": "pp-naut-003",
                "description": "Anglage assente sulla cassa",
                "identification": (
                    "L'anglage (bisellatura e lucidatura degli angoli) di Patek è manuale "
                    "e produce angoli affilati con due superfici di rifinitura diversa. "
                    "Nei falsi gli angoli sono arrotondati o con finitura uniforme."
                ),
                "prevalence": "very_common",
                "origin": "Multiple",
                "price_range": "500–20000€",
                "visual_tells": [
                    "Angoli della cassa arrotondati",
                    "Finitura uniforme senza alternanza opaco/lucido",
                ],
            },
        ],

        "Calatrava": [
            {
                "id": "pp-cal-001",
                "description": "Indici stampati invece di applicati",
                "identification": (
                    "I Calatrava originali hanno indici in oro applicati (fisicamente incollati) "
                    "che proiettano ombra sul quadrante. Nei falsi sono stampati e piatti."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "100–5000€",
                "visual_tells": [
                    "Assenza di ombreggiatura sotto gli indici",
                    "Indici piatti senza spessore",
                    "Indici con bordi non netti",
                ],
            },
        ],
    },

    # =========================================================================
    # AUDEMARS PIGUET
    # =========================================================================
    "Audemars Piguet": {
        "Royal Oak": [
            {
                "id": "ap-ro-001",
                "description": "Viti lunetta non perfettamente allineate",
                "identification": (
                    "Le 8 viti esagonali del Royal Oak devono formare un ottagono perfetto "
                    "e allinearsi in verticale a ore 3, 6, 9, 12. "
                    "Nei falsi le viti presentano micro-disallineamenti."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "100–5000€",
                "visual_tells": [
                    "Viti non perfettamente allineate orizzontalmente/verticalmente",
                    "Testa delle viti non perfettamente esagonale",
                    "Spaziatura non uniforme tra le viti",
                ],
            },
            {
                "id": "ap-ro-002",
                "description": "Pattern Grande Tapisserie piatto",
                "identification": (
                    "Il pattern Grande Tapisserie del Royal Oak è inciso in rilievo. "
                    "Nei falsi è spesso stampato o inciso superficialmente, "
                    "risultando piatto alla visione angolata."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "200–10000€",
                "visual_tells": [
                    "Pattern quadrante piatto senza rilievo visibile angolando",
                    "Pattern non uniforme vicino agli indici",
                    "Colore 'bleu ardoise' non corrispondente all'originale",
                ],
            },
            {
                "id": "ap-ro-003",
                "description": "Transizione cassa-bracciale non fluida",
                "identification": (
                    "Il bracciale AP è integrato nella cassa con una transizione "
                    "invisibile. Nei falsi si nota un gradino o una giunzione visibile "
                    "tra cassa e primo elemento del bracciale."
                ),
                "prevalence": "common",
                "origin": "Multiple",
                "price_range": "500–15000€",
                "visual_tells": [
                    "Gradino visibile tra cassa e bracciale",
                    "Primo elemento del bracciale con forma non integrata",
                ],
            },
        ],
    },

    # =========================================================================
    # OMEGA
    # =========================================================================
    "Omega": {
        "Speedmaster": [
            {
                "id": "omega-speed-001",
                "description": "Scala tachimetrica con numeri al contrario o in senso errato",
                "identification": (
                    "La scala tachimetrica dello Speedmaster va da 500 (vicino alle 12) "
                    "in senso antiorario fino a 60 (vicino alle 9). "
                    "Nei falsi l'ordine è spesso invertito."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "30–200€",
                "visual_tells": [
                    "Numeri scala in ordine errato",
                    "Punto di partenza della scala in posizione diversa",
                ],
            },
            {
                "id": "omega-speed-002",
                "description": "Cristallo Hesalite sostituito con cristallo minerale",
                "identification": (
                    "Lo Speedmaster Moonwatch usa cristallo Hesalite (plexiglass). "
                    "Nei falsi viene usato vetro minerale o zaffiro, "
                    "riconoscibili perché non si graffiano 'facilmente' come il plexiglass "
                    "e riflettono diversamente la luce."
                ),
                "prevalence": "occasional",
                "origin": "Multiple",
                "price_range": "50–500€",
                "visual_tells": [
                    "Cristallo senza i tipici micro-graffi dell'Hesalite",
                    "Riflesso anti-riflesso sul cristallo (Hesalite non ha AR coating)",
                ],
            },
        ],

        "Seamaster": [
            {
                "id": "omega-sea-001",
                "description": "Pattern a onde quadrante non uniforme",
                "identification": (
                    "Il pattern a onde del Seamaster deve essere uniforme e preciso. "
                    "Nei falsi le onde presentano irregolarità, interruzioni o "
                    "il pattern non è perfettamente concentrico."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "50–300€",
                "visual_tells": [
                    "Onde non uniformi o con interruzioni",
                    "Pattern non concentrico",
                    "Colore del quadrante non uniforme",
                ],
            },
            {
                "id": "omega-sea-002",
                "description": "Valvola escape elio decorativa",
                "identification": (
                    "La valvola elio a ore 10 nei falsi è spesso solo decorativa. "
                    "Nell'originale è avvitabile/funzionale. "
                    "Test: ruotare la valvola — deve girare."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "50–300€",
                "visual_tells": [
                    "Valvola elio non avvitabile",
                    "Forma della valvola diversa dall'originale",
                ],
            },
        ],
    },

    # =========================================================================
    # TUDOR
    # =========================================================================
    "Tudor": {
        "Black Bay": [
            {
                "id": "tudor-bb-001",
                "description": "Lancette Snowflake senza lume funzionante",
                "identification": (
                    "Le lancette Snowflake Tudor devono avere lume abbondante (Super-LumiNova). "
                    "Nei falsi il lume è assente o di qualità inferiore."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "50–300€",
                "visual_tells": [
                    "Lume assente o scarso sulle lancette Snowflake",
                    "Lume verde-giallo fluorescente invece di bianco al buio",
                ],
            },
            {
                "id": "tudor-bb-002",
                "description": "Insert lunetta non in alluminio anodizzato",
                "identification": (
                    "L'insert della lunetta Black Bay è in alluminio anodizzato. "
                    "Nei falsi viene usato insert in plastica o vernice che si stacca "
                    "con l'uso."
                ),
                "prevalence": "very_common",
                "origin": "China",
                "price_range": "30–200€",
                "visual_tells": [
                    "Insert si stacca o mostra segni di usura anomali",
                    "Colore dell'insert non uniforme",
                    "Insert con superficie lucida invece di opaca",
                ],
            },
            {
                "id": "tudor-bb-003",
                "description": "Scudo Tudor sul quadrante con proporzioni errate",
                "identification": (
                    "Lo scudo Tudor deve essere proporzionato al quadrante. "
                    "Nei falsi è spesso troppo grande, troppo piccolo o mal centrato."
                ),
                "prevalence": "common",
                "origin": "China",
                "price_range": "50–500€",
                "visual_tells": [
                    "Scudo Tudor con proporzioni evidentemente errate",
                    "Logo Tudor mal centrato sul quadrante",
                    "Font 'TUDOR' con spaziatura non corretta",
                ],
            },
        ],
    },
}


def find_matching_fakes(brand: str, model: str | None = None) -> list[dict]:
    """
    Restituisce i pattern di falsi noti per brand e opzionalmente per modello.
    Ricerca case-insensitive.
    """
    brand_key = next(
        (k for k in KNOWN_FAKE_PATTERNS if k.lower() == brand.lower()), None
    )
    if not brand_key:
        return []

    brand_fakes = KNOWN_FAKE_PATTERNS[brand_key]

    if model is None:
        # Restituisce tutti i falsi del brand
        all_fakes = []
        for model_name, fakes in brand_fakes.items():
            for fake in fakes:
                all_fakes.append({**fake, "model": model_name, "brand": brand_key})
        return all_fakes

    model_key = next(
        (k for k in brand_fakes if k.lower() == model.lower()), None
    )
    if not model_key:
        return []

    return [
        {**fake, "model": model_key, "brand": brand_key}
        for fake in brand_fakes[model_key]
    ]


def get_fake_prevalence_summary(brand: str, model: str | None = None) -> dict:
    """
    Restituisce un sommario della prevalenza di falsi per brand/modello.
    """
    fakes = find_matching_fakes(brand, model)
    if not fakes:
        return {"total": 0, "by_prevalence": {}}

    prevalence_count: dict[str, int] = {}
    for fake in fakes:
        p = fake.get("prevalence", "unknown")
        prevalence_count[p] = prevalence_count.get(p, 0) + 1

    return {
        "total": len(fakes),
        "by_prevalence": prevalence_count,
        "risk_level": (
            "very_high" if prevalence_count.get("very_common", 0) >= 2
            else "high" if prevalence_count.get("very_common", 0) >= 1
            else "medium" if prevalence_count.get("common", 0) >= 2
            else "low"
        ),
    }
