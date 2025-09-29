from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Optional


# Rate limiting configurations for different endpoints
class RateLimitConfig:
    # Default rate limits
    DEFAULT = "100/minute"
    
    # Webhook endpoints, will be even more loosened after we have signature validation
    WEBHOOK = "1000/minute" 
    
    # Health check endpoints (very lenient)
    HEALTH_CHECK = "50/minute"
    
    # Test endpoints (stricter since they're for development)
    TEST = "30/minute"
    
    # Chat endpoints
    CHAT = "50/minute"


def get_rate_limit_key(request: Request) -> str:
    """
    Custom key function for rate limiting.
    You can customize this to use different identifiers like:
    - IP address (default)
    - User ID from headers
    - API key
    - Phone number for webhook
    """
    # For webhook endpoints, we might want to use the phone number
    if request.url.path.startswith("/api/webhook"):
        # Try to get phone number from form data for more granular limiting
        # This is async, so we'll fall back to IP for now
        pass
    
    # Default to IP address
    return get_remote_address(request)


# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for when rate limit is exceeded.
    """
    from fastapi.responses import JSONResponse
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "detail": str(exc)
        },
        headers={"Retry-After": "60"}  # Default retry after 60 seconds
    )


# Initialize the limiter
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[RateLimitConfig.DEFAULT]
)
