from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.routers import test, healthcheck, whatsapp_router
from app.config.rate_limits import limiter, custom_rate_limit_handler


settings.validate()

app = FastAPI(
    title="WhatsApp Medical Agent",
    description="A multilingual medical tourism assistant for IstanbulMedic",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

origins = [
  "http://localhost",
  "http://localhost:8000",
  # TODO: the backend domain will be added here when deployed
]

# Middlewares
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Include routers
app.include_router(whatsapp_router.router)
app.include_router(healthcheck.router)

# Only include test router in debug mode
if settings.DEBUG:
    app.include_router(test.router)

# Root endpoint
@app.get("/")
async def read_root():
    return "V"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
