from fastapi import APIRouter, Request
from datetime import datetime
from app.config.settings import settings
from app.config.rate_limits import limiter, RateLimitConfig

router = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)

@router.get("/")
@limiter.limit(RateLimitConfig.HEALTH_CHECK)
async def health_check(request: Request):
    """
    Health check endpoint to verify the application is running properly.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@router.get("/ready")
@limiter.limit(RateLimitConfig.HEALTH_CHECK)
async def readiness_check(request: Request):
    """
    Readiness check endpoint to verify the application is ready to serve requests.
    """
    # Here you can add checks for external dependencies like databases, APIs, etc.
    # For now, we'll just return a simple ready status
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "twilio_configured": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN),
            "vector_store_configured": bool(settings.VECTOR_STORE_EN)
        }
    }
