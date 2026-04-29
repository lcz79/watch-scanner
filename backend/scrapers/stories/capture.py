"""
Instagram Stories capture via Playwright.
Usa una sessione browser persistente (auth state salvato su disco) invece
delle API private di Instagram — molto più stabile, meno ban.
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator
from utils.logger import get_logger

logger = get_logger("stories.capture")

AUTH_STATE_FILE = Path(__file__).parent.parent.parent / "data" / "ig_browser_auth.json"
SCREENSHOTS_DIR = Path(__file__).parent.parent.parent / "data" / "story_screenshots"

# Dealer italiani prioritari con stories attive
PRIORITY_DEALERS = [
    "ruzzaorologi",
    "preziosoparma",
    "ismawatches",
    "edwatch",
    "goldfingersorologi",
    "cantelliorologi",
    "ketervintagewatches",
    "msellatiorologi",
    "watchmarket_it",
    "watchesofitalia",
    "luxurywatchesmilan",
    "orologi_secondmano",
]

# User-agent realistico Chrome Mac
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


async def save_auth_state(username: str, password: str) -> bool:
    """
    Apre Chrome visibile su instagram.com/login.
    L'utente fa il login manualmente (anche con 2FA/challenge).
    Quando la home di IG è caricata, salva la sessione automaticamente.
    Timeout: 3 minuti per completare il login.
    """
    from playwright.async_api import async_playwright

    AUTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(
            user_agent=_UA,
            locale="it-IT",
            no_viewport=True,
        )
        page = await context.new_page()

        try:
            logger.info("Apertura Chrome per login Instagram manuale...")
            await page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")

            # Accetta cookie se presente (non blocca se assente)
            try:
                await page.click('text="Consenti tutti i cookie"', timeout=4000)
                await asyncio.sleep(1)
            except Exception:
                pass

            # Prova a compilare automaticamente — se fallisce, l'utente fa manualmente
            try:
                await page.fill('input[name="username"]', username, timeout=8000)
                await asyncio.sleep(0.4)
                await page.fill('input[name="password"]', password, timeout=5000)
                await asyncio.sleep(0.4)
                await page.click('button[type="submit"]', timeout=5000)
            except Exception:
                logger.info("Compilazione automatica fallita — completa il login manualmente nel browser")

            logger.info("In attesa del login completato (max 3 minuti)...")

            # Aspetta che l'URL diventi la home di Instagram (login completato)
            await page.wait_for_url(
                lambda url: "instagram.com" in url and "/login" not in url and "/accounts" not in url,
                timeout=180_000,  # 3 minuti
            )
            await asyncio.sleep(4)

            # Chiudi popup "Non ora"
            for text in ["Non ora", "Not Now", "Adesso no", "Salta"]:
                try:
                    await page.click(f'text="{text}"', timeout=2000)
                    await asyncio.sleep(1)
                except Exception:
                    pass

            # Aspetta il cookie sessionid (fondamentale per autenticazione)
            logger.info("Attendo cookie sessionid...")
            for _ in range(30):  # max 30 secondi
                cookies = await context.cookies()
                if any(c["name"] == "sessionid" for c in cookies):
                    logger.info("Cookie sessionid trovato!")
                    break
                await asyncio.sleep(1)
            else:
                logger.warning("sessionid non trovato — potrebbe essere necessario completare il login manualmente")

            await asyncio.sleep(2)

            # Salva sessione
            state = await context.storage_state()
            cookies = state.get("cookies", [])
            ig_cookies = [c for c in cookies if "instagram" in c.get("domain", "")]
            logger.info(f"Sessione salvata: {len(ig_cookies)} cookie Instagram ({AUTH_STATE_FILE})")
            AUTH_STATE_FILE.write_text(json.dumps(state))
            return True

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
        finally:
            await browser.close()


def has_valid_auth() -> bool:
    """Controlla se esiste un auth state salvato (non verifica se è ancora valido)."""
    return AUTH_STATE_FILE.exists()


async def capture_stories(
    username: str,
    max_frames: int = 15,
) -> list[dict]:
    """
    Naviga direttamente a /stories/{username}/ e cattura screenshot frame per frame.
    Più affidabile del click sull'anello profile che varia spesso.
    """
    from playwright.async_api import async_playwright

    if not has_valid_auth():
        logger.warning("Nessun auth state — skip stories.")
        return []

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(AUTH_STATE_FILE),
            user_agent=_UA,
            locale="it-IT",
            timezone_id="Europe/Rome",
            viewport={"width": 1080, "height": 1920},  # mobile-like per stories
        )
        page = await context.new_page()

        try:
            stories_url = f"https://www.instagram.com/stories/{username}/"
            await page.goto(stories_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            # Sessione scaduta
            if "/accounts/login" in page.url:
                logger.warning(f"Sessione scaduta — ricrea auth state")
                return []

            # Nessuna story: IG reindirizza al profilo o mostra "Nessuna storia"
            if f"/stories/{username}/" not in page.url:
                logger.debug(f"@{username}: nessuna story attiva (redirect a {page.url})")
                return []

            # Chiudi popup generici
            for text in ["Non ora", "Not Now", "Chiudi", "Close"]:
                try:
                    await page.click(f'text="{text}"', timeout=1500)
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

            # Conferma dialogo "Vuoi visualizzare come watch.scanner?"
            # IG chiede conferma prima di mostrare la storia (privacy overlay)
            # Il testo esatto del pulsante è "Visualizza storia"
            for text in ["Visualizza storia", "Visualizza", "View story", "View", "Continua", "Continue"]:
                try:
                    await page.click(f'text="{text}"', timeout=3000)
                    logger.debug(f"@{username}: dialogo conferma visualizzazione chiuso ({text})")
                    await asyncio.sleep(2)
                    break
                except Exception:
                    pass

            # Loop frame per frame
            prev_url = ""
            frame_index = 0

            while frame_index < max_frames:
                await asyncio.sleep(1.5)

                current_url = page.url
                # Story finita se IG ci ha mandato altrove
                if f"/stories/{username}/" not in current_url:
                    logger.debug(f"@{username}: story terminata al frame {frame_index}")
                    break

                # Screenshot del frame corrente
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = SCREENSHOTS_DIR / f"{username}_{ts}_{frame_index}.png"
                await page.screenshot(path=str(fname), full_page=False)

                # Testo visibile (include didascalie IG che appaiono nel DOM)
                try:
                    raw_text = await page.inner_text("body")
                except Exception:
                    raw_text = ""

                results.append({
                    "username": username,
                    "frame_index": frame_index,
                    "screenshot_path": str(fname),
                    "timestamp": datetime.now().isoformat(),
                    "raw_page_text": raw_text[:3000],
                })
                logger.debug(f"@{username} frame {frame_index} → {fname.name}")

                # Avanza: click lato destro dello schermo (zona "avanti" nelle stories)
                try:
                    w = page.viewport_size["width"] if page.viewport_size else 1080
                    h = page.viewport_size["height"] if page.viewport_size else 1920
                    await page.mouse.click(w * 0.75, h * 0.5)
                    await asyncio.sleep(1.2)
                except Exception:
                    try:
                        await page.keyboard.press("ArrowRight")
                    except Exception:
                        break

                frame_index += 1

        except Exception as e:
            logger.debug(f"@{username} stories capture error: {e}")
        finally:
            await context.close()
            await browser.close()

    logger.info(f"@{username}: {len(results)} frame catturati")
    return results


async def capture_recent_posts(username: str, max_posts: int = 6) -> list[dict]:
    """
    Fallback: cattura screenshot dei post recenti se le stories non sono disponibili.
    """
    from playwright.async_api import async_playwright

    if not has_valid_auth():
        return []

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(AUTH_STATE_FILE),
            user_agent=_UA,
            locale="it-IT",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        try:
            await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded")
            await asyncio.sleep(3)

            if "/accounts/login" in page.url:
                return []

            # Chiudi popup
            for text in ["Non ora", "Not Now", "Chiudi"]:
                try:
                    await page.click(f'text="{text}"', timeout=1500)
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

            # Trova link ai post — prova selettori multipli
            post_links = []
            for selector in ['a[href*="/p/"]', 'a[href*="/reel/"]']:
                try:
                    links = await page.eval_on_selector_all(
                        selector,
                        'els => [...new Set(els.map(e => e.href))].slice(0, 9)'
                    )
                    post_links.extend(links)
                except Exception:
                    pass

            post_links = list(dict.fromkeys(post_links))[:max_posts]  # deduplica

            for i, link in enumerate(post_links[:max_posts]):
                await page.goto(link, wait_until="domcontentloaded")
                await asyncio.sleep(1.5)

                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = SCREENSHOTS_DIR / f"{username}_post_{ts}_{i}.png"
                await page.screenshot(path=str(fname))

                try:
                    raw_text = await page.inner_text("body")
                except Exception:
                    raw_text = ""

                results.append({
                    "username": username,
                    "frame_index": i,
                    "screenshot_path": str(fname),
                    "timestamp": datetime.now().isoformat(),
                    "raw_page_text": raw_text[:2000],
                    "post_url": link,
                })

                await asyncio.sleep(1 + asyncio.get_event_loop().time() % 0.5)

        except Exception as e:
            logger.debug(f"@{username} posts fallback error: {e}")
        finally:
            await context.close()
            await browser.close()

    return results
