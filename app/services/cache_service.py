from datetime import datetime, timedelta, timezone
from typing import Any, Optional


class MemoryCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, datetime]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires = self._store[key]
            if expires > datetime.now(timezone.utc):
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._store[key] = (value, expires)

    def invalidate(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()


cache = MemoryCache()
