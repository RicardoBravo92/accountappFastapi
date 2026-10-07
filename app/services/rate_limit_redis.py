"""Redis-based distributed rate limiter for multi-worker deployments."""

import time

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from app.core.config import settings


class RedisRateLimiter:
    """Redis-backed distributed rate limiter.

    Uses sliding window log algorithm with Redis sorted sets for
    accurate rate limiting across multiple workers.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int = 100,
        window_seconds: int = 60,
        prefix: str = "ratelimit",
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _make_key(self, identifier: str) -> str:
        """Create Redis key for rate limit."""
        return f"{self.prefix}:{identifier}"

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if a request is allowed under the rate limit.

        Uses sliding window with Redis sorted set for accuracy.

        Returns:
            Tuple of (allowed: bool, retry_after: int)
        """
        redis_key = self._make_key(key)
        now = time.time()
        window_start = now - self.window_seconds

        async with self.redis.pipeline(transaction=True) as pipe:
            # Remove expired entries
            pipe.zremrangebyscore(redis_key, 0, window_start)

            # Count current requests in window
            pipe.zcard(redis_key)

            # Add current request with timestamp as score
            pipe.zadd(redis_key, {str(now): now})

            # Set expiry on the key
            pipe.expire(redis_key, self.window_seconds + 1)

            results = await pipe.execute()

        current_count = results[1]

        if current_count >= self.max_requests:
            # Get oldest entry to calculate retry-after
            oldest = await self.redis.zrange(redis_key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + self.window_seconds - now) + 1
            else:
                retry_after = self.window_seconds
            return False, max(retry_after, 1)

        return True, 0

    async def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        redis_key = self._make_key(key)
        await self.redis.delete(redis_key)

    async def get_current_count(self, key: str) -> int:
        """Get current request count for a key."""
        redis_key = self._make_key(key)
        now = time.time()
        window_start = now - self.window_seconds

        # Clean expired and count
        await self.redis.zremrangebyscore(redis_key, 0, window_start)
        return await self.redis.zcard(redis_key)


class RedisRateLimitManager:
    """Manages Redis rate limiters with connection pooling."""

    def __init__(self):
        self._redis: redis.Redis | None = None
        self._api_limiter: RedisRateLimiter | None = None
        self._login_limiter: RedisRateLimiter | None = None

    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        self._redis = redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            decode_responses=True,
        )

        # Test connection
        await self._redis.ping()

        # Initialize limiters
        self._api_limiter = RedisRateLimiter(
            redis_client=self._redis,
            max_requests=100,
            window_seconds=60,
            prefix="ratelimit:api",
        )

        self._login_limiter = RedisRateLimiter(
            redis_client=self._redis,
            max_requests=5,
            window_seconds=60,
            prefix="ratelimit:login",
        )

    async def close(self) -> None:
        """Close Redis connection pool."""
        if self._redis:
            await self._redis.close()
            await self._redis.connection_pool.disconnect()

    @property
    def api_limiter(self) -> RedisRateLimiter:
        if not self._api_limiter:
            raise RuntimeError("Rate limiter not initialized. Call initialize() first.")
        return self._api_limiter

    @property
    def login_limiter(self) -> RedisRateLimiter:
        if not self._login_limiter:
            raise RuntimeError("Rate limiter not initialized. Call initialize() first.")
        return self._login_limiter


# Global rate limit manager instance
rate_limit_manager = RedisRateLimitManager()


async def get_redis_client() -> redis.Redis:
    """Dependency to get Redis client."""
    if not rate_limit_manager._redis:
        await rate_limit_manager.initialize()
    return rate_limit_manager._redis


async def rate_limit_redis(request: Request, identifier: str | None = None):
    """Check rate limit using Redis and raise HTTPException if exceeded."""
    if not rate_limit_manager._redis:
        await rate_limit_manager.initialize()

    client_id = rate_limit_manager.api_limiter._get_client_id(request)
    key = f"{client_id}:{identifier}" if identifier else client_id

    allowed, retry_after = await rate_limit_manager.api_limiter.is_allowed(key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


async def check_login_rate_limit_redis(request: Request, email: str):
    """Check login rate limit using Redis and raise HTTPException if exceeded."""
    if not rate_limit_manager._redis:
        await rate_limit_manager.initialize()

    client_id = rate_limit_manager.login_limiter._get_client_id(request)
    key = f"login:{email}:{client_id}"

    allowed, retry_after = await rate_limit_manager.login_limiter.is_allowed(key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


# Backwards compatibility - in-memory fallback for tests
class InMemoryRateLimiter:
    """Simple in-memory rate limiter for testing."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def is_allowed(self, key: str) -> tuple[bool, int]:
        now = time.time()
        window_start = now - self.window_seconds

        if key not in self.requests:
            self.requests[key] = []

        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        if len(self.requests[key]) >= self.max_requests:
            oldest = min(self.requests[key]) if self.requests[key] else now
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, max(retry_after, 1)

        self.requests[key].append(now)
        return True, 0

    def reset(self):
        self.requests.clear()


# Fallback limiters for when Redis is not available
_fallback_api_limiter = InMemoryRateLimiter(max_requests=100, window_seconds=60)
_fallback_login_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)


async def rate_limit(request: Request, identifier: str | None = None):
    """Check rate limit with Redis fallback to in-memory."""
    try:
        if not rate_limit_manager._redis:
            await rate_limit_manager.initialize()
        await rate_limit_redis(request, identifier)
    except Exception:
        # Fallback to in-memory for resilience
        client_id = _fallback_api_limiter._get_client_id(request)
        key = f"{client_id}:{identifier}" if identifier else client_id
        allowed, retry_after = _fallback_api_limiter.is_allowed(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )


async def check_login_rate_limit(request: Request, email: str):
    """Check login rate limit with Redis fallback to in-memory."""
    try:
        if not rate_limit_manager._redis:
            await rate_limit_manager.initialize()
        await check_login_rate_limit_redis(request, email)
    except Exception:
        # Fallback to in-memory for resilience
        client_id = _fallback_login_limiter._get_client_id(request)
        key = f"login:{email}:{client_id}"
        allowed, retry_after = _fallback_login_limiter.is_allowed(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )
