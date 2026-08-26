"""Admin API endpoints for editing the magazine homepage configuration."""

import os
import re
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from database_handler import db_handler
from cache_manager import cache_manager

router = APIRouter(prefix="/admin/api/magazine-homepage", tags=["admin_magazine_homepage_api"])

COOKIE_NAME = "admin_session"

_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "page_serving_routers", "static", "templates",
)
_templates = Jinja2Templates(directory=_BASE_DIR)


async def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


# ── Default config ───────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "leadership_spotlight_section": {
        "magazine_cover_slug": None,
        "heading": "Leadership Spotlight",
        "profiles": [
            {"name": "", "description": "", "image_url": ""},
            {"name": "", "description": "", "image_url": ""},
            {"name": "", "description": "", "image_url": ""},
        ],
    },
    "magazine_grid_section": {
        "mode": "auto",
        "magazine_slugs": [None, None, None, None, None, None],
    },
    "fuel_ambition_section": {
        "mode": "auto",
        "manual_link": "",
    },
}


# ── Helpers ──────────────────────────────────────────────────────────

async def _resolve_magazine_slug(slug: str | None) -> dict | None:
    """Look up a published magazine by slug and return cover info."""
    if not slug:
        return None
    db = db_handler.get_db()
    mag = await db["magazines"].find_one({"slug": slug, "status": "published"})
    if not mag:
        return None
    return {
        "slug": mag.get("slug", ""),
        "title": mag.get("title", ""),
        "image_url": mag.get("image_url", ""),
    }


async def _get_latest_magazine_slug() -> str | None:
    """Get the slug of the most recently published magazine."""
    db = db_handler.get_db()
    mag = await db["magazines"].find({"status": "published"}).sort("created_at", -1).limit(1).to_list(length=1)
    if mag:
        return mag[0].get("slug")
    return None


async def _get_magazine_homepage_config() -> dict:
    """Get config from DB or return default."""
    db = db_handler.get_db()
    doc = await db["magazine_homepage_config"].find_one({})
    if not doc:
        return dict(DEFAULT_CONFIG)
    doc.pop("_id", None)
    return doc


async def resolve_config_to_template_data(config: dict) -> dict:
    """Resolve a config dict into the data structure the template expects.

    Used by both the page-serving router and the preview endpoint.
    """
    data = {}

    # Leadership spotlight section
    ls = config.get("leadership_spotlight_section", {})
    magazine_cover = await _resolve_magazine_slug(ls.get("magazine_cover_slug"))
    data["leadership_spotlight_section"] = {
        "magazine_cover": magazine_cover or {"slug": "", "title": "", "image_url": ""},
        "heading": ls.get("heading", "Leadership Spotlight"),
        "profiles": ls.get("profiles", DEFAULT_CONFIG["leadership_spotlight_section"]["profiles"]),
    }

    # Magazine grid section
    mgs = config.get("magazine_grid_section", DEFAULT_CONFIG["magazine_grid_section"])
    grid_mode = mgs.get("mode", "auto")
    grid_data = {"mode": grid_mode, "magazines": []}
    if grid_mode == "manual":
        for slug in mgs.get("magazine_slugs", []):
            resolved = await _resolve_magazine_slug(slug)
            grid_data["magazines"].append(resolved)
    data["magazine_grid_section"] = grid_data

    # Fuel ambition section
    fas = config.get("fuel_ambition_section", DEFAULT_CONFIG["fuel_ambition_section"])
    fuel_mode = fas.get("mode", "auto")
    if fuel_mode == "manual" and fas.get("manual_link", "").strip():
        data["fuel_ambition_link"] = fas["manual_link"].strip()
    else:
        latest_slug = await _get_latest_magazine_slug()
        data["fuel_ambition_link"] = f"/magazine/{latest_slug}" if latest_slug else "/magazine_page"

    return data


# ── API Endpoints ────────────────────────────────────────────────────

