from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import time
import uvicorn

from PAGE_SERVING_ROUTERS.routers.homepage_router import router as homepage_router
from PAGE_SERVING_ROUTERS.routers.service_router import router as service_router

from database_handler import db_handler
from bucket_handler import bucket_handler

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup and shutdown logic.
    """
    import json
    
    try:
        db_handler.connect()
        bucket_handler.connect()
        
        # Seed database collections if they are empty
        db = db_handler.get_db()
        json_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JSON_FILES")
        
        # Homepage
        if await db["homepage"].count_documents({}) == 0:
            try:
                with open(os.path.join(json_dir, "homepage.json"), "r", encoding="utf-8") as f:
                    await db["homepage"].insert_one(json.load(f))
                print("Seeded homepage collection.")
            except FileNotFoundError:
                print("Seed file not found for homepage")
                
        # Services
        for category in ["business", "technology", "gcc", "sustainability", "semiconductor"]:
            col_name = f"service_{category}"
            if await db[col_name].count_documents({}) == 0:
                try:
                    with open(os.path.join(json_dir, f"{col_name}.json"), "r", encoding="utf-8") as f:
                        await db[col_name].insert_one(json.load(f))
                    print(f"Seeded {col_name} collection.")
                except FileNotFoundError:
                    print(f"Seed file not found for {col_name}")

    except Exception as e:
        print(f"Error during startup connection initialization: {e}")
    yield
    
    try:
        db_handler.disconnect()
    except Exception as e:
        print(f"Error during shutdown connection cleanup: {e}")

class HealthCheck(BaseModel):
    """Data model for health check response."""
    status: str

app = FastAPI(title="Brands of cloud", lifespan=lifespan)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """
    Middleware to log the total execution time of the request.
    This helps identify slow API calls overall.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    print(f"API Execution Time | [{request.method}] {request.url.path} | Total Time: {process_time:.4f}s")
    return response


app.mount("/static", StaticFiles(directory="PAGE_SERVING_ROUTERS/static"), name="static")


app.include_router(homepage_router)
app.include_router(service_router)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Returns the health status of the API."""
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)