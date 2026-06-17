# Watch Reference Scraping Pipeline

Scraping di WatchBase (watchbase.com) per costruire il database completo
delle referenze orologi da usare nell'autocomplete di WatchScanner.

## Architettura

```
brands (config.py)
  └─ brand_spider.py  →  collezioni per brand
       └─ reference_spider.py  →  dettagli ogni referenza
            └─ normalize.py  →  pulisce + merge con catalog manuale
                 └─ watches_full.json + watches.json
```

## Uso

```bash
cd backend/catalog/pipeline

# Installa dipendenze
pip install requests beautifulsoup4

# Scraping completo (tutti i brand in config.py)
python3 run_pipeline.py

# Solo un brand (riprende dal punto in cui si era fermato)
python3 run_pipeline.py --brand rolex
python3 run_pipeline.py --brand omega

# Merge senza ri-scrapare (usa watches_full.json già scritto)
python3 run_pipeline.py --merge-only

# Riparte da zero
python3 run_pipeline.py --reset
```

## Output

- `watches_full.json` — tutti i record scraped (raw)
- `../watches.json` — merged con catalogo manuale (`build_catalog.py`);
  i record manuali hanno priorità (dati curati > scraped)

## Sorgente: WatchBase

- URL brand:      `https://watchbase.com/{brand-slug}/`
- URL collection: `https://watchbase.com/{brand-slug}/{collection-slug}`
- URL referenza:  `https://watchbase.com/{brand-slug}/{collection-slug}/{ref-slug}`

Il pipeline rispetta il server: delay 1.5s tra richieste, 3s tra brand.
La cache su `.cache/` evita di ri-scrapare URL già visitati.

## Brand coperti (25)

Rolex, Omega, Patek Philippe, Audemars Piguet, Vacheron Constantin,
TAG Heuer, Tudor, IWC, Breitling, Panerai, Cartier, Jaeger-LeCoultre,
A. Lange & Söhne, Richard Mille, Hublot, Zenith, Longines, Seiko,
Grand Seiko, Nomos, Glashütte Original, F.P. Journe, H. Moser & Cie,
MB&F, Urwerk.
