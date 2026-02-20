import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
import json
import time

router = APIRouter()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


homepage_cache = {
    "data": None,
    "expires_at": 0
}
CACHE_TTL = 300  

async def get_homepage_data():
    """
    Fetches the homepage data from the cache if valid, 
    otherwise fetches from MongoDB and updates the cache.
    Also auto-news the cache if called while still valid.
    """
    current_time = time.time()
    
    
    if homepage_cache["data"] and current_time < homepage_cache["expires_at"]:
        
        homepage_cache["expires_at"] = current_time + CACHE_TTL
        return homepage_cache["data"]

    
    db_start_time = time.time()
    db = db_handler.get_db()
    collection = db["homepage"]
    
    
    doc_count = await collection.count_documents({})
    if doc_count == 0:
        homepage_data = {}
    else:
        homepage_data = await collection.find_one({})
    
    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | Homepage Data | Time: {db_elapsed:.4f}s")
    
    
    homepage_cache["data"] = homepage_data
    homepage_cache["expires_at"] = current_time + CACHE_TTL
    
    return homepage_data

@router.get("/", tags=["Pages"])
async def serve_homepage(request: Request):
    """
    Serves the static homepage HTML page.
    """
    data = await get_homepage_data()
    return templates.TemplateResponse("homepage.html", {"request": request, "data": data})
