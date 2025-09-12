from fastapi import FastAPI
import uvicorn
from app.config.settings import settings
from app.routers import webhook, test

settings.validate()

app = FastAPI(
    title="WhatsApp Medical Agent",
    description="A multilingual medical tourism assistant for IstanbulMedic",
    version="1.0.0"
)

app.include_router(webhook.router)
app.include_router(test.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
