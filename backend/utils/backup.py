"""
Backup automatico dei database SQLite.
Copia tutti i .db in data/ → data/backups/ con timestamp.
Mantieni ultimi 7 backup per DB. Scheduler: ogni 24h.
"""
import asyncio
import shutil
from datetime import datetime
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("backup")

DATA_DIR = Path(__file__).parent.parent / "data"
BACKUP_DIR = DATA_DIR / "backups"
MAX_BACKUPS = 7


def backup_all_dbs() -> list[str]:
    """Copia tutti i .db in data/backups/ con timestamp. Ritorna i nomi creati."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    created = []

    for db_file in DATA_DIR.glob("*.db"):
        dest = BACKUP_DIR / f"{db_file.stem}_{ts}.db"
        try:
            shutil.copy2(db_file, dest)
            created.append(dest.name)
            logger.debug(f"Backup: {db_file.name} → {dest.name}")
        except Exception as e:
            logger.warning(f"Backup error per {db_file.name}: {e}")

        # Pruning: mantieni solo gli ultimi MAX_BACKUPS per questo DB
        old = sorted(
            BACKUP_DIR.glob(f"{db_file.stem}_*.db"),
            key=lambda f: f.stat().st_mtime,
        )
        for f in old[:-MAX_BACKUPS]:
            try:
                f.unlink()
                logger.debug(f"Rimosso backup vecchio: {f.name}")
            except Exception:
                pass

    logger.info(f"Backup completato: {len(created)} file → {BACKUP_DIR}")
    return created


def get_backup_status() -> dict:
    """Ritorna info sull'ultimo backup disponibile."""
    if not BACKUP_DIR.exists():
        return {"last_backup": None, "backup_count": 0}

    all_backups = sorted(BACKUP_DIR.glob("*.db"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not all_backups:
        return {"last_backup": None, "backup_count": 0}

    latest = all_backups[0]
    mtime = latest.stat().st_mtime
    last_backup = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    return {"last_backup": last_backup, "backup_count": len(all_backups)}


async def start_backup_scheduler():
    """Backup ogni 24h, prima esecuzione dopo 60s dall'avvio."""
    logger.info("Backup scheduler avviato (ogni 24h)")
    await asyncio.sleep(60)
    while True:
        try:
            created = backup_all_dbs()
            logger.info(f"Backup scheduler: {len(created)} file salvati")
        except Exception as e:
            logger.error(f"Backup scheduler error: {e}")
        await asyncio.sleep(24 * 3600)
