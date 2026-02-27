"""Serves service category pages with cached data from MongoDB."""

import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
from page_serving_routers.routers.navbar_fetcher import get_navbar_data
from cache_manager import cache_manager

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")
JSON_DIR = os.path.join(BASE_DIR, "..", "JSON_FILES")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _make_service_fetcher(category: str):
    """
    Returns an async fetcher that resolves service page data.
    If a service_page_config doc exists for the category, it uses config-based
    resolution. Otherwise, falls back to legacy service_{category} collection.
    """
    async def _fetch():
        db = db_handler.get_db()

        # Check for admin-configured service page config
        config_doc = await db["service_page_config"].find_one({"category": category})
        if config_doc:
            config_doc.pop("_id", None)
            from API_ROUTERS.admin.admin_service_page_router import resolve_config_to_service_data
            return await resolve_config_to_service_data(config_doc, category)

        # Legacy fallback: read from service_{category} collection
        collection_name = f"service_{category}"
        collection = db[collection_name]
        doc_count = await collection.count_documents({})
        if doc_count == 0:
            return {}
        return await collection.find_one({})

    return _fetch


async def get_service_data(category: str):
    """
    Returns service data for the given category using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    cache_key = f"service_{category}"
    fetcher = _make_service_fetcher(category)
    return await cache_manager.get(cache_key, fetcher)


@router.get("/business", tags=["Pages"])
@router.get("/technology", tags=["Pages"])
@router.get("/gcc", tags=["Pages"])
@router.get("/sustainability", tags=["Pages"])
@router.get("/semiconductor", tags=["Pages"])
async def serve_service_page(request: Request):
    """Serves the static service HTML page populated with dynamic category data."""
    category = request.url.path.strip("/")
    data = await get_service_data(category)
    navbar = await get_navbar_data()

    # Auto-resolve fuel ambition link to latest magazine
    from API_ROUTERS.admin.admin_magazine_homepage_router import _get_latest_magazine_slug
    latest_slug = await _get_latest_magazine_slug()
    data["fuel_ambition_link"] = f"/magazine/{latest_slug}" if latest_slug else "/magazine_page"

    return templates.TemplateResponse("service.html", {"request": request, "data": data, "navbar": navbar})
