"""Serves the magazine homepage with cached data from MongoDB."""

import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
from PAGE_SERVING_ROUTERS.routers.navbar_fetcher import get_navbar_data
from cache_manager import cache_manager

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def _fetch_magazine_homepage_from_db():
    """Fetch magazine homepage data directly from MongoDB."""
    db = db_handler.get_db()
    collection = db["magazine_homepage"]

    doc_count = await collection.count_documents({})
    if doc_count == 0:
        return {}
    return await collection.find_one({})


async def get_magazine_homepage_data():
    """
    Returns magazine homepage data using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    return await cache_manager.get("magazine_homepage", _fetch_magazine_homepage_from_db)


@router.get("/magazine", tags=["Pages"])
async def serve_magazine_homepage(request: Request):
    """Serves the static magazine homepage HTML page."""
    data = await get_magazine_homepage_data()
    navbar = await get_navbar_data()
    return templates.TemplateResponse("magazine-homepage.html", {"request": request, "data": data, "navbar": navbar})
