"""Rate limiting utilities for API endpoints."""
import time
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self._store: Dict[str, Tuple[int, float]] = {}
        self._cleanup_interval = 3600
        self._last_cleanup = time.time()

    def _cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        expired_keys = [
            key for key, (_, reset_time) in self._store.items()
            if now > reset_time
        ]
        for key in expired_keys:
            del self._store[key]
        self._last_cleanup = now

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        self._cleanup()
        now = time.time()

        if key in self._store:
            count, reset_time = self._store[key]
            if now > reset_time:
                self._store[key] = (1, now + window_seconds)
                return True, max_requests - 1, 0
            else:
                if count >= max_requests:
                    retry_after = int(reset_time - now)
                    return False, 0, retry_after
                else:
                    self._store[key] = (count + 1, reset_time)
                    return True, max_requests - count - 1, 0
        else:
            self._store[key] = (1, now + window_seconds)
            return True, max_requests - 1, 0


_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


class RateLimitError(HTTPException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )


async def check_rate_limit(
    request: Request,
    max_requests: int = 5,
    window_seconds: int = 60,
    key_prefix: str = ""
) -> None:
    """Check rate limit for a request. Raises RateLimitError if limit exceeded."""
    limiter = get_rate_limiter()
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}:{request.url.path}"
    allowed, _, retry_after = limiter.is_allowed(key, max_requests, window_seconds)
    if not allowed:
        raise RateLimitError(retry_after)
