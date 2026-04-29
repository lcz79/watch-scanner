from abc import ABC, abstractmethod
from datetime import datetime
from models.schemas import WatchQuery, WatchListing, AgentStatus
from utils.logger import get_logger
from config import get_settings


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self.mock_mode = self.settings.mock_mode
        self.logger = get_logger(name)
        self._last_run: datetime | None = None
        self._last_error: str | None = None

    async def run(self, query: WatchQuery) -> list[WatchListing]:
        self.logger.info(f"Running {'[MOCK]' if self.mock_mode else '[REAL]'} | ref={query.reference}")
        try:
            if self.mock_mode:
                results = await self._mock_results(query)
            else:
                results = await self._real_results(query)
            self._last_run = datetime.now()
            self._last_error = None
            self.logger.info(f"Found {len(results)} listings")
            return results
        except Exception as e:
            self._last_error = str(e)
            self.logger.error(f"Agent error: {e}")
            return []

    @abstractmethod
    async def _real_results(self, query: WatchQuery) -> list[WatchListing]:
        """Implementa lo scraping reale qui."""
        ...

    @abstractmethod
    async def _mock_results(self, query: WatchQuery) -> list[WatchListing]:
        """Restituisce dati mock realistici."""
        ...

    def status(self) -> AgentStatus:
        return AgentStatus(
            name=self.name,
            status="mock" if self.mock_mode else ("error" if self._last_error else "ok"),
            mock_mode=self.mock_mode,
            last_run=self._last_run,
            error=self._last_error,
        )
