from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- Modalità ---
    mock_mode: bool = True  # True = dati finti, False = scraping reale
    debug: bool = False

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- OpenAI (Vision Agent) ---
    # Inserisci la tua chiave su https://platform.openai.com/api-keys
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # --- Instagram (Social Agent) ---
    # Account Instagram da usare per la scansione (preferibilmente un account dedicato)
    instagram_username: str = ""
    instagram_password: str = ""

    # --- TikTok (Social Agent) ---
    # Cookie sessionid TikTok per risultati autenticati (opzionale).
    # Ottienilo da DevTools → Application → Cookies → tiktok.com → sessionid
    tiktok_session_id: str = ""

    # --- Facebook (Social Agent) ---
    # Cookie sessione Facebook in formato JSON (array di oggetti Playwright cookie).
    # Opzionale: se assente, Marketplace viene scrapato in modalità pubblica.
    # Formato: '[{"name":"c_user","value":"...","domain":".facebook.com","path":"/"}]'
    facebook_cookies: str = ""

    # --- Telegram (Alert) ---
    # Crea un bot con @BotFather e inserisci il token
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # --- Email (Alert via Gmail SMTP) ---
    # 1. myaccount.google.com → Sicurezza → Password per le app → crea "Mail"
    # 2. Inserisci qui la password a 16 caratteri (es. "xxxx xxxx xxxx xxxx")
    email_from: str = ""
    email_password: str = ""
    email_to: str = ""

    # --- WhatsApp (Alert via CallMeBot — gratuito) ---
    # 1. Aggiungi +34 644 59 77 88 ai contatti WhatsApp
    # 2. Invia "I allow callmebot to send me messages" a quel numero
    # 3. Ricevi il tuo apikey via WhatsApp
    whatsapp_phone: str = ""   # es. +393331234567
    whatsapp_apikey: str = ""  # es. 1234567

    # --- Apify (scraping JS-rendered) ---
    # Opzionale: https://apify.com
    apify_api_key: str = ""

    # --- Rate limiting ---
    scraper_delay_seconds: float = 2.0
    max_retries: int = 3
    request_timeout_seconds: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
