"""Simple in-memory rate limiter for public API endpoints."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from threading import Lock

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)

WINDOW_SEC = int(os.environ.get("RATE_LIMIT_WINDOW_SEC", "60"))
MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX", "60"))


def check_rate_limit(client_key: str) -> None:
    """Raise ValueError when limit exceeded (caller maps to HTTP 429)."""
    now = time.time()
    with _lock:
        hits = [t for t in _buckets[client_key] if now - t < WINDOW_SEC]
        if len(hits) >= MAX_REQUESTS:
            raise ValueError("rate_limit_exceeded")
        hits.append(now)
        _buckets[client_key] = hits
