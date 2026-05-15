"""
Backup automatico SQLite per WatchScanner.
Copia tutti i .db in data/ → data/backups/ con timestamp.
Mantieni solo gli ultimi 7 backup per ogni DB.
"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("backup")

DATA_DIR = Path(__file__).parent.parent / "data"
BACKUPS_DIR = DATA_DIR / "backups"
MAX_BACKUPS_PER_DB = 7


def backup_all_dbs() -> list[str]:
    """
    Copia tutti i file .db presenti in data/ in data/backups/ con timestamp nel nome.
    Mantieni solo gli ultimi MAX_BACKUPS_PER_DB backup per ogni DB.
    Ritorna la lista dei file di backup creati.
    """
    if not DATA_DIR.exists():
        logger.warning(f"Directory data/ non trovata: {DATA_DIR}")
        return []

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    created = []

    db_files = list(DATA_DIR.glob("*.db"))
    if not db_files:
        logger.info("Nessun file .db trovato in data/")
        return []

    for db_path in db_files:
        stem = db_path.stem  # es. "news"
        backup_name = f"{stem}_{timestamp}.db"
        backup_path = BACKUPS_DIR / backup_name

        try:
            shutil.copy2(db_path, backup_path)
            created.append(backup_name)
            logger.info(f"Backup creato: {backup_name} ({backup_path.stat().st_size // 1024} KB)")
        except Exception as e:
            logger.error(f"Errore backup {db_path.name}: {e}")
            continue

        # Mantieni solo gli ultimi MAX_BACKUPS_PER_DB backup per questo DB
        existing = sorted(
            BACKUPS_DIR.glob(f"{stem}_*.db"),
            key=lambda p: p.stat().st_mtime,
        )
        if len(existing) > MAX_BACKUPS_PER_DB:
            to_delete = existing[: len(existing) - MAX_BACKUPS_PER_DB]
            for old in to_delete:
                try:
                    old.unlink()
                    logger.info(f"Backup vecchio rimosso: {old.name}")
                except Exception as e:
                    logger.warning(f"Impossibile rimuovere {old.name}: {e}")

    logger.info(f"Backup completato: {len(created)} file creati")
    return created


def get_backup_status() -> dict:
    """Ritorna info sui backup più recenti per ogni DB."""
    if not BACKUPS_DIR.exists():
        return {"backups_dir": str(BACKUPS_DIR), "dbs": {}}

    dbs: dict[str, dict] = {}
    for backup_file in sorted(BACKUPS_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True):
        # Estrai il nome del DB dal filename (rimuove il timestamp)
        parts = backup_file.stem.rsplit("_", 2)
        if len(parts) < 3:
            continue
        db_name = parts[0]
        if db_name not in dbs:
            dbs[db_name] = {
                "latest_backup": backup_file.name,
                "latest_mtime": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                "size_kb": backup_file.stat().st_size // 1024,
                "count": 0,
            }
        dbs[db_name]["count"] += 1

    return {
        "backups_dir": str(BACKUPS_DIR),
        "dbs": dbs,
    }


async def start_backup_scheduler() -> None:
    """Async loop che esegue il backup ogni 24h."""
    # Prima run dopo 1 minuto (lascia avviare il resto del sistema)
    await asyncio.sleep(60)

    while True:
        try:
            logger.info("Avvio backup schedulato SQLite...")
            created = backup_all_dbs()
            logger.info(f"Backup schedulato completato: {len(created)} file")
        except Exception as e:
            logger.error(f"Errore nel backup schedulato: {e}")

        # Aspetta 24h
        await asyncio.sleep(24 * 60 * 60)
