"""
Auctions module — sistema per raccolta, storicizzazione e analisi
dei risultati d'asta mondiali di orologi di lusso.

Componenti:
- database.py   : SQLite schema + CRUD (auctions.db)
- models.py     : Pydantic models
- seed_data.py  : 100+ risultati storici reali
- sentiment.py  : sentiment engine (score 0-100)
- calendar.py   : calendario aste 2025-2026
- router.py     : FastAPI endpoints /auctions/*
- scrapers/     : scrapers Phillips, Christie's, Sotheby's, Antiquorum
"""
from .router import router

__all__ = ["router"]
