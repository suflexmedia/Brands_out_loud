"""Serves the remastered homepage from the page_content collection."""

import os
from typing import Any, Dict

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from page_serving_routers.routers.site_context import base_context

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))

TEMPLATE_NAME = "homepage_remaster.html"


async def build_context(content_override: Dict[str, Any] = None) -> Dict[str, Any]:
    """Builds the homepage template context, optionally from unsaved content."""
    return await base_context(active_nav="home", page_id="homepage", content_override=content_override)


@router.get("/", tags=["Pages"])
async def serve_homepage(request: Request):
    """Serves the remastered homepage."""
    return templates.TemplateResponse(request, TEMPLATE_NAME, await build_context())
