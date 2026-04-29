# WatchScanner — Orchestratore Multi-Agente

## Progetto
Sistema agentico per trovare il prezzo minimo su orologi di lusso.
- **Backend**: FastAPI + Python → `/backend/`
- **Frontend**: React + TailwindCSS → `/frontend/src/`
- **Stack**: asyncio, httpx, Playwright, instagrapi, pydantic

## Regola principale
Quando l'utente dà un task di sviluppo, **analizza sempre il task e lancia gli agenti appropriati in parallelo** usando il tool Agent con `run_in_background: true`. Non fare tutto da solo in sequenza.

---

## Agenti disponibili

### 🎨 AgentUX
**Responsabilità**: esperienza utente, design visivo, copy, animazioni, accessibilità
**File**: `frontend/src/pages/`, `frontend/src/components/`, stili Tailwind
**Focus**: il risultato deve sembrare professionale e fluido. Pensa prima all'utente finale.
**Non toccare**: backend, API, logica di business

### ⚛️ AgentFrontend
**Responsabilità**: logica React, TanStack Query, state management, integrazione API, TypeScript
**File**: `frontend/src/lib/api.ts`, `frontend/src/types/index.ts`, hooks, mutations
**Focus**: dati corretti, gestione errori, performance, tipi TypeScript precisi
**Non toccare**: design visivo (solo struttura), backend Python

### 🔧 AgentBackend
**Responsabilità**: FastAPI, endpoint, Pydantic schemas, config, business logic
**File**: `backend/main.py`, `backend/config.py`, `backend/models/`, `backend/orchestrator.py`
**Focus**: API corrette, validazione input, performance, compatibilità con frontend
**Non toccare**: scrapers, frontend

### 🕷️ AgentScraper
**Responsabilità**: scrapers web, agenti Python, anti-bot, parsing dati, Instagram
**File**: `backend/scrapers/`, `backend/agents/`
**Focus**: affidabilità, gestione errori, rate limiting, dati puliti
**Non toccare**: frontend, endpoint API

### ✅ AgentQA
**Responsabilità**: verifica che le modifiche degli altri agenti siano coerenti tra loro
**File**: legge tutto il codice modificato dagli altri agenti
**Focus**: trova incongruenze (es. campo aggiunto nel backend ma non nel tipo TypeScript), errori di import, logica rotta
**Output**: lista di problemi trovati + fix

---

## Come orchestrare un task

1. **Analizza** il task → quali agenti servono?
2. **Lancia in parallelo** tutti gli agenti necessari (`run_in_background: true`)
3. **Mentre lavorano**, pensa a potenziali conflitti tra i loro cambiamenti
4. **Quando finiscono**, leggi i risultati e applica le modifiche
5. **Lancia AgentQA** per verifica finale
6. **Comunica** all'utente cosa è stato fatto

## Regole di coordinamento

- Se AgentUX e AgentFrontend toccano lo stesso file `.tsx`, AgentUX gestisce il markup/stili, AgentFrontend gestisce la logica
- AgentBackend definisce sempre prima lo schema Pydantic → AgentFrontend aggiorna il tipo TypeScript di conseguenza
- AgentScraper non dipende dagli altri → può sempre girare in parallelo
- AgentQA gira sempre per ultimo, dopo che gli altri hanno finito

## Struttura progetto (riferimento rapido)

```
backend/
├── main.py              # FastAPI app + lifespan + endpoints
├── config.py            # Settings da .env
├── orchestrator.py      # Coordina gli agenti scraper
├── models/schemas.py    # Pydantic models
├── agents/
│   ├── marketplace_agent.py   # Chrono24 + eBay via Playwright
│   ├── social_agent.py        # Instagram posts
│   └── alert_checker.py       # Job 30min per gli alert
├── scrapers/
│   ├── chrono24.py
│   ├── ebay.py
│   ├── instagram.py
│   └── instagram_stories.py   # OCR stories
└── utils/
    ├── notifier.py      # Email + WhatsApp + Telegram
    └── logger.py

frontend/src/
├── pages/
│   ├── SearchPage.tsx   # Ricerca + risultati
│   └── AlertsPage.tsx   # Gestione alert
├── lib/api.ts           # Chiamate HTTP al backend
└── types/index.ts       # TypeScript interfaces
```

## Stato attuale del progetto
- ✅ Chrono24 scraper funzionante (51 risultati, anti-bot attivo)
- ✅ eBay scraper funzionante
- ✅ Instagram posts (filtra per referenza in caption)
- ✅ Instagram Stories con OCR tesseract (job ogni 6h)
- ✅ Alert system con email notifiche (Gmail SMTP)
- ✅ Alert checker background job (ogni 30 min)
- ⚠️ Instagram challenge frequente su account nuovo
- ❌ Nessun test automatico
- ❌ Nessun database persistente (alert in memoria)
