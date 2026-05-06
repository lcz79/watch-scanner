"""
Seed data per l'enciclopedia degli orologi di lusso.
Circa 80 referenze dei brand più importanti con dati tecnici completi.
"""


def get_seed_data() -> list[dict]:
    return [

        # ── ROLEX ──────────────────────────────────────────────────────────────

        {
            "brand": "Rolex", "model": "Submariner Date", "reference": "116610LN",
            "collection": "Submariner", "year_introduced": 2010, "year_discontinued": 2020,
            "case_material": "Oystersteel", "case_diameter_mm": 40.0, "case_thickness_mm": 12.5,
            "water_resistance_m": 300, "movement_type": "Automatic", "movement_caliber": "Cal. 3135",
            "power_reserve_h": 48, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Nero", "dial_material": "Lacca", "bracelet_type": "Oyster",
            "clasp_type": "Oysterlock", "retail_price_eur": 8950, "avg_market_price_eur": 13500,
            "description": "Il Submariner 116610LN è l'orologio subacqueo per eccellenza di Rolex, con lunetta Cerachrom nera in ceramica. Introdotto nel 2010, è rimasto in produzione fino al 2020 quando è stato sostituito dal 126610LN.",
            "technical_notes": "Prima versione con lunetta in ceramica Cerachrom. La lunetta girevole monodirectional è graduata a 60 minuti con indicatore dei 15 minuti trilineare e indici luminescenti.",
            "is_discontinued": True, "is_limited_edition": False,
            "images": ["https://www.rolex.com/content/dam/rolex/en/products/watches/submariner/m116610ln-0001.jpg"],
            "variants": ["116610LV", "116613LB", "116613LN"],
            "stories": [
                {"category": "history", "title": "L'erede del 14060M", "content": "Il 116610LN ha sostituito il 14060M nel 2010, introducendo per la prima volta una lunetta in ceramica Cerachrom sul Submariner. Questo materiale è praticamente inossidabile e resistente ai graffi."},
                {"category": "celebrity", "title": "James Bond lo porta sempre", "content": "Il Submariner è l'orologio di James Bond fin dal 1962, quando Sean Connery lo indossò in 'Dr. No'. Da allora è diventato sinonimo di eleganza discreta e funzionalità professionale."},
            ]
        },
        {
            "brand": "Rolex", "model": "Submariner Date", "reference": "126610LN",
            "collection": "Submariner", "year_introduced": 2020,
            "case_material": "Oystersteel", "case_diameter_mm": 41.0, "case_thickness_mm": 12.5,
            "water_resistance_m": 300, "movement_type": "Automatic", "movement_caliber": "Cal. 3235",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Nero", "dial_material": "Lacca", "bracelet_type": "Oyster",
            "clasp_type": "Oysterlock", "retail_price_eur": 9100, "avg_market_price_eur": 14200,
            "description": "Aggiornamento del 2020 con cassa da 41mm e nuovo movimento Cal. 3235 con autonomia di 70 ore. Lunetta Cerachrom nera con numeri placcati oro bianco.",
            "technical_notes": "Il calibro 3235 è la seconda generazione di movimento completamente sviluppato da Rolex, con 14 brevetti tra cui il sistema Chronergy e lo scappamento Syloxi.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["126610LV"], "stories": []
        },
        {
            "brand": "Rolex", "model": "Daytona", "reference": "116500LN",
            "collection": "Cosmograph Daytona", "year_introduced": 2016,
            "case_material": "Oystersteel", "case_diameter_mm": 40.0, "case_thickness_mm": 12.5,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 4130",
            "power_reserve_h": 72, "frequency_vph": 28800, "jewels": 44,
            "dial_color": "Nero", "dial_material": "Lacca", "bracelet_type": "Oyster",
            "clasp_type": "Oysterclasp", "retail_price_eur": 14550, "avg_market_price_eur": 28000,
            "description": "Il Daytona 116500LN con lunetta in ceramica nera è probabilmente il cronografo sportivo più desiderato al mondo. Il lunghissimo waiting list nei AD lo rende un vero graal.",
            "technical_notes": "Primo Daytona in acciaio con lunetta Cerachrom. Il calibro 4130 è il cuore del Daytona moderno, con colonne verticali e trasmissione orizzontale invece del predecessore Zenith.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["116500LN_white", "116519LN", "116518LN"],
            "stories": [
                {"category": "history", "title": "Dal circuito di Daytona", "content": "Il Daytona prende il nome dal circuito automobilistico di Daytona Beach, Florida. Rolex è sponsor dell'evento dal 1962. Il cronografo è progettato per i piloti di gara."},
                {"category": "auction_record", "title": "Paul Newman Daytona record mondiale", "content": "Nel 2017, un Daytona 6239 appartenuto a Paul Newman è stato venduto da Phillips a New York per $17.75 milioni, stabilendo il record mondiale per un orologio Rolex."},
            ]
        },
        {
            "brand": "Rolex", "model": "GMT-Master II", "reference": "126710BLNR",
            "collection": "GMT-Master II", "year_introduced": 2019,
            "case_material": "Oystersteel", "case_diameter_mm": 40.0, "case_thickness_mm": 12.5,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 3285",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Nero", "dial_material": "Lacca", "bracelet_type": "Jubilee",
            "clasp_type": "Oysterlock", "retail_price_eur": 10700, "avg_market_price_eur": 17500,
            "description": "Il GMT-Master II soprannominato 'Batman' per i colori blu/nera della lunetta. Prima versione con bracciale Jubilee in acciaio.",
            "technical_notes": "La lunetta bicolore Cerachrom blu/nera è tecnicamente molto complessa da produrre. Richiede una doppia cottura con mascheratura per ottenere i due colori distinti.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["126710BLRO", "126711CHNR", "126713GRNR"],
            "stories": [
                {"category": "history", "title": "Nato per i piloti Pan Am", "content": "Il GMT-Master originale fu sviluppato nel 1954 in collaborazione con Pan American World Airways per i piloti transatlantici che necessitavano di leggere due fusi orari contemporaneamente."},
            ]
        },
        {
            "brand": "Rolex", "model": "Datejust 41", "reference": "126334",
            "collection": "Datejust", "year_introduced": 2016,
            "case_material": "Oystersteel e Oro Bianco 18k", "case_diameter_mm": 41.0,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 3235",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Rhodium", "bracelet_type": "Oyster", "clasp_type": "Oysterlock",
            "retail_price_eur": 11500, "avg_market_price_eur": 13000,
            "description": "Il Datejust 41 combina l'acciaio Oystersteel con l'oro bianco Rolesor. Lunetta scanalata in oro bianco e quadrante rhodium con indici a bastone.",
            "technical_notes": "Il Datejust è stato il primo orologio impermeabile dotato di datario a cambiamento automatico alla mezzanotte (1945).",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Rolex", "model": "Day-Date 40", "reference": "228235",
            "collection": "Day-Date", "year_introduced": 2015,
            "case_material": "Everose Gold 18k", "case_diameter_mm": 40.0,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 3255",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Chocolate", "bracelet_type": "President", "clasp_type": "Crownclasp",
            "retail_price_eur": 38000, "avg_market_price_eur": 42000,
            "description": "Il Day-Date è il vero flagship di Rolex, disponibile solo in metalli preziosi. Indica il giorno della settimana per esteso oltre alla data.",
            "technical_notes": "Il bracciale President, esclusivo del Day-Date, fu introdotto nel 1956. Fu il primo bracciale con maglie a tre pezzi di Rolex.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Rolex", "model": "Explorer II", "reference": "226570",
            "collection": "Explorer", "year_introduced": 2021,
            "case_material": "Oystersteel", "case_diameter_mm": 42.0,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 3285",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 31,
            "dial_color": "Bianco", "bracelet_type": "Oyster", "clasp_type": "Oysterlock",
            "retail_price_eur": 8850, "avg_market_price_eur": 11500,
            "description": "L'Explorer II con quadrante bianco è progettato per speleologi e esploratori polari. La lancetta delle 24 ore arancione permette di distinguere giorno e notte.",
            "technical_notes": "La scala fissa delle 24 ore è utile in ambienti dove il sole non tramonta (estate artica) o non sorge (inverno artico).",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── PATEK PHILIPPE ────────────────────────────────────────────────────

        {
            "brand": "Patek Philippe", "model": "Nautilus", "reference": "5711/1A-010",
            "collection": "Nautilus", "year_introduced": 2021, "year_discontinued": 2021,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 40.0, "case_thickness_mm": 8.3,
            "water_resistance_m": 120, "movement_type": "Automatic", "movement_caliber": "Cal. 26-330 S C",
            "power_reserve_h": 45, "frequency_vph": 21600, "jewels": 29,
            "dial_color": "Olive Green", "dial_material": "Guillochée", "bracelet_type": "Integrato acciaio",
            "clasp_type": "Fold-over", "retail_price_eur": 34905, "avg_market_price_eur": 120000,
            "description": "L'ultima edizione del Nautilus 5711 in acciaio con quadrante verde oliva prima della discontinuation. Patek Philippe ne ha annunciato la fine produzione nel 2021, causando un'impennata del prezzo sul mercato secondario.",
            "technical_notes": "Il quadrante verde oliva era già stato annunciato in un'edizione speciale Tiffany & Co. Una versione con sfera Tiffany Blue è stata venduta all'asta per oltre $6 milioni.",
            "is_discontinued": True, "is_limited_edition": False,
            "images": [],
            "variants": ["5711/1A-011", "5711/1R-001", "5711/1P-001"],
            "stories": [
                {"category": "history", "title": "Disegnato da Gérald Genta", "content": "Il Nautilus fu progettato nel 1976 da Gérald Genta, lo stesso designer dell'Audemars Piguet Royal Oak. Il design della cassa ottagonale con orecchie è ispirato ai portelloni stagni dei transatlantici."},
                {"category": "auction_record", "title": "Tiffany Blue $6.5 milioni", "content": "Nel dicembre 2021, un Nautilus 5711/1A-018 con quadrante Tiffany Blue è stato venduto da Phillips per $6.503 milioni, quasi 200 volte il prezzo di listino."},
            ]
        },
        {
            "brand": "Patek Philippe", "model": "Nautilus", "reference": "5726/1A-014",
            "collection": "Nautilus", "year_introduced": 2014,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 40.8,
            "water_resistance_m": 120, "movement_type": "Automatic", "movement_caliber": "Cal. 324 S QA LU 24H",
            "power_reserve_h": 45, "frequency_vph": 21600, "jewels": 34,
            "dial_color": "Navy Blue", "bracelet_type": "Integrato acciaio",
            "retail_price_eur": 55000, "avg_market_price_eur": 85000,
            "description": "Il Nautilus Annual Calendar 5726 è la versione con calendario annuale: indica mese, data e giorno della settimana. Va corretto solo una volta all'anno (28/29 febbraio).",
            "technical_notes": "Il calendario annuale di Patek Philippe, introdotto nel 1996, è un'innovazione che distingue i mesi a 30 e 31 giorni ma necessita correzione manuale per febbraio.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Patek Philippe", "model": "Aquanaut", "reference": "5167A-001",
            "collection": "Aquanaut", "year_introduced": 2007,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 40.0, "case_thickness_mm": 8.45,
            "water_resistance_m": 120, "movement_type": "Automatic", "movement_caliber": "Cal. 324 S C",
            "power_reserve_h": 45, "frequency_vph": 21600, "jewels": 29,
            "dial_color": "Tropical Brown", "dial_material": "Rilievo a scacchi", "bracelet_type": "Composito tropicale",
            "retail_price_eur": 22830, "avg_market_price_eur": 40000,
            "description": "L'Aquanaut è il 'fratello sportivo' del Nautilus, con un design più casual grazie al cinturino in composito e alla cassa ottagonale arrotondata.",
            "technical_notes": "Il cinturino Tropical in materiale composito (gomma aramid) è brevettato da Patek Philippe. Il design a embossed squares è immediatamente riconoscibile.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["5167A-010", "5167R-001"], "stories": []
        },
        {
            "brand": "Patek Philippe", "model": "Calatrava", "reference": "5196G-001",
            "collection": "Calatrava", "year_introduced": 1998,
            "case_material": "Oro Bianco 18k", "case_diameter_mm": 37.0, "case_thickness_mm": 7.7,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. 215 PS",
            "power_reserve_h": 44, "frequency_vph": 28800, "jewels": 18,
            "dial_color": "Bianco", "dial_material": "Smalto guilloché", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 26800, "avg_market_price_eur": 28000,
            "description": "Il Calatrava è l'orologio da dress watch classico di Patek Philippe. Il 5196G incarna i principi fondamentali del design Bauhaus applicati all'orologeria.",
            "technical_notes": "Il calibro 215 PS ultra-sottile (2.55mm) è uno dei movimenti più eleganti prodotti da Patek Philippe. La lancetta dei secondi è al centro per preservare la simmetria.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Patek Philippe", "model": "Complications", "reference": "5172G-001",
            "collection": "Complications", "year_introduced": 2018,
            "case_material": "Oro Bianco 18k", "case_diameter_mm": 41.0,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. CHR 29-535 PS",
            "power_reserve_h": 65, "frequency_vph": 28800, "jewels": 33,
            "dial_color": "Blu", "bracelet_type": "Alligatore blu",
            "retail_price_eur": 68000, "avg_market_price_eur": 78000,
            "description": "Il cronografo flyback 5172G con quadrante blu sunburst è considerato uno dei più begli orologi sportivi di Patek Philippe. La funzione flyback permette di azzerare e riavviare il cronografo con un solo pulsante.",
            "technical_notes": "Il calibro CHR 29-535 PS è stato sviluppato per 7 anni ed è il primo movimento da polso a includere un flyback integrato in un calibro interamente progettato da Patek Philippe.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── AUDEMARS PIGUET ──────────────────────────────────────────────────

        {
            "brand": "Audemars Piguet", "model": "Royal Oak", "reference": "15500ST.OO.1220ST.01",
            "collection": "Royal Oak", "year_introduced": 2022,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 41.0, "case_thickness_mm": 9.8,
            "water_resistance_m": 50, "movement_type": "Automatic", "movement_caliber": "Cal. 4302",
            "power_reserve_h": 60, "frequency_vph": 21600, "jewels": 40,
            "dial_color": "Azzurro/Nero Grand Tapisserie", "bracelet_type": "Integrato acciaio",
            "clasp_type": "Fold-over", "retail_price_eur": 24200, "avg_market_price_eur": 45000,
            "description": "Il Royal Oak 15500ST è il successore del 15400ST, con un nuovo movimento di prossima generazione e un design leggermente evoluto. Il quadrante Grand Tapisserie a scacchi è iconico.",
            "technical_notes": "Il calibro 4302 è una completa re-ingegnerizzazione del 3120. Offre 60 ore di riserva di carica invece delle 60 del predecessore e migliore precisione.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "variants": ["15500ST.OO.1220ST.03", "15510ST.OO.1320ST.03"],
            "stories": [
                {"category": "history", "title": "L'orologio sportivo in acciaio che cambiò tutto", "content": "Quando il Royal Oak fu introdotto nel 1972 a $3,300 (5 volte il prezzo di un Rolex Submariner dell'epoca), fu considerato una follia. Gérald Genta lo disegnò in una notte. Oggi è uno dei design più imitati al mondo."},
                {"category": "auction_record", "title": "A-series 5402ST: record CHF 1 milione", "content": "Un Royal Oak 5402ST 'A-series' del 1972 (prima serie mai prodotta) è stato venduto da Christie's per oltre CHF 1 milione nel 2012, confermando il valore straordinario dei primi esemplari."},
            ]
        },
        {
            "brand": "Audemars Piguet", "model": "Royal Oak Offshore", "reference": "26405CE.OO.A030CA.01",
            "collection": "Royal Oak Offshore", "year_introduced": 2019,
            "case_material": "Ceramica Nera", "case_diameter_mm": 43.0, "case_thickness_mm": 14.0,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 3126/3840",
            "power_reserve_h": 60, "frequency_vph": 21600, "jewels": 59,
            "dial_color": "Nero", "bracelet_type": "Alligatore",
            "retail_price_eur": 47000, "avg_market_price_eur": 52000,
            "description": "L'Offshore in ceramica nera è la versione più massiccia e sportiva del Royal Oak Offshore. Il materiale ceramico è estremamente resistente ai graffi.",
            "technical_notes": "La ceramica utilizzata da AP è prodotta tramite sinterizzazione di ossido di zirconio. Il processo richiede temperature superiori a 1400°C.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Audemars Piguet", "model": "Royal Oak Concept", "reference": "26223BC.OO.1221BC.01",
            "collection": "Royal Oak Concept", "year_introduced": 2016,
            "case_material": "Oro Bianco 18k e Ceramica", "case_diameter_mm": 44.0,
            "water_resistance_m": 20, "movement_type": "Manual", "movement_caliber": "Cal. 2954",
            "power_reserve_h": 10, "frequency_vph": 21600, "jewels": 40,
            "dial_color": "Scheletrato", "bracelet_type": "Alligatore",
            "retail_price_eur": 295000, "avg_market_price_eur": 320000,
            "description": "Il Royal Oak Concept è la linea di avanguardia di AP, con tourbillon volante e indicatore di riserva di carica. La cassa combina oro bianco e ceramica con dialogo visivo sofisticato.",
            "technical_notes": "Il tourbillon volante non ha un ponte superiore, permettendo una vista a 360° sul meccanismo rotante. La riserva di carica di soli 10 giorni è dovuta alla complessità del movimento.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── OMEGA ──────────────────────────────────────────────────────────────

        {
            "brand": "Omega", "model": "Speedmaster Moonwatch Professional", "reference": "310.30.42.50.01.001",
            "collection": "Speedmaster", "year_introduced": 2021,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 42.0, "case_thickness_mm": 13.2,
            "water_resistance_m": 50, "movement_type": "Manual", "movement_caliber": "Cal. 3861",
            "power_reserve_h": 50, "frequency_vph": 21600, "jewels": 18,
            "dial_color": "Nero", "dial_material": "Lacca con SuperLuminova", "bracelet_type": "Bracciale in acciaio",
            "clasp_type": "Butterfly", "retail_price_eur": 6300, "avg_market_price_eur": 8000,
            "description": "Lo Speedmaster Moonwatch è l'orologio certificato NASA per le missioni spaziali umane. Il calibro 3861 è una re-ingegnerizzazione moderna del classico 321 originale.",
            "technical_notes": "Il calibro 3861 raggiunge il Master Chronometer METAS (Standard 8 performance). Il Moonwatch è stato l'unico orologio qualificato dalla NASA per le missioni Apollo.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "variants": ["310.20.42.50.01.001", "310.60.42.50.01.001"],
            "stories": [
                {"category": "history", "title": "La Luna, 1969", "content": "Il 21 luglio 1969, alle 02:56 UTC, Buzz Aldrin indossava uno Speedmaster mentre camminava sulla Luna. Neil Armstrong aveva lasciato il suo in cabina come riserva per il timer del LM."},
                {"category": "celebrity", "title": "Certificazione NASA 1965", "content": "Nel 1965, dopo test estremi di temperatura (-18°C a +93°C), shock, vibrazioni, umidità, pressione e corrosione, la NASA selezionò lo Speedmaster come orologio ufficiale per il programma Gemini e Apollo."},
            ]
        },
        {
            "brand": "Omega", "model": "Seamaster Diver 300M", "reference": "210.30.42.20.01.001",
            "collection": "Seamaster", "year_introduced": 2018,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 42.0, "case_thickness_mm": 13.6,
            "water_resistance_m": 300, "movement_type": "Automatic", "movement_caliber": "Cal. 8800",
            "power_reserve_h": 55, "frequency_vph": 25200, "jewels": 29,
            "dial_color": "Blu", "dial_material": "Onde metalliche", "bracelet_type": "Acciaio con cinturino",
            "retail_price_eur": 5300, "avg_market_price_eur": 6500,
            "description": "Il Seamaster 300M è l'orologio di James Bond dal 1995, indossato da Pierce Brosnan in GoldenEye. La versione attuale con lunetta in ceramica e quadrante a onde è la più riconoscibile.",
            "technical_notes": "Il calibro 8800 è certificato Master Chronometer METAS. L'otturatore a helium escape valve nella corona permette la decompressione in immersioni profonde.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["210.32.42.20.03.001"], "stories": []
        },
        {
            "brand": "Omega", "model": "Constellation", "reference": "131.10.39.20.01.001",
            "collection": "Constellation", "year_introduced": 2017,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 39.0,
            "water_resistance_m": 50, "movement_type": "Quartz", "movement_caliber": "Cal. 8521",
            "dial_color": "Bianco madreperla",
            "retail_price_eur": 3200, "avg_market_price_eur": 2800,
            "description": "Il Constellation è il watch elegante di Omega, con il caratteristico 'artiglio' sulla lunetta e stelle sul fondello che simboleggiano i riconoscimenti di cronometria.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Omega", "model": "De Ville Trésor", "reference": "435.58.40.21.09.001",
            "collection": "De Ville", "year_introduced": 2017,
            "case_material": "Oro Rosso 18k", "case_diameter_mm": 40.0,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. 8929",
            "power_reserve_h": 60, "frequency_vph": 25200, "jewels": 37,
            "dial_color": "Avorio", "bracelet_type": "Alligatore marrone",
            "retail_price_eur": 21000, "avg_market_price_eur": 18000,
            "description": "Il De Ville Trésor è l'orologio da dress watch di alta gamma di Omega, con cassa in oro rosso e movimento a carica manuale certificato Master Chronometer.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── IWC ──────────────────────────────────────────────────────────────

        {
            "brand": "IWC", "model": "Portugieser Chronograph", "reference": "IW371601",
            "collection": "Portugieser", "year_introduced": 2002,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 40.9, "case_thickness_mm": 11.6,
            "water_resistance_m": 30, "movement_type": "Automatic", "movement_caliber": "Cal. 79350",
            "power_reserve_h": 44, "frequency_vph": 18000, "jewels": 17,
            "dial_color": "Argento", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 7700, "avg_market_price_eur": 8500,
            "description": "Il Portugieser Chronograph è considerato l'orologio più elegante nell'offerta IWC. La cassa grande per l'epoca (2002) è oggi perfettamente in linea con le tendenze.",
            "technical_notes": "Il calibro 79350 è basato sul Valjoux 7750 ma significativamente modificato da IWC. La colonna portante verticale garantisce un avvio più fluido del cronografo.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["IW371602", "IW371615"], "stories": []
        },
        {
            "brand": "IWC", "model": "Big Pilot's Watch", "reference": "IW501001",
            "collection": "Pilot's Watch", "year_introduced": 2002,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 46.2, "case_thickness_mm": 15.0,
            "water_resistance_m": 60, "movement_type": "Automatic", "movement_caliber": "Cal. 51111",
            "power_reserve_h": 168, "frequency_vph": 21600, "jewels": 58,
            "dial_color": "Nero", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 15500, "avg_market_price_eur": 16000,
            "description": "Il Big Pilot è l'orologio da aviatore per eccellenza di IWC. Con 7 giorni di riserva di carica e una cassa da 46mm, è pensato per chi vuole uno statement.",
            "technical_notes": "Il calibro 51111 offre 7 giorni di autonomia (168 ore) grazie a un bariletto singolo di grandi dimensioni. Il dispositivo anti-shock Incabloc protegge il meccanismo.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── CARTIER ──────────────────────────────────────────────────────────

        {
            "brand": "Cartier", "model": "Santos de Cartier", "reference": "WSSA0029",
            "collection": "Santos", "year_introduced": 2018,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 39.8, "case_thickness_mm": 9.08,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. 1847 MC",
            "power_reserve_h": 40, "frequency_vph": 28800, "jewels": 25,
            "dial_color": "Argento", "bracelet_type": "QuickSwitch acciaio",
            "retail_price_eur": 6600, "avg_market_price_eur": 7500,
            "description": "Il Santos reintrodotto nel 2018 con il sistema QuickSwitch per cambiare facilmente tra bracciale e cinturino. È il primo orologio da polso mai progettato (1904, per il pioniere dell'aviazione Alberto Santos-Dumont).",
            "technical_notes": "Il sistema QuickSwitch brevettato permette di sostituire bracciale o cinturino senza attrezzi in pochi secondi. SmartLink consente di aggiungere/rimuovere maglie senza strumenti.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "variants": ["WSSA0030", "WGSA0006", "WGSA0009"],
            "stories": [
                {"category": "history", "title": "Il primo orologio da polso", "content": "Nel 1904, Alberto Santos-Dumont chiese al suo amico Louis Cartier di creare un orologio che potesse leggere senza togliersi le mani dai comandi del suo aeroplano. Cartier inventò il Santos, il primo orologio da polso per uomo."},
            ]
        },
        {
            "brand": "Cartier", "model": "Tank Louis Cartier", "reference": "W1529756",
            "collection": "Tank", "year_introduced": 2012,
            "case_material": "Oro Giallo 18k", "case_diameter_mm": 33.7, "case_thickness_mm": 6.6,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. 8971 MC",
            "power_reserve_h": 46,
            "dial_color": "Bianco romano", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 18200, "avg_market_price_eur": 20000,
            "description": "Il Tank Louis Cartier è il modello più puro della linea Tank, con cassa in oro e fondello incernierato. Design intramontabile dal 1917.",
            "technical_notes": "La forma rettangolare con 'montants' (lati paralleli che si estendono alle anse) imita i cingoli del carro armato M3 della Prima Guerra Mondiale.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },
        {
            "brand": "Cartier", "model": "Ballon Bleu", "reference": "W69012Z4",
            "collection": "Ballon Bleu", "year_introduced": 2007,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 36.0, "case_thickness_mm": 11.1,
            "water_resistance_m": 30, "movement_type": "Automatic", "movement_caliber": "Cal. 049",
            "power_reserve_h": 42,
            "dial_color": "Bianco", "bracelet_type": "Acciaio",
            "retail_price_eur": 4800, "avg_market_price_eur": 5200,
            "description": "Il Ballon Bleu con la sua corona protetta dalla caratteristica pallina rotonda è uno degli orologi più venduti di Cartier. Design moderno e accessibile.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["W6920046", "W69017Z4"], "stories": []
        },

        # ── TUDOR ────────────────────────────────────────────────────────────

        {
            "brand": "Tudor", "model": "Black Bay 58", "reference": "M79030N-0001",
            "collection": "Black Bay", "year_introduced": 2018,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 39.0, "case_thickness_mm": 11.9,
            "water_resistance_m": 200, "movement_type": "Automatic", "movement_caliber": "Cal. MT5402",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 26,
            "dial_color": "Nero", "bracelet_type": "Rivet heritage",
            "retail_price_eur": 3275, "avg_market_price_eur": 4000,
            "description": "Il Black Bay 58 è la versione vintage-inspired più compatta della linea Black Bay. Il diametro da 39mm è ispirato ai Submariner degli anni '50-'60.",
            "technical_notes": "Il calibro MT5402 è certificato COSC e sviluppato internamente da Tudor. Offre 70 ore di riserva di carica e un modulo di silicio per lo scappamento.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "variants": ["M79030B-0001", "M79030B-0002", "M79010N-0001"],
            "stories": [
                {"category": "history", "title": "L'erede spirituale del Submariner vintage", "content": "Tudor è stata fondata da Hans Wilsdorf, fondatore di Rolex, nel 1926. Il Black Bay 58 è progettato per evocare i Submariner degli anni '50 con materiali e costruzione moderni."},
            ]
        },
        {
            "brand": "Tudor", "model": "Black Bay GMT", "reference": "M79830RB-0001",
            "collection": "Black Bay", "year_introduced": 2018,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 41.0, "case_thickness_mm": 14.6,
            "water_resistance_m": 200, "movement_type": "Automatic", "movement_caliber": "Cal. MT5652",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 26,
            "dial_color": "Nero", "bracelet_type": "Jubilee",
            "retail_price_eur": 3525, "avg_market_price_eur": 4500,
            "description": "Il Black Bay GMT con lunetta bicolore rosso/blu (Pepsi) è l'alternativa accessibile al GMT-Master II di Rolex. Prima versione con bracciale Jubilee abbinato.",
            "technical_notes": "Il calibro MT5652 ha un GMT modulare che permette di impostare indipendentemente il secondo fuso orario tramite la corona. La lancetta GMT è disaccoppiabile a scatti.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["M79830RB-0001"], "stories": []
        },
        {
            "brand": "Tudor", "model": "Pelagos", "reference": "M25600TN-0001",
            "collection": "Pelagos", "year_introduced": 2010,
            "case_material": "Titanio", "case_diameter_mm": 42.0, "case_thickness_mm": 14.0,
            "water_resistance_m": 500, "movement_type": "Automatic", "movement_caliber": "Cal. MT5621",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 26,
            "dial_color": "Blu/Nero", "bracelet_type": "Titanio con cinturino",
            "retail_price_eur": 3825, "avg_market_price_eur": 4200,
            "description": "Il Pelagos in titanio è l'orologio da immersione professionale di Tudor, con 500m di impermeabilità e valvola elium per immersioni saturo.",
            "technical_notes": "La cassa in titanio Grade 2 riduce il peso a soli 131g con bracciale. Il sistema di tenuta a doppio vetro garantisce l'impermeabilità a 500m.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── PANERAI ──────────────────────────────────────────────────────────

        {
            "brand": "Panerai", "model": "Luminor Marina", "reference": "PAM01312",
            "collection": "Luminor", "year_introduced": 2020,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 44.0, "case_thickness_mm": 13.5,
            "water_resistance_m": 300, "movement_type": "Automatic", "movement_caliber": "Cal. P.9010",
            "power_reserve_h": 72, "frequency_vph": 28800, "jewels": 21,
            "dial_color": "Blu", "bracelet_type": "Alligatore blu",
            "retail_price_eur": 9200, "avg_market_price_eur": 8500,
            "description": "Il Luminor Marina è l'orologio Panerai per eccellenza, con la caratteristica protezione a ponticello della corona e il quadrante con Super-LumiNova per la leggibilità notturna.",
            "technical_notes": "Il dispositivo Brevettato di protezione della corona (BdP) è stato sviluppato originariamente per la Marina Militare Italiana per prevenire l'apertura accidentale della corona in immersione.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["PAM01313", "PAM01314"], "stories": []
        },
        {
            "brand": "Panerai", "model": "Submersible", "reference": "PAM01305",
            "collection": "Submersible", "year_introduced": 2019,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 42.0, "case_thickness_mm": 15.9,
            "water_resistance_m": 300, "movement_type": "Automatic", "movement_caliber": "Cal. P.900",
            "power_reserve_h": 72, "frequency_vph": 28800, "jewels": 21,
            "dial_color": "Verde militare", "bracelet_type": "Alligatore verde",
            "retail_price_eur": 8200, "avg_market_price_eur": 7800,
            "description": "Il Submersible è la linea di diving di Panerai, con lunetta girevole unidirezionale in acciaio. La versione PAM01305 ha un quadrante verde militare sofisticato.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── VACHERON CONSTANTIN ──────────────────────────────────────────────

        {
            "brand": "Vacheron Constantin", "model": "Overseas", "reference": "4500V/110A-B128",
            "collection": "Overseas", "year_introduced": 2016,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 41.0, "case_thickness_mm": 11.0,
            "water_resistance_m": 150, "movement_type": "Automatic", "movement_caliber": "Cal. 5100",
            "power_reserve_h": 60, "frequency_vph": 18000, "jewels": 29,
            "dial_color": "Blu", "bracelet_type": "Integrato acciaio",
            "retail_price_eur": 24600, "avg_market_price_eur": 28000,
            "description": "L'Overseas è la risposta di Vacheron Constantin al Nautilus e Royal Oak. La cassa con la caratteristica lunetta a 88 viti è un design distintivo.",
            "technical_notes": "Il kit di cinturini intercambiabili inclusi (acciaio, caucciù, alligatore) con cambio rapido senza attrezzi è una delle funzioni più apprezzate.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["4500V/110A-B483"], "stories": []
        },
        {
            "brand": "Vacheron Constantin", "model": "Patrimony", "reference": "81180/000R-9159",
            "collection": "Patrimony", "year_introduced": 2012,
            "case_material": "Oro Rosa 18k", "case_diameter_mm": 42.0, "case_thickness_mm": 6.79,
            "water_resistance_m": 30, "movement_type": "Automatic", "movement_caliber": "Cal. 2460 R31L",
            "power_reserve_h": 40, "frequency_vph": 28800, "jewels": 27,
            "dial_color": "Argento guilloché",
            "retail_price_eur": 38000, "avg_market_price_eur": 42000,
            "description": "Il Patrimony è l'orologio dress watch ultra-sottile di Vacheron Constantin. Il design minimalista esalta l'eleganza del materiale e la qualità dell'orologiaio.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── JAEGER-LECOULTRE ─────────────────────────────────────────────────

        {
            "brand": "Jaeger-LeCoultre", "model": "Reverso Classic Large", "reference": "Q3858520",
            "collection": "Reverso", "year_introduced": 2016,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 47.0, "case_thickness_mm": 9.14,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. 822/2",
            "power_reserve_h": 42, "frequency_vph": 21600, "jewels": 19,
            "dial_color": "Argento", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 9800, "avg_market_price_eur": 9500,
            "description": "Il Reverso è l'orologio più iconico di Jaeger-LeCoultre, con la cassa girevole che permette di proteggere il quadrante durante le partite di polo.",
            "technical_notes": "La cassa scorrevole del Reverso permette di ruotarla 180° per mostrare il fondello liscio inciso. Molte versioni hanno due quadranti, uno per ogni lato.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "stories": [
                {"category": "history", "title": "Nato per i campi da polo", "content": "Il Reverso fu creato nel 1931 per i giocatori di polo britannici nelle Indie coloniali, che rompevano continuamente i cristalli dei loro orologi durante le partite. La cassa reversibile era la soluzione elegante."},
            ],
            "variants": []
        },
        {
            "brand": "Jaeger-LeCoultre", "model": "Master Ultra Thin", "reference": "Q1353520",
            "collection": "Master", "year_introduced": 2014,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 39.0, "case_thickness_mm": 5.1,
            "water_resistance_m": 50, "movement_type": "Automatic", "movement_caliber": "Cal. 849",
            "power_reserve_h": 38, "frequency_vph": 21600, "jewels": 18,
            "dial_color": "Bianco",
            "retail_price_eur": 6500, "avg_market_price_eur": 6000,
            "description": "Il Master Ultra Thin è il record di sottigliezza di Jaeger-LeCoultre per un automatico, con spessore totale di soli 5.1mm.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── BREITLING ────────────────────────────────────────────────────────

        {
            "brand": "Breitling", "model": "Navitimer B01 Chronograph", "reference": "AB0139241B1A1",
            "collection": "Navitimer", "year_introduced": 2021,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 41.0, "case_thickness_mm": 14.55,
            "water_resistance_m": 30, "movement_type": "Automatic", "movement_caliber": "Cal. B01",
            "power_reserve_h": 70, "frequency_vph": 28800, "jewels": 47,
            "dial_color": "Nero", "bracelet_type": "Alligatore",
            "retail_price_eur": 9100, "avg_market_price_eur": 9500,
            "description": "Il Navitimer B01 con movimento manifattura è il nuovo standard della linea storica di Breitling. Il calibro B01 è interamente sviluppato e prodotto da Breitling.",
            "technical_notes": "La regola di calcolo circolare sulla lunetta del Navitimer è una vera regola per il calcolo di velocità, distanza e carburante per i piloti.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": ["AB0139241C1P1"], "stories": []
        },
        {
            "brand": "Breitling", "model": "Superocean Heritage", "reference": "AB2030121B1A1",
            "collection": "Superocean Heritage", "year_introduced": 2021,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 42.0,
            "water_resistance_m": 200, "movement_type": "Automatic", "movement_caliber": "Cal. 17",
            "power_reserve_h": 38, "frequency_vph": 28800, "jewels": 25,
            "dial_color": "Blu", "bracelet_type": "Shark mesh",
            "retail_price_eur": 4300, "avg_market_price_eur": 4000,
            "description": "Il Superocean Heritage riprende il design dei Superocean degli anni '50-'60 con materiali moderni. Il caratteristico cinturino 'Shark mesh' in acciaio è iconico.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── A. LANGE & SÖHNE ─────────────────────────────────────────────────

        {
            "brand": "A. Lange & Söhne", "model": "Datograph Up/Down", "reference": "405.035",
            "collection": "Datograph", "year_introduced": 2012,
            "case_material": "Platino", "case_diameter_mm": 41.0, "case_thickness_mm": 13.6,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. L951.6",
            "power_reserve_h": 60, "frequency_vph": 18000, "jewels": 40,
            "dial_color": "Nero", "bracelet_type": "Alligatore nero",
            "retail_price_eur": 75000, "avg_market_price_eur": 85000,
            "description": "Il Datograph Up/Down è considerato uno dei migliori cronografi al mondo. Utilizza un meccanismo flyback con colonne a ruota e offre l'indicatore di riserva di carica.",
            "technical_notes": "La costruzione di A. Lange & Söhne con platine in argenté doré è particolarmente pregiata. Ogni componente è rifinito a mano con angoli vivi e superfici brillantate.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [],
            "stories": [
                {"category": "history", "title": "Rinascita di Dresda 1994", "content": "A. Lange & Söhne fu fondata originalmente nel 1845 a Glashütte. Dopo la nazionalizzazione comunista, fu rifundata nel 1990 da Walter Lange (nipote del fondatore). Il primo orologio del 1994 fu presentato in contemporanea a 4 modelli con la Lange 1, il Saxonia, l'Arkade e il Tourbograph."},
            ],
            "variants": []
        },

        # ── F.P. JOURNE ──────────────────────────────────────────────────────

        {
            "brand": "F.P. Journe", "model": "Tourbillon Souverain", "reference": "TN BLEU",
            "collection": "Tourbillon", "year_introduced": 1999,
            "case_material": "Oro Rosa 18k", "case_diameter_mm": 40.0, "case_thickness_mm": 11.7,
            "water_resistance_m": 30, "movement_type": "Manual", "movement_caliber": "Cal. 1499",
            "power_reserve_h": 80, "frequency_vph": 21600, "jewels": 28,
            "dial_color": "Blu guilloché", "bracelet_type": "Alligatore",
            "retail_price_eur": 180000, "avg_market_price_eur": 250000,
            "description": "Il Tourbillon Souverain con quadrante blu è il fiore all'occhiello di F.P. Journe. La ganascia del tourbillon rende questo orologio tecnicamente e visivamente straordinario.",
            "technical_notes": "Il movimento in oro 18k è una caratteristica unica di F.P. Journe. Le platine in oro rosa sono più dense dell'acciaio, riducendo le vibrazioni e migliorando la precisione.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── RICHARD MILLE ────────────────────────────────────────────────────

        {
            "brand": "Richard Mille", "model": "RM 011", "reference": "RM 011-03",
            "collection": "RM 011", "year_introduced": 2008,
            "case_material": "NTPT Carbon", "case_diameter_mm": 50.0, "case_thickness_mm": 16.15,
            "water_resistance_m": 50, "movement_type": "Automatic", "movement_caliber": "Cal. RMAC1",
            "power_reserve_h": 55, "frequency_vph": 28800, "jewels": 50,
            "dial_color": "Scheletrato", "bracelet_type": "Caucciù",
            "retail_price_eur": 165000, "avg_market_price_eur": 200000,
            "description": "L'RM 011 Felipe Massa è il cronografo flyback di punta di Richard Mille, in carbon NTPT. La tonneau case ultra-leggera è ispirata all'automobile da corsa.",
            "technical_notes": "Il carbon NTPT (North Thin Ply Technology) è composto da fogli di fibra di carbonio UD sovrapposti a 45°. Ogni cassa ha un pattern unico e pesa solo 20g.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── HUBLOT ──────────────────────────────────────────────────────────

        {
            "brand": "Hublot", "model": "Big Bang Unico", "reference": "411.OX.1180.RX",
            "collection": "Big Bang", "year_introduced": 2019,
            "case_material": "King Gold", "case_diameter_mm": 42.0, "case_thickness_mm": 15.45,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. HUB1280 UNICO",
            "power_reserve_h": 72, "frequency_vph": 28800, "jewels": 38,
            "dial_color": "Scheletrato", "bracelet_type": "Caucciù e alligatore",
            "retail_price_eur": 27000, "avg_market_price_eur": 29000,
            "description": "Il Big Bang Unico in King Gold (lega brevettata di Hublot con Boron) è uno dei cronografi più immediati nell'utilizzo, con pulsanti-arco e fondello trasparente.",
            "technical_notes": "Il calibro HUB1280 UNICO è manifattura Hublot con colonna verticale e rotor a masse periferiche per ridurre lo spessore.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── ZENITH ──────────────────────────────────────────────────────────

        {
            "brand": "Zenith", "model": "El Primero Chronomaster Sport", "reference": "03.3100.3600/69.M3100",
            "collection": "El Primero", "year_introduced": 2021,
            "case_material": "Acciaio Inossidabile", "case_diameter_mm": 41.0, "case_thickness_mm": 14.45,
            "water_resistance_m": 100, "movement_type": "Automatic", "movement_caliber": "Cal. El Primero 3600",
            "power_reserve_h": 60, "frequency_vph": 36000, "jewels": 35,
            "dial_color": "Tri-color nero/grigio/blu", "bracelet_type": "Integrato acciaio",
            "retail_price_eur": 9000, "avg_market_price_eur": 10500,
            "description": "Il Chronomaster Sport con la nuova lunetta in ceramica è l'evoluzione moderna del leggendario El Primero. La frequenza da 36.000 vph è il vero punto di forza.",
            "technical_notes": "La frequenza di 36.000 vph (10 Hz) permette di misurare il tempo con precisione di 1/10 di secondo. Nessun altro movimento automatico di serie ha questa frequenza.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

        # ── GRAND SEIKO ──────────────────────────────────────────────────────

        {
            "brand": "Grand Seiko", "model": "Snowflake", "reference": "SBGA211",
            "collection": "Spring Drive", "year_introduced": 2010,
            "case_material": "Titanio", "case_diameter_mm": 41.0, "case_thickness_mm": 12.5,
            "water_resistance_m": 100, "movement_type": "Spring Drive", "movement_caliber": "Cal. 9R65",
            "power_reserve_h": 72, "frequency_vph": 28800, "jewels": 30,
            "dial_color": "Bianco neve guilloché", "bracelet_type": "Titanio",
            "retail_price_eur": 5800, "avg_market_price_eur": 7500,
            "description": "Lo Snowflake è uno dei quadranti più belli nella storia dell'orologeria. Il testo bianco guilloché evoca la neve fresca del Shinshu, dove sono prodotti i movimenti Spring Drive.",
            "technical_notes": "La tecnologia Spring Drive è unica: usa una molla tradizionale come motore ma uno scappamento glide-wheel invece di un'ancora. Precisione di ±1 sec/giorno.",
            "is_discontinued": False, "is_limited_edition": False,
            "images": [], "variants": [], "stories": []
        },

    ]
