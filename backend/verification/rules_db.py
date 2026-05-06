"""
Database di regole di autenticità per orologi di lusso.
Ogni regola ha un peso (weight) usato nel calcolo dello score finale.
"""
from typing import Any

# ---------------------------------------------------------------------------
# Struttura di ogni check:
# {
#   "check":        str  — identificatore univoco
#   "description":  str  — cosa controllare
#   "weight":       float (0-1) — importanza per lo score finale
#   "fake_indicators": list[str] — elementi che segnalano un falso
#   "authentic_indicators": list[str] — elementi che confermano autenticità (opzionale)
# }
# ---------------------------------------------------------------------------

AUTHENTICATION_RULES: dict[str, Any] = {

    # =========================================================================
    # ROLEX
    # =========================================================================
    "Rolex": {
        "general": [
            {
                "check": "serial_format",
                "description": (
                    "Numero seriale Rolex: inciso sul fondello (pre-2005) o tra le anse "
                    "a ore 6 sul bordo superiore della cassa (post-2005). "
                    "Formato: 5-8 cifre numeriche (pre-2010) oppure 8 caratteri alfanumerici "
                    "casuali (post-2010, es. 'X5J23819')."
                ),
                "weight": 0.15,
                "fake_indicators": [
                    "seriale con lettere nel mezzo (post-2010 eccetto prefisso singola lettera pre-2007)",
                    "meno di 5 cifre",
                    "incisione superficiale o stampata invece di incisa laser",
                    "seriale illeggibile o sbavato",
                ],
                "authentic_indicators": [
                    "incisione laser precisa e uniforme",
                    "cifre o caratteri ben definiti",
                ],
            },
            {
                "check": "model_number",
                "description": (
                    "Numero di modello (referenza) inciso sul lato opposto al seriale, "
                    "tra le anse a ore 12 (pre-2005) o sul bordo superiore cassa tra le anse a ore 12 (post-2005)."
                ),
                "weight": 0.10,
                "fake_indicators": [
                    "referenza assente",
                    "referenza non corrisponde al modello visivo",
                    "font errato o spaziatura irregolare",
                ],
            },
            {
                "check": "crown_logo",
                "description": (
                    "La corona Rolex sul quadrante deve avere esattamente 5 punte, "
                    "bordi netti e profili simmetrici. Incisa/stampata con inchiostro sericografico "
                    "tridimensionale e lucido su quadrante originale."
                ),
                "weight": 0.20,
                "fake_indicators": [
                    "corona con 4 o 6 punte",
                    "bordi della corona sfumati o irregolari",
                    "corona piatta senza effetto tridimensionale",
                    "corona troppo grande o troppo piccola rispetto al testo sottostante",
                    "corona color oro su referenza in acciaio senza decorazioni gold",
                ],
                "authentic_indicators": [
                    "5 punte precise e simmetriche",
                    "aspetto tridimensionale e lucido",
                    "dimensioni proporzionate al quadrante",
                ],
            },
            {
                "check": "dial_printing",
                "description": (
                    "La stampa del quadrante Rolex usa serigrafia multi-strato. "
                    "Il testo 'ROLEX' è in Helvetica (non Arial). 'OYSTER PERPETUAL' e il modello "
                    "sono in font proprietario con spaziatura precisa. "
                    "'SWISS MADE' in fondo al quadrante, piccolo e bilanciato."
                ),
                "weight": 0.20,
                "fake_indicators": [
                    "font Arial o simile invece di Helvetica per 'ROLEX'",
                    "spaziatura irregolare tra le lettere",
                    "testo 'SWISS MADE' assente o in posizione errata",
                    "testo sbavato o non nitido",
                    "livello serigrafico piatto (assenza di spessore)",
                    "colore del testo leggermente diverso (es. bianco sporco invece di bianco puro)",
                ],
                "authentic_indicators": [
                    "font Helvetica preciso",
                    "serigrafia multi-strato visibile in luce radente",
                    "SWISS MADE presente e ben centrato",
                ],
            },
            {
                "check": "cyclops_lens",
                "description": (
                    "La lente Cyclops sopra la data deve ingrandire esattamente 2.5x. "
                    "È posizionata perfettamente centrata sulla finestra data. "
                    "Su modelli in acciaio è trasparente e cristallina."
                ),
                "weight": 0.12,
                "fake_indicators": [
                    "lente non centrata sulla data",
                    "ingrandimento minore di 2.5x (data ancora piccola)",
                    "ingrandimento eccessivo o distorto",
                    "lente piatta senza curvatura",
                    "bolle o inclusioni nella lente",
                ],
                "authentic_indicators": [
                    "data ingrandita 2.5x e perfettamente leggibile",
                    "lente ben centrata",
                ],
            },
            {
                "check": "crown_winding",
                "description": (
                    "Il fondello Rolex è avvitato (non a pressione) per modelli Oyster. "
                    "La corona di carica è avvitabile (Triplock o Twinlock a seconda del modello). "
                    "Resistenza all'acqua garantita dal sistema Oyster."
                ),
                "weight": 0.08,
                "fake_indicators": [
                    "fondello a pressione su modelli Oyster",
                    "corona non avvitabile su modelli che dovrebbero averla",
                    "mancanza del logo 'ROLEX' sulla corona di carica",
                ],
                "authentic_indicators": [
                    "fondello avvitato con scanalature",
                    "corona con logo Rolex in rilievo",
                ],
            },
            {
                "check": "movement_sweep",
                "description": (
                    "Il movimento Rolex è automatico con secondi che scorrono in modo "
                    "quasi continuo (8 tick al secondo = circa 28.800 bph). "
                    "Il rotore deve girare silenziosamente."
                ),
                "weight": 0.15,
                "fake_indicators": [
                    "lancetta dei secondi a scatto (1 tick/sec = movimento al quarzo)",
                    "movimento rumoroso o con vibrazioni eccessive",
                    "rotore che cigola",
                ],
                "authentic_indicators": [
                    "secondi quasi continui, 8 step al secondo",
                    "rotore silenzioso",
                ],
            },
        ],
        "models": {
            "Submariner": {
                "references": [
                    "116610LN", "126610LN", "116610LV", "126610LV",
                    "16610", "16610T", "14060", "14060M",
                    "116613LB", "126613LB", "116618LN", "126618LN",
                ],
                "checks": [
                    {
                        "check": "bezel_insert",
                        "description": (
                            "Lunetta Submariner: ceramica nera (116610LN/126610LN) o verde (126610LV). "
                            "Pre-2010 (16610) aveva insert in alluminio anodizzato. "
                            "I 60 graduazioni devono essere perfettamente allineate. "
                            "Il triangolo a ore 12 deve essere pieno e preciso."
                        ),
                        "weight": 0.25,
                        "fake_indicators": [
                            "insert in alluminio su referenza post-2010 (dovrebbe essere ceramica)",
                            "colore non uniforme della ceramica",
                            "testo o graduazioni storte o mal allineate",
                            "triangolo delle ore 12 vuoto o deformato",
                            "luminova nel triangolo assente o color verde invece di bianco/crema",
                            "ceramica che graffia facilmente (la vera ceramica Rolex è quasi impossibile da graffiare)",
                        ],
                        "authentic_indicators": [
                            "ceramica con colore uniforme e profondo",
                            "graduazioni precise e allineate",
                            "triangolo pieno con luminova",
                        ],
                    },
                    {
                        "check": "maxi_dial",
                        "description": (
                            "Quadrante Maxi (post-2008): indici spessi e ricoperti da luminova bianca "
                            "(non verde). Lancette corrispondenti con luminova sulle punte. "
                            "Il quadrante è incassato rispetto alla lunetta."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "indici sottili non-Maxi su referenza post-2008",
                            "luminova verde fluorescente invece di bianca/crema",
                            "indici non uniformi nella dimensione",
                            "quadrante allo stesso livello della lunetta (non incassato)",
                        ],
                        "authentic_indicators": [
                            "indici Maxi spessi e uniformi",
                            "luminova bianca/Super-LumiNova sugli indici",
                        ],
                    },
                    {
                        "check": "bracelet_oyster",
                        "description": (
                            "Bracciale Oyster con maglie solide (non cave). "
                            "Chiusura Oysterlock con sistema di sicurezza Easylink (+5mm) sui modelli recenti. "
                            "La maglie centrale è satinata, quelle esterne lucide."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "maglie cave (suono vuoto quando battute)",
                            "finitura uniforme senza contrasto opaco/lucido",
                            "chiusura a farfalla semplice invece di Oysterlock",
                            "bracciale che non ha peso adeguato (troppo leggero)",
                        ],
                        "authentic_indicators": [
                            "maglie solide e pesanti",
                            "contrasto satinato/lucido corretto",
                            "sistema Easylink funzionante",
                        ],
                    },
                    {
                        "check": "water_resistance_crown",
                        "description": (
                            "Corona di carica Triplock (3 punti sul simbolo corona) per Submariner. "
                            "Si avvita saldamente senza giochi."
                        ),
                        "weight": 0.10,
                        "fake_indicators": [
                            "simbolo Twinlock (2 punti) invece di Triplock",
                            "corona che si allenta facilmente",
                            "corona senza incisione del logo",
                        ],
                        "authentic_indicators": [
                            "3 punti visibili sul logo della corona",
                            "avvitamento preciso senza giochi",
                        ],
                    },
                ],
                "serial_ranges": {
                    "116610LN": {"from_year": 2010, "to_year": 2020},
                    "126610LN": {"from_year": 2020, "to_year": None},
                    "16610": {"from_year": 1989, "to_year": 2010},
                    "14060M": {"from_year": 1998, "to_year": 2012},
                },
            },

            "Daytona": {
                "references": [
                    "116500LN", "126500LN", "116520", "116523", "116505",
                    "16520", "116519", "116519LN",
                ],
                "checks": [
                    {
                        "check": "subdials_alignment",
                        "description": (
                            "I 3 contatori cronografo (ore 3, 6, 9) devono essere perfettamente "
                            "centrati e allineati tra loro. "
                            "Contatore ore 6: 60 minuti. Ore 3: 12 ore. Ore 9: secondi continui."
                        ),
                        "weight": 0.25,
                        "fake_indicators": [
                            "contatori non perfettamente centrati",
                            "asimmetria tra i tre contatori",
                            "font dei numeri nei contatori errato",
                            "indici interni ai contatori mal posizionati",
                        ],
                        "authentic_indicators": [
                            "tre contatori perfettamente simmetrici",
                            "font uniforme e preciso",
                        ],
                    },
                    {
                        "check": "tachymeter_bezel",
                        "description": (
                            "Lunetta con scala tachimetrica in ceramica nera (116500LN/126500LN). "
                            "Numeri bianchi perfettamente leggibili e uniformi. "
                            "16520 e precedenti: lunetta in acciaio con inserto in alluminio."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "scala tachimetrica con numeri storte o mal allineati",
                            "ceramica su referenza che dovrebbe avere alluminio",
                            "alluminio su referenza che dovrebbe avere ceramica",
                            "colore della ceramica non uniforme",
                        ],
                        "authentic_indicators": [
                            "numeri tachimetrici uniformi e ben leggibili",
                            "ceramica di qualità uniforme",
                        ],
                    },
                    {
                        "check": "pushers",
                        "description": (
                            "I pulsanti del cronografo (a ore 2 e 4) devono avere forma a tubo "
                            "e resistenza precisa alla pressione. Non devono avere giochi laterali."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "pulsanti con eccessivo gioco laterale",
                            "forma dei pulsanti errata (rotondi invece che tubolari)",
                            "resistenza irregolare alla pressione",
                        ],
                        "authentic_indicators": [
                            "pulsanti tubolari senza giochi",
                            "resistenza uniforme e precisa",
                        ],
                    },
                    {
                        "check": "chronograph_function",
                        "description": (
                            "Il cronografo deve partire, fermarsi e azzerarsi con scatti netti. "
                            "L'azzeramento della lancetta dei secondi al centro deve essere istantaneo."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "azzeramento non preciso (lancetta non torna esattamente a 12)",
                            "scatti imprecisi dei pulsanti",
                            "contatori che non si resettano correttamente",
                        ],
                        "authentic_indicators": [
                            "azzeramento preciso a 12",
                            "funzione cronografo fluida e precisa",
                        ],
                    },
                ],
                "serial_ranges": {
                    "116500LN": {"from_year": 2016, "to_year": 2023},
                    "126500LN": {"from_year": 2023, "to_year": None},
                    "116520": {"from_year": 2000, "to_year": 2016},
                    "16520": {"from_year": 1988, "to_year": 2000},
                },
            },

            "GMT-Master II": {
                "references": [
                    "116710LN", "116710BLNR", "126710BLNR", "126710BLRO",
                    "126711CHNR", "116713LN", "116718LN",
                    "16710", "16713",
                ],
                "checks": [
                    {
                        "check": "bezel_bicolor",
                        "description": (
                            "Lunetta bicolore (Batman 116710BLNR: blu/nero; Pepsi 126710BLRO: rosso/blu). "
                            "La divisione tra i due colori deve essere perfettamente netta a ore 6 e 12. "
                            "La ceramica bicolore è prodotta da Rolex con processo brevettato."
                        ),
                        "weight": 0.30,
                        "fake_indicators": [
                            "divisione tra colori sfumata o imprecisa",
                            "colori non uniformi nei rispettivi emisferi",
                            "superficie della ceramica opaca invece di lucida",
                            "colori sbiaditi o non corrispondenti al modello",
                        ],
                        "authentic_indicators": [
                            "divisione netta e precisa a ore 6/12",
                            "colori vividi e uniformi",
                            "superficie lucida tipica ceramica Rolex",
                        ],
                    },
                    {
                        "check": "gmt_hand",
                        "description": (
                            "La lancetta GMT (a freccia) deve avere il triangolo triangolo/punta visibile "
                            "con luminova. Deve muoversi di 1 ora per scatto sulla lunetta girevole."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "lancetta GMT senza luminova",
                            "forma della punta GMT errata",
                            "lancetta GMT che non si muove indipendentemente",
                        ],
                        "authentic_indicators": [
                            "luminova sulla punta GMT",
                            "movimento indipendente funzionante",
                        ],
                    },
                    {
                        "check": "jubilee_or_oyster_bracelet",
                        "description": (
                            "GMT-Master II può avere bracciale Jubilee (maglie più piccole, alternanza "
                            "opaco/lucido) o Oyster. Il Jubilee ha 5 parti per maglia. "
                            "Rolex ha introdotto Jubilee su GMT dal 2018 (126710)."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "bracciale Jubilee su referenza 116710 (non originale)",
                            "maglie del Jubilee non uniformi o cave",
                            "finitura Jubilee senza contrasto opaco/lucido",
                        ],
                        "authentic_indicators": [
                            "bracciale corretto per la referenza",
                            "maglie solide e ben rifinite",
                        ],
                    },
                ],
                "serial_ranges": {
                    "116710LN": {"from_year": 2007, "to_year": 2018},
                    "116710BLNR": {"from_year": 2013, "to_year": 2019},
                    "126710BLNR": {"from_year": 2019, "to_year": None},
                    "126710BLRO": {"from_year": 2018, "to_year": None},
                    "16710": {"from_year": 1989, "to_year": 2007},
                },
            },

            "Datejust": {
                "references": [
                    "126200", "126300", "126334", "116200", "116300",
                    "16200", "16234", "16030", "68274",
                    "126233", "126231", "116233",
                ],
                "checks": [
                    {
                        "check": "date_window",
                        "description": (
                            "Finestra data con cornice ciclops (solo modelli con data). "
                            "La data deve essere perfettamente centrata nella finestra. "
                            "Font dei numeri data: Rolex usa font specifico con caratteri nitidi."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "data non centrata nella finestra",
                            "font data errato o sbavato",
                            "finestra data di dimensioni errate",
                        ],
                        "authentic_indicators": [
                            "data centrata e ben leggibile",
                            "font data preciso",
                        ],
                    },
                    {
                        "check": "fluted_bezel",
                        "description": (
                            "Lunetta godronata (fluted) in oro o bicolore: "
                            "le scanalature devono essere uniformi e simmetriche. "
                            "Modelli in acciaio hanno lunetta liscia o con diamanti."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "scanalature non uniformi nella profondità o larghezza",
                            "lunetta godronata su modello che la prevede liscia",
                            "finitura oro troppo uniforme (possibile placcatura invece di oro pieno)",
                        ],
                        "authentic_indicators": [
                            "scanalature uniformi e simmetriche",
                            "finitura oro di qualità",
                        ],
                    },
                    {
                        "check": "jubilee_bracelet",
                        "description": (
                            "Bracciale Jubilee originale del Datejust: 5 parti per maglia, "
                            "maglie centrali satiante, esterne lucide. "
                            "Chiusura Crownclasp con sistema di sicurezza."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "maglie Jubilee cave o con suono vuoto",
                            "assenza del contrasto satinato/lucido",
                            "maglie con spaziatura non uniforme",
                            "chiusura senza sistema di sicurezza Crownclasp",
                        ],
                        "authentic_indicators": [
                            "maglie piene e pesanti",
                            "contrasto satinato/lucido corretto",
                            "Crownclasp funzionante",
                        ],
                    },
                ],
                "serial_ranges": {
                    "126200": {"from_year": 2019, "to_year": None},
                    "116200": {"from_year": 2000, "to_year": 2019},
                    "16200": {"from_year": 1994, "to_year": 2000},
                },
            },
        },
    },

    # =========================================================================
    # PATEK PHILIPPE
    # =========================================================================
    "Patek Philippe": {
        "general": [
            {
                "check": "finishing_quality",
                "description": (
                    "Patek Philippe usa finiture alternate opache/lucide con angoli "
                    "perfettamente netti (anglage). Ogni superficie deve avere un aspetto "
                    "diverso da quella adiacente. Il côtes de Genève è visibile sul movimento."
                ),
                "weight": 0.25,
                "fake_indicators": [
                    "finitura uniforme senza contrasto opaco/lucido",
                    "angoli arrotondati invece che netti",
                    "mancanza di anglage sulle anse",
                    "superfici con graffi o irregolarità",
                ],
                "authentic_indicators": [
                    "anglage perfetto su tutte le anse",
                    "contrasto netto opaco/lucido",
                    "superfici speculari senza difetti",
                ],
            },
            {
                "check": "pp_seal",
                "description": (
                    "Il Sigillo Patek Philippe (Patek Philippe Seal, ex Poinçon de Genève) "
                    "garantisce standard meccanici e estetici superiori. "
                    "Inciso sul fondello e nel movimento."
                ),
                "weight": 0.15,
                "fake_indicators": [
                    "Sigillo assente o male inciso",
                    "font del sigillo errato",
                ],
                "authentic_indicators": [
                    "Sigillo chiaramente visibile e ben inciso",
                ],
            },
            {
                "check": "dial_quality",
                "description": (
                    "I quadranti Patek Philippe sono realizzati con tecniche artigianali. "
                    "Guillochè, smaltatura, lacca: ogni tecnica deve mostrare qualità estrema. "
                    "Il logo 'PATEK PHILIPPE GENEVE' è in font proprietario."
                ),
                "weight": 0.25,
                "fake_indicators": [
                    "guillochè non uniforme o con pattern interrotto",
                    "testo in font non corretto",
                    "smalto con bolle o irregolarità",
                    "indici appiccicati invece di applicati",
                ],
                "authentic_indicators": [
                    "guillochè uniforme e preciso",
                    "indici applicati con precisione",
                    "font proprietario corretto",
                ],
            },
            {
                "check": "calatrava_cross",
                "description": (
                    "La Croce di Calatrava (logo PP) sulla corona di carica: "
                    "deve essere ben proporzionata e simmetrica."
                ),
                "weight": 0.10,
                "fake_indicators": [
                    "croce asimmetrica",
                    "croce assente o mal incisa",
                    "proporzioni errate",
                ],
                "authentic_indicators": [
                    "croce simmetrica e ben proporzionata",
                    "incisione precisa",
                ],
            },
            {
                "check": "movement_quality",
                "description": (
                    "I movimenti Patek sono rifiniti manualmente. "
                    "Côtes de Genève sulle platine, anglage sulle parti, "
                    "polvra bleuies sulle viti."
                ),
                "weight": 0.25,
                "fake_indicators": [
                    "movimento al quarzo in modello che dovrebbe essere meccanico",
                    "côtes de Genève assenti o non uniformi",
                    "viti non bleuies",
                    "rotore di scarsa qualità",
                ],
                "authentic_indicators": [
                    "côtes de Genève uniformi e profondi",
                    "viti bleuies visibili",
                    "anglage perfetto sulle parti del movimento",
                ],
            },
        ],
        "models": {
            "Nautilus": {
                "references": [
                    "5711/1A-010", "5711/1A-011", "5726/1A-010",
                    "5711/1A-014", "5711/110A-001",
                    "5980/1AR-001", "5990/1A-001",
                ],
                "checks": [
                    {
                        "check": "nautilus_case_shape",
                        "description": (
                            "La cassa del Nautilus ha la forma di oblò con le orecchie laterali "
                            "integrate. La lunetta ha 8 viti decorative. "
                            "Il profilo laterale mostra il sistema di chiusura idraulica."
                        ),
                        "weight": 0.25,
                        "fake_indicators": [
                            "forma delle orecchie laterali non simmetrica",
                            "viti decorative non uniformi o assenti",
                            "profilo laterale non corrispondente all'originale",
                            "cassa con spessore errato",
                        ],
                        "authentic_indicators": [
                            "orecchie laterali perfettamente simmetriche",
                            "8 viti decorative uniformi",
                            "profilo laterale corretto",
                        ],
                    },
                    {
                        "check": "horizontal_embossed_dial",
                        "description": (
                            "Il quadrante del Nautilus ha il caratteristico pattern a rilievo "
                            "orizzontale ('horizontal embossed motif'). Su 5711 è grigio-blu "
                            "con riflessi che cambiano con l'angolazione."
                        ),
                        "weight": 0.30,
                        "fake_indicators": [
                            "pattern orizzontale assente o non uniforme",
                            "colore non cambia con l'angolazione",
                            "pattern stampato invece di in rilievo",
                            "riflessi non corretti",
                        ],
                        "authentic_indicators": [
                            "pattern orizzontale in rilievo uniforme",
                            "riflessi che cambiano con l'angolazione",
                        ],
                    },
                    {
                        "check": "integrated_bracelet",
                        "description": (
                            "Il bracciale del Nautilus è integrato nella cassa (stesso disegno). "
                            "Le maglie centrali sono lucide, le laterali satiante. "
                            "La chiusura è nascosta sotto la maglia del bracciale."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "bracciale non integrato visivamente nella cassa",
                            "contrasto opaco/lucido non corretto",
                            "chiusura visibile o di tipo standard",
                            "maglie con giochi o non uniformi",
                        ],
                        "authentic_indicators": [
                            "bracciale integrato visivamente",
                            "maglie uniformi senza giochi",
                            "chiusura nascosta funzionante",
                        ],
                    },
                ],
            },

            "Calatrava": {
                "references": [
                    "5196P-001", "5196G-010", "5227P-001", "5227G-010",
                    "6000G-001", "5153G-010", "3796",
                ],
                "checks": [
                    {
                        "check": "calatrava_dial_simplicity",
                        "description": (
                            "Il Calatrava ha un quadrante minimalista. "
                            "Indici in oro applicati e batons o numeri romani. "
                            "Nessun elemento superfluo. La qualità artigianale è massima."
                        ),
                        "weight": 0.30,
                        "fake_indicators": [
                            "indici non applicati ma stampati",
                            "indici con spaziatura non uniforme",
                            "quadrante con texture o pattern non appropriato per il modello",
                        ],
                        "authentic_indicators": [
                            "indici applicati con ombreggiatura",
                            "spaziatura uniforme e armoniosa",
                        ],
                    },
                    {
                        "check": "hunter_case_hinge",
                        "description": (
                            "Modelli con cassa hunter: la cerniera deve essere invisibile "
                            "quando chiusa e aprirsi senza giochi."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "cerniera visibile quando chiusa",
                            "giochi nell'apertura",
                        ],
                    },
                ],
            },
        },
    },

    # =========================================================================
    # AUDEMARS PIGUET
    # =========================================================================
    "Audemars Piguet": {
        "general": [
            {
                "check": "ap_finishing",
                "description": (
                    "AP usa finiture alternate opache e lucide con angoli netti "
                    "(come Patek). Il metodo di alternanza è caratteristico: "
                    "superfici piane lucide, flanchi satinati."
                ),
                "weight": 0.25,
                "fake_indicators": [
                    "finitura uniforme senza alternanza opaco/lucido",
                    "angoli arrotondati",
                    "superfici con graffi o sbavature",
                ],
                "authentic_indicators": [
                    "alternanza opaco/lucido precisa",
                    "angoli affilati",
                ],
            },
            {
                "check": "ap_logo_quality",
                "description": (
                    "Il logo AP sul quadrante deve essere in proporzione corretta. "
                    "La scritta 'AUDEMARS PIGUET' usa il font proprietario AP "
                    "con spaziatura specifica."
                ),
                "weight": 0.15,
                "fake_indicators": [
                    "font non corretto o spaziatura errata",
                    "logo AP fuori proporzione",
                    "stampa non nitida",
                ],
            },
        ],
        "models": {
            "Royal Oak": {
                "references": [
                    "15400ST.OO.1220ST.01", "15202ST.OO.1240ST.01",
                    "26320ST.OO.1220ST.02", "15500ST.OO.1220ST.01",
                    "15500ST.OO.1220ST.03", "16202ST.OO.1240ST.01",
                    "15400OR.OO.1220OR.01", "15710ST.OO.A002CA.01",
                ],
                "checks": [
                    {
                        "check": "octagonal_bezel_screws",
                        "description": (
                            "La lunetta ottagonale del Royal Oak ha 8 viti in acciaio "
                            "(o oro a seconda del modello). Le viti sono esagonali e "
                            "perfettamente allineate in verticale e orizzontale. "
                            "È la firma visiva principale di AP."
                        ),
                        "weight": 0.30,
                        "fake_indicators": [
                            "meno di 8 viti",
                            "viti non perfettamente allineate",
                            "viti con testa errata (non esagonale)",
                            "viti decorative non avvitate realmente",
                            "lunetta non perfettamente ottagonale (angoli non uniformi)",
                        ],
                        "authentic_indicators": [
                            "8 viti esagonali perfettamente allineate",
                            "lunetta ottagonale simmetrica",
                        ],
                    },
                    {
                        "check": "grande_tapisserie_dial",
                        "description": (
                            "Il quadrante 'Grande Tapisserie' del Royal Oak ha un pattern "
                            "a scacchiera in rilievo. Ogni quadrato deve essere identico "
                            "e perfettamente allineato. Su acciaio: grigio 'bleu ardoise'."
                        ),
                        "weight": 0.30,
                        "fake_indicators": [
                            "pattern Tapisserie non uniforme o con quadrati irregolari",
                            "pattern stampato invece che in rilievo",
                            "colore non corrispondente alla referenza",
                            "pattern interrotto vicino agli indici",
                        ],
                        "authentic_indicators": [
                            "pattern uniforme e in rilievo",
                            "quadrati identici e allineati",
                            "colore corretto per la referenza",
                        ],
                    },
                    {
                        "check": "integrated_bracelet_ap",
                        "description": (
                            "Il bracciale del Royal Oak è integrato nella cassa. "
                            "Maglie centrali lucide, laterali satiante. "
                            "La chiusura AP Fold è integrata nel bracciale."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "transizione cassa-bracciale non fluida",
                            "maglie con giochi o non uniformi",
                            "chiusura non integrata",
                            "peso del bracciale errato",
                        ],
                        "authentic_indicators": [
                            "transizione fluida cassa-bracciale",
                            "maglie piene e uniformi",
                        ],
                    },
                    {
                        "check": "ap_movement",
                        "description": (
                            "Il calibro AP (es. 3120 per 15400) deve avere "
                            "côtes de Genève, anglage e decorazioni tipiche AP. "
                            "Il rotore è in oro e decorato."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "movimento al quarzo su modello meccanico",
                            "côtes de Genève assenti",
                            "rotore non in oro (su modelli che lo prevedono)",
                        ],
                        "authentic_indicators": [
                            "côtes de Genève visibili e uniformi",
                            "rotore in oro decorato",
                        ],
                    },
                ],
            },
        },
    },

    # =========================================================================
    # OMEGA
    # =========================================================================
    "Omega": {
        "general": [
            {
                "check": "omega_logo",
                "description": (
                    "Il simbolo Omega (Ω) sul quadrante deve essere proporzionato "
                    "e ben stampato. La scritta 'OMEGA' usa il font proprietario "
                    "con spaziatura e peso specifici."
                ),
                "weight": 0.20,
                "fake_indicators": [
                    "simbolo Ω mal proporzionato",
                    "font 'OMEGA' con spaziatura errata",
                    "stampa sbavata o non nitida",
                    "simbolo Ω con proporzioni diverse dall'originale",
                ],
                "authentic_indicators": [
                    "simbolo Ω proporzionato e preciso",
                    "font corretto con spaziatura uniforme",
                ],
            },
            {
                "check": "omega_movement",
                "description": (
                    "I movimenti Omega Co-Axial (dal 1999) hanno uno scappamento "
                    "specifico. Il fondello trasparente mostra le decorazioni: "
                    "Côtes de Genève, bleuissage, Genève striping."
                ),
                "weight": 0.20,
                "fake_indicators": [
                    "fondello trasparente che mostra movimento di scarsa qualità",
                    "assenza di decorazioni sul movimento",
                    "movimento al quarzo in modello che dovrebbe essere Co-Axial",
                ],
                "authentic_indicators": [
                    "movimento Co-Axial con decorazioni visibili",
                    "rotor con incisione Omega",
                ],
            },
        ],
        "models": {
            "Speedmaster": {
                "references": [
                    "311.30.42.30.01.005", "310.30.42.50.01.001",
                    "3570.50.00", "145.022", "145.012",
                    "321.30.42.50.01.001",
                ],
                "checks": [
                    {
                        "check": "hesalite_or_sapphire",
                        "description": (
                            "Speedmaster Moonwatch professionale (3570.50): cristallo Hesalite "
                            "(plexiglass) anti-riflesso naturale. "
                            "Moonwatch Master Chronometer: cristallo zaffiro con trattamento AR. "
                            "Il tipo di cristallo deve corrispondere alla referenza."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "zaffiro su referenza che prevede Hesalite",
                            "Hesalite su referenza che prevede zaffiro",
                            "cristallo con bolle o inclusioni",
                        ],
                        "authentic_indicators": [
                            "tipo di cristallo corretto per la referenza",
                        ],
                    },
                    {
                        "check": "asymmetric_case",
                        "description": (
                            "La cassa del Speedmaster è asimmetrica con il fondello "
                            "che copre i pulsanti del cronografo. "
                            "La forma degli horns è caratteristica."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "forma degli horns non corretta",
                            "asimmetria della cassa non presente o errata",
                            "pulsanti in posizione sbagliata",
                        ],
                        "authentic_indicators": [
                            "cassa asimmetrica corretta",
                            "horns della forma giusta",
                        ],
                    },
                    {
                        "check": "tachymeter_bezel_speedy",
                        "description": (
                            "La scala tachimetrica è incisa sull'insert della lunetta in alluminio "
                            "anodizzato nero. I numeri vanno da 500 a 60 (in senso antiorario)."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "scala tachimetrica in senso errato",
                            "numeri mal allineati o con font errato",
                            "insert non in alluminio anodizzato",
                        ],
                        "authentic_indicators": [
                            "scala tachimetrica corretta (500-60)",
                            "insert in alluminio anodizzato di qualità",
                        ],
                    },
                    {
                        "check": "subdials_speedy",
                        "description": (
                            "3 contatori: ore 3 (30 min), ore 6 (12 ore), ore 9 (secondi continui). "
                            "Tutti con font e dimensioni corrette, indici interni ben allineati."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "contatori con font errato",
                            "indici interni mal allineati",
                            "numeri dei contatori con spaziatura errata",
                        ],
                        "authentic_indicators": [
                            "font uniformi e corretti nei contatori",
                            "indici interni perfettamente allineati",
                        ],
                    },
                ],
                "serial_ranges": {
                    "3570.50.00": {"from_year": 1997, "to_year": 2005},
                    "311.30.42.30.01.005": {"from_year": 2012, "to_year": None},
                },
            },

            "Seamaster": {
                "references": [
                    "210.30.42.20.01.001", "210.30.42.20.06.001",
                    "2254.50.00", "2531.80.00",
                    "210.22.42.20.01.001",
                ],
                "checks": [
                    {
                        "check": "wave_dial",
                        "description": (
                            "Il quadrante del Seamaster Professional 300m ha il caratteristico "
                            "pattern a onde. Su modelli recenti è in ceramica. "
                            "Il colore deve essere uniforme e il pattern preciso."
                        ),
                        "weight": 0.25,
                        "fake_indicators": [
                            "pattern a onde non uniforme",
                            "colore non uniforme",
                            "quadrante piatto senza pattern su modelli che lo prevedono",
                        ],
                        "authentic_indicators": [
                            "pattern a onde uniforme e preciso",
                            "colore uniforme",
                        ],
                    },
                    {
                        "check": "helium_escape_valve",
                        "description": (
                            "Il Seamaster Professional 300m ha la valvola di escape elio "
                            "a ore 10. Deve sporgere leggermente dalla cassa e funzionare."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "valvola assente su modello che la prevede",
                            "valvola decorativa non funzionante",
                            "posizione errata (non a ore 10)",
                        ],
                        "authentic_indicators": [
                            "valvola presente a ore 10",
                            "funzionamento verificabile",
                        ],
                    },
                ],
            },
        },
    },

    # =========================================================================
    # TUDOR
    # =========================================================================
    "Tudor": {
        "general": [
            {
                "check": "tudor_shield_logo",
                "description": (
                    "Il logo Tudor (scudo) sul quadrante deve essere proporzionato "
                    "e ben stampato. La scritta 'TUDOR' sotto lo scudo usa font specifico."
                ),
                "weight": 0.20,
                "fake_indicators": [
                    "scudo Tudor non proporzionato",
                    "font 'TUDOR' non corretto",
                    "logo sbavato o non nitido",
                ],
                "authentic_indicators": [
                    "scudo Tudor proporzionato",
                    "font corretto",
                ],
            },
            {
                "check": "tudor_movement",
                "description": (
                    "Tudor usa movimenti ETA o proprietari (calibro MT5612 da 2015). "
                    "I modelli recenti con MT56xx hanno certificazione COSC."
                ),
                "weight": 0.15,
                "fake_indicators": [
                    "movimento al quarzo su modello meccanico",
                    "movimento di qualità evidentemente inferiore visibile dal fondello",
                ],
            },
        ],
        "models": {
            "Black Bay": {
                "references": [
                    "79230N", "79230R", "M79230N-0007",
                    "M79730-0007", "M79212B-0002",
                    "M7941A1A0RU-0002", "M7941A1A0RU-0003",
                ],
                "checks": [
                    {
                        "check": "bb_bezel",
                        "description": (
                            "Lunetta del Black Bay in alluminio anodizzato (nero, rosso, bordeaux, verde). "
                            "La graduazione ha il triangolo a ore 12 senza lume (solo il diving dot è con lume). "
                            "Il 'snowflake' indica il modello con lancette vintage."
                        ),
                        "weight": 0.25,
                        "fake_indicators": [
                            "triangolo ore 12 con lume invece che senza (su modelli che non lo prevedono)",
                            "colore lunetta non corrispondente alla referenza",
                            "insert in materiale diverso dall'alluminio anodizzato",
                            "graduazioni mal allineate",
                        ],
                        "authentic_indicators": [
                            "insert in alluminio anodizzato",
                            "triangolo corretto per il modello",
                            "graduazioni allineate",
                        ],
                    },
                    {
                        "check": "snowflake_hands",
                        "description": (
                            "Le lancette 'Snowflake' del Black Bay hanno la caratteristica "
                            "forma con allargamento alle punte, diversa dalla lancetta standard. "
                            "Devono avere lume sufficiente."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "lancette non snowflake su referenza che le prevede",
                            "lume assente o insufficiente sulle lancette snowflake",
                            "forma delle punte non corretta",
                        ],
                        "authentic_indicators": [
                            "lancette snowflake con forma corretta",
                            "lume presente e funzionante",
                        ],
                    },
                    {
                        "check": "bb_dial",
                        "description": (
                            "Il quadrante Black Bay è disponibile in nero o nero con indici dorati. "
                            "Gli indici circolari devono essere applicati e ricoperti di lume. "
                            "La texture del quadrante è satinata."
                        ),
                        "weight": 0.20,
                        "fake_indicators": [
                            "indici stampati invece di applicati",
                            "texture quadrante lucida invece di satinata",
                            "lume sugli indici assente o di colore errato",
                        ],
                        "authentic_indicators": [
                            "indici applicati con ombreggiatura",
                            "texture satinata corretta",
                            "lume bianco/crema sugli indici",
                        ],
                    },
                    {
                        "check": "rivet_bracelet_or_leather",
                        "description": (
                            "Black Bay è tipicamente fornito con bracciale a rivetti (stile vintage) "
                            "o cinturino in pelle/fabric. Il bracciale a rivetti ha le maglie "
                            "visibilmente 'aperte' ai lati con i rivetti esposti."
                        ),
                        "weight": 0.15,
                        "fake_indicators": [
                            "rivetti decorativi non reali",
                            "maglie non aperte lateralmente",
                            "chiusura di tipo errato per il modello",
                        ],
                        "authentic_indicators": [
                            "rivetti reali e funzionali",
                            "maglie aperte lateralmente",
                        ],
                    },
                ],
                "serial_ranges": {
                    "79230N": {"from_year": 2012, "to_year": 2017},
                    "M79230N-0007": {"from_year": 2017, "to_year": None},
                },
            },
        },
    },
}


