import uvicorn

from app.app import app
from app.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
