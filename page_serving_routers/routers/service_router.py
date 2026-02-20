import os
import json
import time
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")
JSON_DIR = os.path.join(BASE_DIR, "..", "JSON_FILES")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

service_cache = {}
CACHE_TTL = 300  

async def get_service_data(category: str):
    """
    Fetches the service data for a given category from the cache if valid, 
    otherwise fetches from MongoDB and updates the cache.
    Also auto-renews the cache if called while still valid.
    """
    current_time = time.time()
    
    if category in service_cache and current_time < service_cache[category]["expires_at"]:
        service_cache[category]["expires_at"] = current_time + CACHE_TTL
        return service_cache[category]["data"]

    db_start_time = time.time()
    db = db_handler.get_db()
    collection_name = f"service_{category}"
    collection = db[collection_name]
    
    doc_count = await collection.count_documents({})
    if doc_count == 0:
        service_data = {}
    else:
        service_data = await collection.find_one({})
    
    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | Service Data ({category}) | Time: {db_elapsed:.4f}s")
    
    service_cache[category] = {
        "data": service_data,
        "expires_at": current_time + CACHE_TTL
    }
    
    return service_data

@router.get("/business", tags=["Pages"])
@router.get("/technology", tags=["Pages"])
@router.get("/gcc", tags=["Pages"])
@router.get("/sustainability", tags=["Pages"])
@router.get("/semiconductor", tags=["Pages"])
async def serve_service_page(request: Request):
    """Serves the static service HTML page populated with dynamic category data."""
    # Extract the category name from the URL path (e.g., '/technology' -> 'technology')
    category = request.url.path.strip("/")
    data = await get_service_data(category)
    return templates.TemplateResponse("service.html", {"request": request, "data": data})
