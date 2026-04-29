"""
Notifiche per gli alert WatchScanner.
Supporta: Email (SMTP Gmail) + WhatsApp (CallMeBot, gratuito) + Telegram
"""

import httpx
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
from utils.logger import get_logger

logger = get_logger("notifier")


# ── Telegram ─────────────────────────────────────────────────────────────────

async def send_telegram(token: str, chat_id: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            })
            ok = r.status_code == 200
            if ok:
                logger.info(f"Telegram → {chat_id}")
            else:
                logger.warning(f"Telegram errore {r.status_code}: {r.text[:80]}")
            return ok
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False


# ── WhatsApp via CallMeBot ────────────────────────────────────────────────────
# Setup (una tantum):
#   1. Aggiungi +34 644 59 77 88 ai contatti
#   2. Invia "I allow callmebot to send me messages" via WhatsApp a quel numero
#   3. Ricevi il tuo apikey via WhatsApp (es. 1234567)
#   4. Nel .env: WHATSAPP_PHONE=+39XXXXXXXXXX  WHATSAPP_APIKEY=1234567

async def send_whatsapp(phone: str, apikey: str, message: str) -> bool:
    """
    Invia messaggio WhatsApp via CallMeBot (gratuito).
    phone: numero con prefisso internazionale es. +393331234567
    apikey: chiave ricevuta da CallMeBot
    """
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded}&apikey={apikey}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            ok = r.status_code == 200 and "Message queued" in r.text
            if ok:
                logger.info(f"WhatsApp → {phone}")
            else:
                logger.warning(f"WhatsApp errore: {r.text[:100]}")
            return ok
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return False


# ── Email via SMTP ────────────────────────────────────────────────────────────
# Setup Gmail:
#   1. Vai su myaccount.google.com → Sicurezza → Password per le app
#   2. Crea una "App password" per "Mail"
#   3. Nel .env: EMAIL_FROM=tuo@gmail.com  EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
#   4. EMAIL_TO=destinatario@email.com

def send_email(from_addr: str, password: str, to_addr: str, subject: str, body_html: str) -> bool:
    """Invia email via Gmail SMTP (o qualsiasi SMTP con SSL)."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.attach(MIMEText(body_html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())

        logger.info(f"Email → {to_addr}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


# ── Formatter messaggi ────────────────────────────────────────────────────────

def format_message_text(alert_id: str, reference: str, listing) -> str:
    """Testo plain per WhatsApp."""
    source_emoji = {
        "chrono24": "🔵", "ebay": "🟡",
        "instagram": "📸", "instagram_story": "📱",
    }.get(listing.source, "⌚")

    return (
        f"🚨 WatchScanner Alert\n\n"
        f"⌚ Referenza: {reference}\n"
        f"{source_emoji} Fonte: {listing.source.upper()}\n"
        f"💰 Prezzo: {listing.price:,.0f} €\n"
        f"👤 Venditore: {listing.seller}\n"
        f"📦 Condizione: {listing.condition}\n\n"
        f"🔗 {listing.url}\n\n"
        f"ID alert: {alert_id}"
    )


def format_message_html(alert_id: str, reference: str, listing) -> tuple[str, str]:
    """Restituisce (subject, html) per email."""
    subject = f"🚨 WatchScanner: {reference} trovato a {listing.price:,.0f}€"
    source_emoji = {
        "chrono24": "🔵", "ebay": "🟡",
        "instagram": "📸", "instagram_story": "📱",
    }.get(listing.source, "⌚")

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;background:#18181b;color:#f4f4f5;padding:32px;border-radius:16px">
      <h2 style="color:#fbbf24;margin-bottom:8px">🚨 WatchScanner Alert</h2>
      <p style="color:#a1a1aa;margin-top:0">È stata trovata un'offerta per la tua referenza</p>
      <hr style="border-color:#3f3f46;margin:20px 0">
      <table style="width:100%;border-collapse:collapse">
        <tr><td style="color:#a1a1aa;padding:6px 0">⌚ Referenza</td><td style="font-weight:bold;color:#fbbf24">{reference}</td></tr>
        <tr><td style="color:#a1a1aa;padding:6px 0">{source_emoji} Fonte</td><td>{listing.source.upper()}</td></tr>
        <tr><td style="color:#a1a1aa;padding:6px 0">💰 Prezzo</td><td style="font-size:1.4em;font-weight:bold;color:#f4f4f5">{listing.price:,.0f} €</td></tr>
        <tr><td style="color:#a1a1aa;padding:6px 0">👤 Venditore</td><td>{listing.seller}</td></tr>
        <tr><td style="color:#a1a1aa;padding:6px 0">📦 Condizione</td><td>{listing.condition}</td></tr>
      </table>
      <hr style="border-color:#3f3f46;margin:20px 0">
      <a href="{listing.url}" style="display:inline-block;background:#fbbf24;color:#18181b;font-weight:bold;padding:12px 24px;border-radius:10px;text-decoration:none">
        Vai all'annuncio →
      </a>
      <p style="color:#52525b;font-size:12px;margin-top:24px">Alert ID: {alert_id}</p>
    </div>
    """
    return subject, html
