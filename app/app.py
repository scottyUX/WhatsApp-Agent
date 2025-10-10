from fastapi import FastAPI
import uvicorn
from app.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhook, test, healthcheck, chat_router, whatsapp_router, medical_data_router
from app.config.rate_limits import limiter, custom_rate_limit_handler
from slowapi.errors import RateLimitExceeded

settings.validate()

app = FastAPI(
    title="WhatsApp Medical Agent",
    description="A multilingual medical tourism assistant for IstanbulMedic",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# CORS for frontend dev/prod
origins = [
    "http://localhost:3000",
    "http://localhost:3010",
]
# Allow custom origin via env var (comma-separated)
additional_origins = [o.strip() for o in (getattr(settings, "CORS_ORIGINS", "") or "").split(",") if o.strip()]
origins.extend(additional_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

app.include_router(webhook.router)
app.include_router(chat_router.router)
app.include_router(whatsapp_router.router)
app.include_router(medical_data_router.router)
app.include_router(healthcheck.router)

# Only include test router in debug mode
if settings.DEBUG:
    app.include_router(test.router)

# Root endpoint
@app.get("/")
async def read_root():
    return "V3"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
