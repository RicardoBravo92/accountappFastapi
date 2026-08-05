import time
from collections import defaultdict
from typing import Optional

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Simple in-memory rate limiter.
    
    For production, replace with Redis-based rate limiting.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed under the rate limit.
        
        Args:
            key: Rate limit key (e.g., client IP, email for login attempts)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[key] = [
            t for t in self.requests[key] if t > window_start
        ]

        if len(self.requests[key]) >= self.max_requests:
            return False

        self.requests[key].append(now)
        return True

    def reset(self):
        """Reset all rate limit counters. Used for testing."""
        self.requests.clear()


# Default rate limiters
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


def rate_limit(request: Request, identifier: Optional[str] = None):
    """Check rate limit and raise HTTPException if exceeded.
    
    Args:
        request: FastAPI request object
        identifier: Additional identifier (e.g., email for login attempts)
    """
    client_id = api_rate_limiter._get_client_id(request)
    key = f"{client_id}:{identifier}" if identifier else client_id

    if not api_rate_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(api_rate_limiter.window_seconds)},
        )


def check_login_rate_limit(request: Request, email: str):
    """Check login rate limit and raise HTTPException if exceeded.
    
    Args:
        request: FastAPI request object
        email: User email being attempted
    """
    client_id = login_rate_limiter._get_client_id(request)
    key = f"login:{email}:{client_id}"

    if not login_rate_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(login_rate_limiter.window_seconds)},
        )