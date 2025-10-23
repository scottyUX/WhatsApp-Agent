from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config.settings import settings
from app.routers import (
    webhook,
    test,
    healthcheck,
    chat_router,
    whatsapp_router,
    medical_data_router,
    consultation_router,
    patient_router,
    consultant_note_router,
    patient_image_router,
    image_analysis_router,
    clinic_router,
    package_router,
)
from app.config.rate_limits import limiter, custom_rate_limit_handler
from slowapi.errors import RateLimitExceeded

settings.validate()

tags_metadata = [
    {
        "name": "Patient Images",
        "description": (
            "Manage image bundles captured for each patient profile. "
            "Use these endpoints to upload images tied to a patient profile and review previous submissions alongside analysis notes."
        ),
    },
    {
        "name": "Clinics",
        "description": "Manage clinic metadata and the packages offered at each location.",
    },
    {
        "name": "Packages",
        "description": "Maintain reusable package templates that can be assigned to clinics.",
    },
]

app = FastAPI(
    title="WhatsApp Medical Agent",
    description="A multilingual medical tourism assistant for IstanbulMedic",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    openapi_tags=tags_metadata,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# CORS for frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3003",
        "http://127.0.0.1:3003",
        "https://istanbulmedic-website.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(chat_router.router)
app.include_router(whatsapp_router.router)
app.include_router(medical_data_router.router)
app.include_router(consultation_router.router)
app.include_router(patient_router.router)
app.include_router(consultant_note_router.router)
app.include_router(patient_image_router.router)
app.include_router(image_analysis_router.router)
app.include_router(clinic_router.router)
app.include_router(package_router.router)
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
