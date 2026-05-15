"""
Monitor sessione Instagram.
Controlla ogni 24h se il cookie sessionid è valido.
Invia email se scaduto o mancano meno di 14 giorni.
"""
import asyncio
import json
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("ig_session_monitor")

AUTH_FILE = Path(__file__).parent.parent / "data" / "ig_browser_auth.json"
ALERT_EMAIL = "luca.campagnoli181279@gmail.com"
WARNING_DAYS = 14


def check_session_valid() -> tuple[bool, str]:
    """
    Legge ig_browser_auth.json e controlla il cookie sessionid.
    Ritorna (valida: bool, messaggio: str).
    """
    if not AUTH_FILE.exists():
        return False, "File auth non trovato"

    try:
        state = json.loads(AUTH_FILE.read_text())
        cookies = state.get("cookies", [])
        session = next(
            (c for c in cookies if c.get("name") == "sessionid" and "instagram" in c.get("domain", "")),
            None,
        )
        if not session:
            return False, "Cookie sessionid non trovato"

        # expires può essere -1 (session cookie) o un Unix timestamp
        exp = session.get("expires", session.get("expirationDate", -1))
        if exp == -1 or exp is None:
            # Cookie di sessione senza scadenza esplicita — consideriamo valido
            return True, "Sessione attiva (nessuna scadenza esplicita)"

        exp_dt = datetime.fromtimestamp(float(exp), tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        days_left = (exp_dt - now).days

        if days_left < 0:
            return False, f"Sessione scaduta il {exp_dt.strftime('%Y-%m-%d')}"
        if days_left < WARNING_DAYS:
            return True, f"Sessione valida ma scade tra {days_left} giorni ({exp_dt.strftime('%Y-%m-%d')})"
        return True, f"Sessione valida — scade il {exp_dt.strftime('%Y-%m-%d')} ({days_left} giorni)"

    except Exception as e:
        return False, f"Errore lettura auth: {e}"


def get_days_left() -> int | None:
    """Ritorna i giorni rimasti alla scadenza, o None se non determinabile."""
    if not AUTH_FILE.exists():
        return None
    try:
        state = json.loads(AUTH_FILE.read_text())
        cookies = state.get("cookies", [])
        session = next(
            (c for c in cookies if c.get("name") == "sessionid" and "instagram" in c.get("domain", "")),
            None,
        )
        if not session:
            return None
        exp = session.get("expires", session.get("expirationDate", -1))
        if exp == -1 or exp is None:
            return 999  # nessuna scadenza
        exp_dt = datetime.fromtimestamp(float(exp), tz=timezone.utc)
        return max(0, (exp_dt - datetime.now(tz=timezone.utc)).days)
    except Exception:
        return None


def send_session_expiry_alert(settings, message: str):
    """Invia email di allerta sessione Instagram via Gmail SMTP."""
    if not settings.email_from or not settings.email_password:
        logger.warning("Email non configurata — skip alert sessione IG")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "⚠️ WatchScanner — Sessione Instagram in scadenza"
        msg["From"] = settings.email_from
        msg["To"] = ALERT_EMAIL

        body = f"""
        <html><body style="font-family:sans-serif;background:#18181b;color:#e4e4e7;padding:32px">
        <h2 style="color:#facc15">⚠️ WatchScanner — Sessione Instagram</h2>
        <p style="font-size:16px">{message}</p>
        <p>Per rinnovare la sessione:</p>
        <ol>
          <li>Apri il progetto in locale</li>
          <li>Lancia: <code>POST /stories/setup</code> con username e password</li>
          <li>Completa il login nel browser Chrome che si apre</li>
          <li>Rideploya: <code>./deploy.sh 157.230.112.22</code></li>
        </ol>
        <p style="color:#71717a;font-size:12px">WatchScanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(settings.email_from, settings.email_password)
            s.sendmail(settings.email_from, ALERT_EMAIL, msg.as_string())
        logger.info("Alert sessione Instagram inviato via email")
    except Exception as e:
        logger.error(f"Errore invio email alert: {e}")


async def start_session_monitor(settings):
    """Controlla la sessione ogni 24h. Invia email se scaduta o < 14 giorni."""
    logger.info("IG session monitor avviato (ogni 24h)")
    await asyncio.sleep(300)  # primo check dopo 5 minuti
    while True:
        try:
            valid, message = check_session_valid()
            logger.info(f"[ig_monitor] {message}")
            if not valid or "scade tra" in message:
                send_session_expiry_alert(settings, message)
        except Exception as e:
            logger.error(f"IG session monitor error: {e}")
        await asyncio.sleep(24 * 3600)
