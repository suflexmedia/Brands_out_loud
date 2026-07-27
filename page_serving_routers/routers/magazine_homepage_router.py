"""Serves the magazine homepage and remaster pages with cached data from MongoDB."""

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
    """Build the magazine homepage data dict that magazine-homepage.html expects."""
    from API_ROUTERS.admin.admin_magazine_homepage_router import (
        _get_magazine_homepage_config,
        resolve_config_to_template_data,
    )

    config = await _get_magazine_homepage_config()
    return await resolve_config_to_template_data(config)


async def get_magazine_homepage_data():
    """Returns magazine homepage data using the centralized cache manager."""
    return await cache_manager.get("magazine_homepage", _fetch_magazine_homepage_from_db)


@router.get("/magazine", tags=["Pages"])
async def serve_magazine_homepage(request: Request):
    """Serves the magazine homepage HTML page."""
    data = await get_magazine_homepage_data()
    navbar = await get_navbar_data()
    return templates.TemplateResponse(request, "magazine-homepage.html", {
        "data": data,
        "navbar": navbar,
    })


@router.get("/magazine_remaster", tags=["Pages"])
async def serve_magazine_remaster(request: Request):
    """Serves the remastered magazine page HTML."""
    data = await get_magazine_homepage_data()
    navbar = await get_navbar_data()
    return templates.TemplateResponse(request, "magazine_remaster.html", {
        "data": data,
        "navbar": navbar,
    })
