import asyncio
import base64
import httpx
from agents.base_agent import BaseAgent
from models.schemas import WatchQuery, WatchListing
from mock.mock_data import mock_vision_listings


class VisionAgent(BaseAgent):
    """
    Analizza immagini da social media usando GPT-4o Vision
    per riconoscere referenze orologi e prezzi nelle caption.
    """

    def __init__(self):
        super().__init__("vision_agent")

    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        await asyncio.sleep(0.5)  # Vision è più lento
        return mock_vision_listings(query.reference)

    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        """
        Pipeline Vision:
        1. Prende le immagini raccolte dal SocialAgent
        2. Invia a GPT-4o Vision per analisi
        3. Estrae referenza confermata e prezzo dalla caption

        Richiede OPENAI_API_KEY nel .env
        """
        if not self.settings.openai_api_key:
            self.logger.warning("OPENAI_API_KEY non configurata — skip Vision Agent")
            return []

        # TODO: Integrare con SocialAgent per ottenere le immagini da analizzare
        # Poi per ogni immagine:
        # result = await self._analyze_image(image_url, query.reference)
        return []

    async def _analyze_image(self, image_url: str, reference: str) -> dict | None:
        """
        Invia un'immagine a GPT-4o Vision e chiede di identificare la referenza e il prezzo.
        """
        prompt = f"""Analizza questa immagine di un orologio.
Sto cercando la referenza: {reference}

Rispondi in JSON con:
- is_match: true/false (l'orologio nell'immagine corrisponde alla referenza?)
- reference_detected: la referenza che vedi (es. "116610LN")
- price_detected: il prezzo che vedi nella caption/immagine (null se non visibile)
- confidence: 0.0-1.0
"""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.openai_model,
                    "max_tokens": 300,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_url}},
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
