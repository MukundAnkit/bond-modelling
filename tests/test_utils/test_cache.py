"""Tests for the local JSON caching layer."""

import os
import shutil
import time
from collections.abc import Generator

import pytest

from src.utils.cache import JSONCache


@pytest.fixture
def temp_cache_dir() -> Generator[str, None, None]:
    """Fixture to provide a clean temporary cache directory."""
    cache_dir = ".temp_cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)
    yield cache_dir
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)


def test_cache_set_get(temp_cache_dir: str) -> None:
    """Test standard set and get operations."""
    cache = JSONCache(cache_dir=temp_cache_dir)
    data = {"yields": [0.03, 0.04, 0.05]}
    cache.set("test_key", data)

    # Check that cache returns the stored data
    cached_data = cache.get("test_key")
    assert cached_data == data


def test_cache_expiry(temp_cache_dir: str) -> None:
    """Test cache entry expiration via TTL."""
    cache = JSONCache(cache_dir=temp_cache_dir)
    data = {"yields": [0.04]}
    # Set TTL to 1 second
    cache.set("expire_key", data, ttl=1)

    assert cache.get("expire_key") == data

    # Wait 1.1 seconds for expiration
    time.sleep(1.1)
    assert cache.get("expire_key") is None


def test_cache_clear(temp_cache_dir: str) -> None:
    """Test clearing all cache entries."""
    cache = JSONCache(cache_dir=temp_cache_dir)
    cache.set("key1", {"value": 1})
    cache.set("key2", {"value": 2})

    assert cache.get("key1") is not None
    assert cache.get("key2") is not None

    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert len(os.listdir(temp_cache_dir)) == 0
