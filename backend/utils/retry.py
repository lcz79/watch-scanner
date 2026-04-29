import asyncio
import functools
from utils.logger import get_logger

logger = get_logger("retry")


def async_retry(max_attempts: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator per retry con exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retry in {delay}s")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