@router.get("/config")
async def get_config(request: Request):
    """Return current config with resolved magazine details."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    config = await _get_magazine_homepage_config()

    ls = config.get("leadership_spotlight_section", {})
    magazine_cover = await _resolve_magazine_slug(ls.get("magazine_cover_slug"))

    # Magazine grid section — resolve manual slugs
    mgs = config.get("magazine_grid_section", DEFAULT_CONFIG["magazine_grid_section"])
    grid_magazines = []
    for slug in mgs.get("magazine_slugs", []):
        resolved_mag = await _resolve_magazine_slug(slug)
        grid_magazines.append(resolved_mag)

    # Fuel ambition section
    fas = config.get("fuel_ambition_section", DEFAULT_CONFIG["fuel_ambition_section"])

    resolved = {
        "leadership_spotlight_section": {
            "magazine_cover_slug": ls.get("magazine_cover_slug"),
            "magazine_cover": magazine_cover,
            "heading": ls.get("heading", "Leadership Spotlight"),
            "profiles": ls.get("profiles", DEFAULT_CONFIG["leadership_spotlight_section"]["profiles"]),
        },
        "magazine_grid_section": {
            "mode": mgs.get("mode", "auto"),
            "magazine_slugs": mgs.get("magazine_slugs", [None] * 6),
            "magazines": grid_magazines,
        },
        "fuel_ambition_section": {
            "mode": fas.get("mode", "auto"),
            "manual_link": fas.get("manual_link", ""),
        },
    }

    return resolved


@router.put("/config")
async def save_config(request: Request):
    """Save the full magazine homepage config."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    db = db_handler.get_db()

    ls = data.get("leadership_spotlight_section", {})
    cover_slug = ls.get("magazine_cover_slug")

    # Validate magazine slug exists if provided
    if cover_slug:
        mag = await db["magazines"].find_one({"slug": cover_slug, "status": "published"})
        if not mag:
            raise HTTPException(
                status_code=400,
                detail=f"Magazine slug not found or not published: {cover_slug}",
            )

    # Build clean config
    profiles = ls.get("profiles", DEFAULT_CONFIG["leadership_spotlight_section"]["profiles"])
    # Ensure exactly 3 profiles
    while len(profiles) < 3:
        profiles.append({"name": "", "description": "", "image_url": ""})
    profiles = profiles[:3]

    # Magazine grid section
    mgs = data.get("magazine_grid_section", DEFAULT_CONFIG["magazine_grid_section"])
    grid_mode = mgs.get("mode", "auto")
    grid_slugs = mgs.get("magazine_slugs", [None] * 6)
    # Ensure exactly 6 slots
    while len(grid_slugs) < 6:
        grid_slugs.append(None)
    grid_slugs = grid_slugs[:6]

    # Validate manual grid slugs
    if grid_mode == "manual":
        for slug in grid_slugs:
            if slug:
                mag = await db["magazines"].find_one({"slug": slug, "status": "published"})
                if not mag:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Magazine slug not found or not published: {slug}",
                    )

    # Fuel ambition section
    fas = data.get("fuel_ambition_section", DEFAULT_CONFIG["fuel_ambition_section"])
    fuel_mode = fas.get("mode", "auto")
    fuel_link = fas.get("manual_link", "").strip() if fuel_mode == "manual" else ""

    config = {
        "leadership_spotlight_section": {
            "magazine_cover_slug": cover_slug,
            "heading": ls.get("heading", "Leadership Spotlight"),
            "profiles": profiles,
        },
        "magazine_grid_section": {
            "mode": grid_mode,
            "magazine_slugs": grid_slugs,
        },
        "fuel_ambition_section": {
            "mode": fuel_mode,
            "manual_link": fuel_link,
        },
    }

    # Upsert
    existing = await db["magazine_homepage_config"].find_one({})
    if existing:
        await db["magazine_homepage_config"].update_one({"_id": existing["_id"]}, {"$set": config})
    else:
        await db["magazine_homepage_config"].insert_one(config)

    # Invalidate cache
    cache_manager.invalidate("magazine_homepage")

    return {"status": "ok", "message": "Magazine homepage config saved successfully"}


@router.get("/search-magazines")
async def search_magazines(request: Request, q: str = "", limit: int = 10):
    """Search published magazines by title for the admin magazine picker."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    query = {"status": "published"}

    if q:
        query["title"] = {"$regex": re.escape(q), "$options": "i"}

    magazines = await db["magazines"].find(query).sort("created_at", -1).limit(limit).to_list(length=limit)

    results = []
    for mag in magazines:
        results.append({
            "slug": mag.get("slug", ""),
            "title": mag.get("title", "Untitled"),
            "thumbnail_url": mag.get("image_url", ""),
        })

    return results


@router.post("/preview")
async def preview_magazine_homepage(request: Request):
    """Render magazine-homepage.html with unsaved config for iframe preview."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    config_data = await request.json()
    data = await resolve_config_to_template_data(config_data)

    from page_serving_routers.routers.navbar_fetcher import get_navbar_data
    navbar = await get_navbar_data()

    return _templates.TemplateResponse(request, "magazine-homepage.html", {
        "data": data,
        "navbar": navbar,
    })
