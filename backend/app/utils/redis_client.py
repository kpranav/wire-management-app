"""Redis client for caching and pub/sub."""
from redis.asyncio import Redis
from typing import Optional
import json
import os


class RedisCache:
    """Redis cache client."""

    def __init__(self, redis_url: str):
        self.redis: Optional[Redis] = None
        self.redis_url = redis_url

    async def connect(self):
        """Connect to Redis."""
        self.redis = await Redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 300):
        """Set key with TTL in seconds (default 5 minutes)."""
        if not self.redis:
            return
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str):
        """Delete key."""
        if not self.redis:
            return
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        if not self.redis:
            return
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

    async def publish(self, channel: str, message: str):
        """Publish message to channel."""
        if not self.redis:
            return
        await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
        """Subscribe to channel."""
        if not self.redis:
            return None
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


# Global cache instance
from app.config import settings

cache = RedisCache(redis_url=settings.REDIS_URL)


async def get_cache() -> RedisCache:
    """Dependency for getting cache instance."""
    return cache
