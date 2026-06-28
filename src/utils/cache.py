"""Local JSON caching layer for API request results."""

import contextlib
import hashlib
import json
import os
import shutil
import time
from typing import Any


class JSONCache:
    """A local file-based JSON caching system with TTL support.

    Parameters
    ----------
    cache_dir : str, optional
        The directory where cache files will be stored. Default is ``".cache"``.
    default_ttl : int, optional
        The default time-to-live in seconds for cache entries. Default is ``86400``
        (1 day).

    """

    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 86400) -> None:
        """Initialize JSONCache instance.

        Parameters
        ----------
        cache_dir : str, optional
            The directory where cache files are stored. Default is ``".cache"``.
        default_ttl : int, optional
            Default TTL in seconds. Default is ``86400``.

        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_filepath(self, key: str) -> str:
        """Generate a safe, unique file path for a cache key using MD5 hashing."""
        key_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache if it exists and has not expired.

        Parameters
        ----------
        key : str
            The unique identifier for the cache entry.

        Returns
        -------
        Any or None
            The cached value, or ``None`` if the key is not found or has expired.

        """
        filepath = self._get_filepath(key)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, encoding="utf-8") as f:
                entry = json.load(f)
        except (json.JSONDecodeError, OSError):
            # If the file is corrupted, delete it and return None
            with contextlib.suppress(OSError):
                os.remove(filepath)
            return None

        expires_at = entry.get("expires_at")
        if expires_at is not None and time.time() > expires_at:
            # Entry has expired; delete file
            with contextlib.suppress(OSError):
                os.remove(filepath)
            return None

        return entry.get("data")

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache with an optional time-to-live.

        Parameters
        ----------
        key : str
            The unique identifier for the cache entry.
        value : Any
            The JSON-serializable value to cache.
        ttl : int, optional
            Time-to-live in seconds. If None, defaults to ``default_ttl``.
            If negative, the entry never expires.

        """
        filepath = self._get_filepath(key)
        used_ttl = ttl if ttl is not None else self.default_ttl

        expires_at = time.time() + used_ttl if used_ttl >= 0 else None

        entry = {
            "key": key,
            "expires_at": expires_at,
            "data": value,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)
        except OSError:
            # Fail silently or log if cache write fails
            pass

    def clear(self) -> None:
        """Remove all files inside the cache directory."""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
