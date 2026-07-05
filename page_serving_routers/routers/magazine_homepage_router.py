"""Serves the magazine homepage with cached data from MongoDB.

Reads from the magazine_homepage_config collection (new schema) and resolves
magazine slugs to cover data. Falls back gracefully if no config exists yet.
"""

import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from page_serving_routers.routers.navbar_fetcher import get_navbar_data
from cache_manager import cache_manager

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def _fetch_magazine_homepage_from_db():
    """Build the magazine homepage data dict that magazine-homepage.html expects.

    1. Read magazine_homepage_config (new slug-based schema).
    2. Resolve magazine cover slug to full magazine data.
    3. Get latest magazine for the fuel ambition button.
    4. If no config exists, return empty defaults for graceful fallback.
    """
    from API_ROUTERS.admin.admin_magazine_homepage_router import (
        _get_magazine_homepage_config,
        resolve_config_to_template_data,
    )

    config = await _get_magazine_homepage_config()
    return await resolve_config_to_template_data(config)


async def get_magazine_homepage_data():
    """
    Returns magazine homepage data using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    return await cache_manager.get("magazine_homepage", _fetch_magazine_homepage_from_db)


@router.get("/magazine", tags=["Pages"])
async def serve_magazine_homepage(request: Request):
    """Serves the magazine homepage HTML page."""
    data = await get_magazine_homepage_data()
    navbar = await get_navbar_data()
    return templates.TemplateResponse(request=request, name="magazine-homepage.html", context={"request": request, "data": data, "navbar": navbar})
