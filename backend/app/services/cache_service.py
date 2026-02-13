"""Caching service for business logic."""

import json

from app.utils.redis_client import RedisCache


class CacheService:
    """High-level caching service."""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    # Wire caching
    async def get_user_wires(self, user_id: int) -> list[dict] | None:
        """Get cached wire list for user."""
        key = f"wires:user:{user_id}"
        cached = await self.cache.get(key)
        return json.loads(cached) if cached else None

    async def set_user_wires(self, user_id: int, wires: list[dict], ttl: int = 300):
        """Cache wire list for user (5 min TTL)."""
        key = f"wires:user:{user_id}"
        await self.cache.set(key, json.dumps(wires), ttl)

    async def invalidate_user_wires(self, user_id: int):
        """Invalidate wire cache when data changes."""
        await self.cache.delete(f"wires:user:{user_id}")

    # Single wire caching
    async def get_wire(self, wire_id: int) -> dict | None:
        """Get cached wire by ID."""
        key = f"wire:{wire_id}"
        cached = await self.cache.get(key)
        return json.loads(cached) if cached else None

    async def set_wire(self, wire_id: int, wire_data: dict, ttl: int = 600):
        """Cache single wire (10 min TTL)."""
        key = f"wire:{wire_id}"
        await self.cache.set(key, json.dumps(wire_data), ttl)

    async def invalidate_wire(self, wire_id: int):
        """Invalidate wire cache."""
        await self.cache.delete(f"wire:{wire_id}")

    # Rate limiting
    async def check_rate_limit(
        self, user_id: int, endpoint: str, max_requests: int = 100, window: int = 60
    ) -> bool:
        """Check if user has exceeded rate limit."""
        key = f"ratelimit:{user_id}:{endpoint}"
        current = await self.cache.get(key)

        if current is None:
            await self.cache.set(key, "1", window)
            return True

        if int(current) >= max_requests:
            return False

        # Increment counter
        if self.cache.redis:
            await self.cache.redis.incr(key)
        return True
