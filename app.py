from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn

from PAGE_SERVING_ROUTERS.routers.homepage_router import router as homepage_router

from database_handler import db_handler
from bucket_handler import bucket_handler

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup and shutdown logic.
    """
    # Startup
    try:
        db_handler.connect()
        bucket_handler.connect()
    except Exception as e:
        print(f"Error during startup connection initialization: {e}")
    yield
    # Shutdown
    try:
        db_handler.disconnect()
    except Exception as e:
        print(f"Error during shutdown connection cleanup: {e}")

class HealthCheck(BaseModel):
    """Data model for health check response."""
    status: str

app = FastAPI(title="Brands of cloud", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="PAGE_SERVING_ROUTERS/static"), name="static")

# Include the homepage router
app.include_router(homepage_router)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Returns the health status of the API."""
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)