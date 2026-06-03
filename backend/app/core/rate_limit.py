import time
from collections import defaultdict
from threading import Lock

from app.core.config import get_settings


class InMemoryRateLimiter:
    """IP-based sliding window counter for MVP."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds
        with self._lock:
            self._hits[key] = [t for t in self._hits[key] if t > window_start]
            if len(self._hits[key]) >= max_requests:
                oldest = min(self._hits[key]) if self._hits[key] else now
                retry_after = max(1, int(window_seconds - (now - oldest)))
                return False, retry_after
            self._hits[key].append(now)
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    return _rate_limiter


def check_analyze_rate_limit(client_ip: str) -> tuple[bool, int]:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return True, 0
    return get_rate_limiter().check(
        f"analyze:{client_ip}",
        settings.rate_limit_analyze_requests,
        settings.rate_limit_analyze_window_seconds,
    )
