"""
Centralized cache manager for all page-serving routers.

Implements:
- Fixed absolute expiry (no TTL renewal on reads)
- Stale-while-revalidate (serves stale data while refreshing in background)
- Event-driven invalidation (admin actions instantly clear relevant caches)
"""

import time
import asyncio
from typing import Any, Callable, Coroutine, Optional


CACHE_TTL = 300
STALE_GRACE_PERIOD = 60


class CacheEntry:
    """Represents a single cached item with fixed absolute expiry."""

    __slots__ = ("data", "expires_at", "_refreshing")

    def __init__(self):
        self.data: Any = None
        self.expires_at: float = 0
        self._refreshing: bool = False

    @property
    def is_fresh(self) -> bool:
        return self.data is not None and time.time() < self.expires_at

    @property
    def is_stale_but_usable(self) -> bool:
        current = time.time()
        return (
            self.data is not None
            and current >= self.expires_at
            and current < self.expires_at + STALE_GRACE_PERIOD
        )

    def set(self, data: Any) -> None:
        self.data = data
        self.expires_at = time.time() + CACHE_TTL
        self._refreshing = False

    def invalidate(self) -> None:
        self.data = None
        self.expires_at = 0
        self._refreshing = False


class CacheManager:
    """
    Manages all application caches with fixed expiry,
    stale-while-revalidate, and event-driven invalidation.
    """

    def __init__(self):
        self._caches: dict[str, CacheEntry] = {}

    def _get_or_create(self, key: str) -> CacheEntry:
        if key not in self._caches:
            self._caches[key] = CacheEntry()
        return self._caches[key]

    async def get(
        self,
        key: str,
        fetcher: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Any:
        """
        Retrieve cached data by key. If expired, fetch fresh data.
        If stale but within grace period, return stale data and
        trigger a background refresh (stale-while-revalidate).

        Args:
            key: Cache key identifier (e.g. "homepage", "navbar", "service_gcc")
            fetcher: Async function that fetches fresh data from the database
        """
        entry = self._get_or_create(key)

        if entry.is_fresh:
            remaining = max(0, entry.expires_at - time.time())
            print(f"Cache HIT   | {key} | Fresh | TTL: {remaining:.0f}s remaining")
            return entry.data

        if entry.is_stale_but_usable and not entry._refreshing:
            entry._refreshing = True
            print(f"Cache STALE | {key} | Serving stale data | Background refresh triggered")
            asyncio.create_task(self._background_refresh(key, fetcher))
            return entry.data

        print(f"Cache MISS  | {key} | Fetching from database...")
        return await self._fetch_and_cache(key, fetcher)

    async def _fetch_and_cache(
        self,
        key: str,
        fetcher: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Any:
        entry = self._get_or_create(key)
        db_start = time.time()

        data = await fetcher()

        elapsed = time.time() - db_start
        print(f"Database Fetch | {key} | Time: {elapsed:.4f}s")

        entry.set(data)
        return data

    async def _background_refresh(
        self,
        key: str,
        fetcher: Callable[[], Coroutine[Any, Any, Any]],
    ) -> None:
        try:
            await self._fetch_and_cache(key, fetcher)
        except Exception as e:
            print(f"Background refresh failed for '{key}': {e}")
            entry = self._get_or_create(key)
            entry._refreshing = False

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry by key."""
        if key in self._caches:
            self._caches[key].invalidate()
            print(f"Cache Invalidated | {key}")

    def invalidate_all(self) -> None:
        """Invalidate every cache entry."""
        for key, entry in self._caches.items():
            entry.invalidate()
        print("Cache Invalidated | ALL")

    def invalidate_pattern(self, prefix: str) -> None:
        """Invalidate all cache entries whose key starts with the given prefix."""
        for key in list(self._caches.keys()):
            if key.startswith(prefix):
                self._caches[key].invalidate()
                print(f"Cache Invalidated | {key}")

    def get_status(self) -> dict:
        """Return a snapshot of all cache entries and their status."""
        now = time.time()
        status = {}
        for key, entry in self._caches.items():
            if entry.data is None:
                state = "empty"
            elif now < entry.expires_at:
                state = "fresh"
            elif now < entry.expires_at + STALE_GRACE_PERIOD:
                state = "stale"
            else:
                state = "expired"

            status[key] = {
                "state": state,
                "expires_at": entry.expires_at,
                "seconds_remaining": max(0, entry.expires_at - now),
                "refreshing": entry._refreshing,
            }
        return status


cache_manager = CacheManager()
