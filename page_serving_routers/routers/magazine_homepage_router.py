import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
import time

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


magazine_homepage_cache = {
    "data": None,
    "expires_at": 0
}
CACHE_TTL = 300  

async def get_magazine_homepage_data():
    """
    Fetches the magazine homepage data from the cache if valid, 
    otherwise fetches from MongoDB and updates the cache.
    """
    current_time = time.time()
    
    if magazine_homepage_cache["data"] and current_time < magazine_homepage_cache["expires_at"]:
        magazine_homepage_cache["expires_at"] = current_time + CACHE_TTL
        return magazine_homepage_cache["data"]

    db_start_time = time.time()
    db = db_handler.get_db()
    collection = db["magazine_homepage"]
    
    doc_count = await collection.count_documents({})
    if doc_count == 0:
        magazine_homepage_data = {}
    else:
        magazine_homepage_data = await collection.find_one({})
    
    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | Magazine Homepage Data | Time: {db_elapsed:.4f}s")
    
    magazine_homepage_cache["data"] = magazine_homepage_data
    magazine_homepage_cache["expires_at"] = current_time + CACHE_TTL
    
    return magazine_homepage_data

@router.get("/magazine", tags=["Pages"])
async def serve_magazine_homepage(request: Request):
    """
    Serves the static magazine homepage HTML page.
    """
    data = await get_magazine_homepage_data()
    return templates.TemplateResponse("magazine-homepage.html", {"request": request, "data": data})
