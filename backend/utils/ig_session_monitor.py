"""
Monitor della sessione browser Instagram per WatchScanner.
Controlla periodicamente la validità del cookie sessionid e invia
un'email di avviso quando la sessione è scaduta o in scadenza.
"""

import asyncio
import json
import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from config import Settings

logger = get_logger("ig_session_monitor")

DATA_DIR = Path(__file__).parent.parent / "data"
AUTH_STATE_FILE = DATA_DIR / "ig_browser_auth.json"

ALERT_RECIPIENT = "luca.campagnoli181279@gmail.com"
EXPIRY_WARNING_DAYS = 14  # avvisa se mancano meno di 14 giorni alla scadenza


def check_session_valid() -> tuple[bool, str]:
    """
    Legge data/ig_browser_auth.json e controlla la validità del cookie sessionid.

    Ritorna:
        (True, "Sessione valida — scade il YYYY-MM-DD") se il cookie è presente e non scaduto
        (False, "<motivo>") in caso contrario
    """
    if not AUTH_STATE_FILE.exists():
        return False, f"File auth non trovato: {AUTH_STATE_FILE}"

    try:
        data = json.loads(AUTH_STATE_FILE.read_text())
    except Exception as e:
        return False, f"Impossibile leggere {AUTH_STATE_FILE}: {e}"

    # Il file Playwright salva i cookie come lista sotto la chiave "cookies"
    cookies: list[dict] = []
    if isinstance(data, dict):
        cookies = data.get("cookies", [])
    elif isinstance(data, list):
        cookies = data

    session_cookie = next((c for c in cookies if c.get("name") == "sessionid"), None)

    if not session_cookie:
        return False, "Cookie sessionid non presente nel file auth"

    expiration = session_cookie.get("expires") or session_cookie.get("expirationDate")
    if expiration is None:
        # Cookie di sessione senza scadenza esplicita — consideriamo valido
        return True, "Sessione valida (nessuna scadenza esplicita)"

    try:
        expiration = float(expiration)
    except (TypeError, ValueError):
        return False, f"Formato expirationDate non valido: {expiration}"

    now_ts = datetime.now(timezone.utc).timestamp()

    if expiration <= 0:
        # Playwright a volte salva -1 per i cookie di sessione senza scadenza
        return True, "Sessione valida (nessuna scadenza esplicita)"

    if expiration < now_ts:
        expired_at = datetime.fromtimestamp(expiration).strftime("%Y-%m-%d %H:%M")
        return False, f"Sessione scaduta il {expired_at}"

    expires_dt = datetime.fromtimestamp(expiration)
    days_left = (expires_dt - datetime.now()).days
    expires_str = expires_dt.strftime("%Y-%m-%d")

    return True, f"Sessione valida — scade il {expires_str} ({days_left} giorni rimanenti)"


def _days_until_expiry() -> int | None:
    """
    Ritorna i giorni alla scadenza del sessionid.
    None se non calcolabile o se la sessione è senza scadenza.
    """
    if not AUTH_STATE_FILE.exists():
        return None

    try:
        data = json.loads(AUTH_STATE_FILE.read_text())
        cookies = data.get("cookies", []) if isinstance(data, dict) else data
        session_cookie = next((c for c in cookies if c.get("name") == "sessionid"), None)
        if not session_cookie:
            return None
        expiration = session_cookie.get("expires") or session_cookie.get("expirationDate")
        if expiration is None or float(expiration) <= 0:
            return None
        expiration = float(expiration)
        days_left = (datetime.fromtimestamp(expiration) - datetime.now()).days
        return days_left
    except Exception:
        return None


def send_session_expiry_alert(settings: "Settings", reason: str) -> bool:
    """
    Invia email via Gmail SMTP a ALERT_RECIPIENT quando la sessione è scaduta
    o in scadenza. Usa settings.email_from e settings.email_password.
    """
    from_addr = settings.email_from
    password = settings.email_password

    if not from_addr or not password:
        logger.warning("Credenziali email non configurate — impossibile inviare alert sessione IG")
        return False

    subject = "⚠️ WatchScanner — Sessione Instagram in scadenza"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;background:#18181b;color:#f4f4f5;padding:32px;border-radius:16px">
      <h2 style="color:#fbbf24;margin-bottom:8px">⚠️ Sessione Instagram</h2>
      <p style="color:#a1a1aa;margin-top:0">WatchScanner ha rilevato un problema con la sessione browser Instagram.</p>
      <hr style="border-color:#3f3f46;margin:20px 0">
      <p style="font-size:1.1em">{reason}</p>
      <hr style="border-color:#3f3f46;margin:20px 0">
      <p style="color:#a1a1aa;font-size:0.9em">
        Per rinnovare la sessione, esegui:<br>
        <code style="background:#27272a;padding:4px 8px;border-radius:4px">POST /stories/setup</code>
      </p>
      <p style="color:#52525b;font-size:12px;margin-top:24px">
        Rilevato il {datetime.now().strftime("%Y-%m-%d %H:%M")}
      </p>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ALERT_RECIPIENT
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, ALERT_RECIPIENT, msg.as_string())

        logger.info(f"Alert sessione IG inviato a {ALERT_RECIPIENT}")
        return True
    except Exception as e:
        logger.error(f"Errore invio alert sessione IG: {e}")
        return False


async def start_session_monitor(settings: "Settings") -> None:
    """
    Async loop che controlla la validità della sessione Instagram ogni 24h.
    Invia email se la sessione è scaduta o mancano meno di EXPIRY_WARNING_DAYS giorni.
    """
    # Prima run dopo 5 minuti
    await asyncio.sleep(5 * 60)

    while True:
        try:
            valid, message = check_session_valid()
            days_left = _days_until_expiry()

            if not valid:
                logger.warning(f"Sessione IG non valida: {message}")
                send_session_expiry_alert(settings, message)
            elif days_left is not None and days_left < EXPIRY_WARNING_DAYS:
                warning_msg = f"La sessione Instagram scade tra {days_left} giorni ({message})"
                logger.warning(warning_msg)
                send_session_expiry_alert(settings, warning_msg)
            else:
                logger.info(f"Sessione IG OK: {message}")
        except Exception as e:
            logger.error(f"Errore nel monitor sessione IG: {e}")

        # Aspetta 24h
        await asyncio.sleep(24 * 60 * 60)
