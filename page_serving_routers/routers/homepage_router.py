"""Serves the homepage with cached data from MongoDB.

Data assembly reads from the homepage_config collection (mode flags + slugs)
and resolves each section to the flat article format homepage.html expects.
Falls back gracefully to the old homepage collection if no config exists yet.
"""

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


# ── Placeholder article for missing / deleted blogs ──────────────────

_EMPTY_ARTICLE = {
    "author": "",
    "date": "",
    "title": "",
    "excerpt": "",
    "image_url": "",
    "link": "#",
    "badge": "",
}


async def _fetch_homepage_from_db():
    """Build the homepage data dict that homepage.html expects.

    1. Try to read homepage_config (new slug-based schema).
    2. For each section check mode:
       - manual -> resolve slugs to full blog data
       - auto   -> compute from page_views / created_at
    3. If no config exists yet, fall back to the old flat homepage collection.
    """
    db = db_handler.get_db()

    config = await db["homepage_config"].find_one({})

    # ── Fallback: no config yet, serve legacy flat data ──────────────
    if not config:
        legacy = await db["homepage"].find_one({})
        if legacy:
            legacy.pop("_id", None)
            return legacy
        return {}

    config.pop("_id", None)

    # Import helpers from the admin router (avoids duplication)
    from API_ROUTERS.admin.admin_homepage_router import (
        _resolve_blog_slug,
        _resolve_blog_slugs,
        get_most_visited_blogs,
        get_most_recent_blogs,
    )

    async def _safe_resolve(slug):
        art = await _resolve_blog_slug(slug)
        return art if art else dict(_EMPTY_ARTICLE)

    async def _safe_resolve_list(slugs):
        results = []
        for s in (slugs or []):
            results.append(await _safe_resolve(s))
        return results

    data = {}

    # ── Hero Section (always manual) ─────────────────────────────────
    hero = config.get("hero_section", {})
    data["hero_section"] = {
        "main_article": await _safe_resolve(hero.get("main_article_slug")),
        "side_articles": await _safe_resolve_list(hero.get("side_article_slugs", [])),
    }

    # ── Featured Section 1 (Trending) ────────────────────────────────
    fs1 = config.get("featured_section_1", {})
    if fs1.get("mode") == "manual":
        data["featured_section_1"] = {
            "main_article": await _safe_resolve(fs1.get("main_article_slug")),
            "latest_news": await _safe_resolve_list(fs1.get("latest_news_slugs", [])),
        }
    else:
        trending = await get_most_visited_blogs(4)
        data["featured_section_1"] = {
            "main_article": trending[0] if trending else dict(_EMPTY_ARTICLE),
            "latest_news": trending[1:4] if len(trending) > 1 else [],
        }

    # ── Strip Section (static, pass through) ─────────────────────────
    data["strip_section"] = config.get("strip_section", {
        "items": ["STARTUPS", "AI", "BUSINESS", "ENTREPRENEUR", "EVENTS", "BRANDS", "TRENDS"]
    })

    # ── Top Stories Section (always manual) ───────────────────────────
    ts = config.get("top_stories_section", {})
    top_story = await _safe_resolve(ts.get("top_story_main_slug"))
    # Ensure badge field exists for the template
    if not top_story.get("badge"):
        top_story["badge"] = "TOP STORIES"
    data["top_stories_section"] = {
        "top_story_main": top_story,
        "leadership_spotlight": ts.get("leadership_spotlight", {
            "title": "Leadership Spotlight",
            "leader_name": "",
            "leader_role": "",
            "leader_bio": "",
            "leader_image_url": "",
            "link": "#",
        }),
    }

    # ── Ad Banner (pass through) ─────────────────────────────────────
    data["ad_banner"] = config.get("ad_banner", {"image_url": "", "link": ""})

    # ── Featured Section 2 (Latest) ──────────────────────────────────
    fs2 = config.get("featured_section_2", {})
    if fs2.get("mode") == "manual":
        data["featured_section_2"] = {
            "main_article": await _safe_resolve(fs2.get("main_article_slug")),
            "latest_news": await _safe_resolve_list(fs2.get("latest_news_slugs", [])),
        }
    else:
        latest = await get_most_recent_blogs(4)
        data["featured_section_2"] = {
            "main_article": latest[0] if latest else dict(_EMPTY_ARTICLE),
            "latest_news": latest[1:4] if len(latest) > 1 else [],
        }

    # ── Category Grid Section ────────────────────────────────────────
    cg = config.get("category_grid_section", {})
    category_grid = []

    for cat_key, cat_name in [("sustainability", "Sustainability"), ("semiconductor", "Semiconductors")]:
        cat = cg.get(cat_key, {"mode": "auto", "article_slugs": []})
        if cat.get("mode") == "manual":
            articles = await _safe_resolve_list(cat.get("article_slugs", []))
        else:
            articles = await get_most_visited_blogs(3, category=cat_key)
        category_grid.append({
            "category_name": cat_name,
            "articles": articles,
        })

    data["category_grid_section"] = category_grid

    return data


async def get_homepage_data():
    """
    Returns homepage data using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    return await cache_manager.get("homepage", _fetch_homepage_from_db)


@router.get("/", tags=["Pages"])
async def serve_homepage(request: Request):
    """Serves the static homepage HTML page."""
    data = await get_homepage_data()
    navbar = await get_navbar_data()
    return templates.TemplateResponse("homepage.html", {"request": request, "data": data, "navbar": navbar})
