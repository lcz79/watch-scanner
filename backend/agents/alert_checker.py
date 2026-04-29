"""
Alert Checker — job background che controlla gli alert attivi ogni 30 minuti.

Per ogni alert attivo:
  1. Esegue una scansione completa (Chrono24 + eBay + Instagram)
  2. Se trova offerte sotto il prezzo massimo → invia notifica Telegram
  3. Aggiorna last_triggered sull'alert

Viene avviato automaticamente all'avvio del server FastAPI.
"""

import asyncio
from datetime import datetime
from utils.logger import get_logger
from utils.notifier import (
    send_telegram, send_whatsapp, send_email,
    format_message_text, format_message_html,
)

logger = get_logger("alert_checker")

CHECK_INTERVAL = 30 * 60  # 30 minuti


async def run_alert_checks(alerts: dict, settings):
    """Controlla tutti gli alert attivi e notifica se trovate offerte."""
    active = [a for a in alerts.values() if a.active]
    if not active:
        return

    logger.info(f"Alert checker: controllo {len(active)} alert attivi")

    from orchestrator import run_scan
    from models.schemas import WatchQuery

    for alert in active:
        ref = alert.config.reference
        max_price = alert.config.max_price
        try:
            logger.info(f"  Scansione alert {alert.alert_id}: {ref} < {max_price}€")
            result = await run_scan(WatchQuery(
                reference=ref,
                max_price=max_price,
            ))

            # Filtra solo le offerte sotto il prezzo massimo
            matches = [l for l in result.listings if l.price <= max_price]

            if not matches:
                logger.info(f"  {ref}: nessuna offerta sotto {max_price}€")
                continue

            best = matches[0]  # già ordinati per prezzo
            logger.info(f"  {ref}: MATCH! {best.price}€ su {best.source} — notifica in invio")

            # Notifica — invia su tutti i canali configurati
            text_msg = format_message_text(alert.alert_id, ref, best)
            notified = False

            # 1. WhatsApp per-alert (numero specificato dall'utente nell'alert)
            if alert.config.notify_whatsapp and settings.whatsapp_apikey:
                ok = await send_whatsapp(alert.config.notify_whatsapp, settings.whatsapp_apikey, text_msg)
                notified = notified or ok

            # 2. WhatsApp globale (numero nel .env)
            elif settings.whatsapp_phone and settings.whatsapp_apikey:
                ok = await send_whatsapp(settings.whatsapp_phone, settings.whatsapp_apikey, text_msg)
                notified = notified or ok

            # 3. Email per-alert (email specificata nell'alert)
            if alert.config.notify_email and settings.email_from and settings.email_password:
                subject, html = format_message_html(alert.alert_id, ref, best)
                ok = send_email(settings.email_from, settings.email_password, alert.config.notify_email, subject, html)
                notified = notified or ok

            # 4. Email globale (email_to nel .env)
            elif settings.email_to and settings.email_from and settings.email_password:
                subject, html = format_message_html(alert.alert_id, ref, best)
                ok = send_email(settings.email_from, settings.email_password, settings.email_to, subject, html)
                notified = notified or ok

            # 5. Telegram (per-alert o globale)
            chat_id = alert.config.notify_telegram_chat_id or settings.telegram_chat_id
            if settings.telegram_bot_token and chat_id:
                ok = await send_telegram(settings.telegram_bot_token, chat_id, text_msg)
                notified = notified or ok

            if not notified:
                logger.warning(f"  {ref}: MATCH trovato ma nessun canale di notifica configurato")

            # Aggiorna last_triggered
            alert.last_triggered = datetime.now()

        except Exception as e:
            logger.error(f"  Alert {alert.alert_id} error: {e}")

        # Pausa tra alert per non sovraccaricare
        await asyncio.sleep(5)


async def start_alert_scheduler(alerts: dict, settings):
    """
    Loop infinito — ogni 30 minuti controlla tutti gli alert attivi.
    `alerts` è il dict condiviso con main.py (passato per riferimento).
    """
    logger.info(f"Alert scheduler avviato (ogni {CHECK_INTERVAL//60} minuti)")

    # Prima esecuzione dopo 2 minuti (lascia tempo al server di avviarsi)
    await asyncio.sleep(120)

    while True:
        await run_alert_checks(alerts, settings)
        logger.info(f"Alert checker: prossimo controllo tra {CHECK_INTERVAL//60} minuti")
        await asyncio.sleep(CHECK_INTERVAL)