def get_rules_for_model(brand: str, model: str) -> dict:
    """
    Restituisce le regole combinate (generali + modello) per brand/modello.
    Cerca in modo case-insensitive.
    """
    brand_key = next(
        (k for k in AUTHENTICATION_RULES if k.lower() == brand.lower()), None
    )
    if not brand_key:
        return {"general": [], "model_specific": [], "found": False}

    brand_rules = AUTHENTICATION_RULES[brand_key]
    general = brand_rules.get("general", [])

    model_key = next(
        (k for k in brand_rules.get("models", {}) if k.lower() == model.lower()),
        None,
    )
    model_data = brand_rules["models"].get(model_key, {}) if model_key else {}
    model_specific = model_data.get("checks", [])

    return {
        "found": True,
        "brand": brand_key,
        "model": model_key or model,
        "general": general,
        "model_specific": model_specific,
        "references": model_data.get("references", []),
        "serial_ranges": model_data.get("serial_ranges", {}),
    }


def get_all_brands() -> list[str]:
    """Restituisce la lista di tutti i brand nel database."""
    return list(AUTHENTICATION_RULES.keys())


def get_models_for_brand(brand: str) -> list[str]:
    """Restituisce la lista di modelli per un brand."""
    brand_key = next(
        (k for k in AUTHENTICATION_RULES if k.lower() == brand.lower()), None
    )
    if not brand_key:
        return []
    return list(AUTHENTICATION_RULES[brand_key].get("models", {}).keys())
