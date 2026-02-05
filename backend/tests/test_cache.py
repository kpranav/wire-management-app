"""Tests for caching functionality."""

import pytest

from app.services.cache_service import CacheService
from app.utils.redis_client import RedisCache


@pytest.mark.asyncio
async def test_cache_service_wire_list():
    """Test caching wire list."""

    # Mock Redis client for testing
    class MockRedis:
        def __init__(self):
            self.store = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ttl=300):
            self.store[key] = value

        async def setex(self, key, ttl, value):
            """Redis setex method: SET with EXpire."""
            self.store[key] = value

        async def delete(self, key):
            self.store.pop(key, None)

    # Create cache service with mock
    mock_redis = MockRedis()
    cache_service = CacheService(RedisCache("redis://fake"))
    cache_service.cache.redis = mock_redis

    # Test caching wire list
    user_id = 1
    wires = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]

    # Set cache
    await cache_service.set_user_wires(user_id, wires)

    # Get from cache
    cached_wires = await cache_service.get_user_wires(user_id)

    assert cached_wires == wires

    # Invalidate cache
    await cache_service.invalidate_user_wires(user_id)

    # Verify cache is cleared
    cached_wires = await cache_service.get_user_wires(user_id)
    assert cached_wires is None


@pytest.mark.asyncio
async def test_cache_service_rate_limit():
    """Test rate limiting."""

    class MockRedis:
        def __init__(self):
            self.store = {}
            self.counters = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ttl=300):
            self.store[key] = value
            self.counters[key] = int(value)

        async def setex(self, key, ttl, value):
            """Redis setex method: SET with EXpire."""
            self.store[key] = value
            self.counters[key] = int(value)

        async def incr(self, key):
            if key in self.counters:
                self.counters[key] += 1
                self.store[key] = str(self.counters[key])
            return self.counters.get(key, 0)

    mock_redis = MockRedis()
    cache_service = CacheService(RedisCache("redis://fake"))
    cache_service.cache.redis = mock_redis

    user_id = 1
    endpoint = "list_wires"

    # First request should pass
    result = await cache_service.check_rate_limit(user_id, endpoint, max_requests=3)
    assert result is True

    # Second request should pass
    result = await cache_service.check_rate_limit(user_id, endpoint, max_requests=3)
    assert result is True

    # Third request should pass
    result = await cache_service.check_rate_limit(user_id, endpoint, max_requests=3)
    assert result is True

    # Fourth request should fail (exceeded limit)
    result = await cache_service.check_rate_limit(user_id, endpoint, max_requests=3)
    assert result is False
