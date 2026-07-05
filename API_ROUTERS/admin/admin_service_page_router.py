"""Admin API endpoints for editing service page configurations."""

import os
import re
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from database_handler import db_handler
from cache_manager import cache_manager
from API_ROUTERS.admin.admin_homepage_router import (
    is_authenticated,
    _blog_to_article,
    _resolve_blog_slug,
    _resolve_blog_slugs,
    get_most_visited_blogs,
)

router = APIRouter(prefix="/admin/api/service-page", tags=["admin_service_page_api"])

VALID_CATEGORIES = {"business", "technology", "gcc", "sustainability", "semiconductor"}

CATEGORY_TITLES = {
    "business": "Business",
    "technology": "Technology",
    "gcc": "GCC",
    "sustainability": "Sustainability",
    "semiconductor": "Semiconductor",
}

_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "page_serving_routers",
    "static",
    "templates",
)
_templates = Jinja2Templates(directory=_BASE_DIR)

_EMPTY_ARTICLE = {
    "author": "",
    "date": "",
    "title": "",
    "excerpt": "",
    "image_url": "",
    "link": "#",
    "badge": "",
}


def _default_config(category: str) -> dict:
    return {
        "category": category,
        "featured_section": {
            "mode": "auto",
            "main_article_slug": None,
            "latest_news_slugs": [None, None, None],
        },
        "editor_picks_section": {
            "mode": "auto",
            "article_slugs": [None, None, None, None, None, None],
        },
        "top_stories_section": {
            "mode": "auto",
            "article_slugs": [None, None, None, None, None, None],
        },
    }


def _validate_category(category: str):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")


async def _get_service_config(category: str) -> dict:
    db = db_handler.get_db()
    doc = await db["service_page_config"].find_one({"category": category})
    if not doc:
        return _default_config(category)
    doc.pop("_id", None)
    return doc


# ── Auto-mode data fetchers ─────────────────────────────────────


async def _auto_featured(category: str) -> dict:
    """Latest 4 published blogs in this category. First = main, next 3 = latest news."""
    db = db_handler.get_db()
    blogs = (
        await db["blogs"]
        .find(
            {
                "status": "published",
                "blogContent.blogCategory": {"$regex": f"^{re.escape(category)}$", "$options": "i"},
            }
        )
        .sort("created_at", -1)
        .limit(4)
        .to_list(length=4)
    )
    articles = [_blog_to_article(b) for b in blogs]
    return {
        "main_article": articles[0] if len(articles) > 0 else dict(_EMPTY_ARTICLE),
        "latest_news": articles[1:4] if len(articles) > 1 else [],
    }


async def _auto_editor_picks(category: str) -> list:
    """Next 6 latest blogs after top 4 (skip 4, take 6)."""
    db = db_handler.get_db()
    blogs = (
        await db["blogs"]
        .find(
            {
                "status": "published",
                "blogContent.blogCategory": {"$regex": f"^{re.escape(category)}$", "$options": "i"},
            }
        )
        .sort("created_at", -1)
        .skip(4)
        .limit(6)
        .to_list(length=6)
    )
    return [_blog_to_article(b) for b in blogs]


async def _auto_top_stories(category: str) -> list:
    """Most viewed blogs in this category."""
    return await get_most_visited_blogs(6, category=category)


# ── Config → template data resolver ─────────────────────────────


async def resolve_config_to_service_data(config: dict, category: str) -> dict:
    """Convert a service page config into the data dict that service.html expects."""

    async def _safe_resolve(slug):
        art = await _resolve_blog_slug(slug)
        return art if art else dict(_EMPTY_ARTICLE)

    async def _safe_resolve_list(slugs):
        return [await _safe_resolve(s) for s in (slugs or [])]

    data = {
        "page_title": CATEGORY_TITLES.get(category, category.title()),
        "ad_banner_1": {"image_url": "", "link": ""},
        "ad_banner_2": {"image_url": "", "link": ""},
    }

    # Featured Section
    fs = config.get("featured_section", {})
    if fs.get("mode") == "manual":
        data["featured_section"] = {
            "main_article": await _safe_resolve(fs.get("main_article_slug")),
            "latest_news": await _safe_resolve_list(fs.get("latest_news_slugs", [])),
        }
    else:
        data["featured_section"] = await _auto_featured(category)

    # Editor Picks
    ep = config.get("editor_picks_section", {})
    if ep.get("mode") == "manual":
        data["editor_picks"] = await _safe_resolve_list(ep.get("article_slugs", []))
    else:
        data["editor_picks"] = await _auto_editor_picks(category)

    # Top Stories
    ts = config.get("top_stories_section", {})
    if ts.get("mode") == "manual":
        data["top_stories"] = await _safe_resolve_list(ts.get("article_slugs", []))
    else:
        data["top_stories"] = await _auto_top_stories(category)

    return data


# ── API Endpoints ────────────────────────────────────────────────


@router.get("/{category}/config")
async def get_config(request: Request, category: str):
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    _validate_category(category)

    config = await _get_service_config(category)

    resolved = {"category": category}

    # Featured section
    fs = config.get("featured_section", {})
    resolved["featured_section"] = {
        "mode": fs.get("mode", "auto"),
        "main_article_slug": fs.get("main_article_slug"),
        "main_article": await _resolve_blog_slug(fs.get("main_article_slug")),
        "latest_news_slugs": fs.get("latest_news_slugs", [None, None, None]),
        "latest_news": await _resolve_blog_slugs(fs.get("latest_news_slugs", [])),
    }

    # Editor picks
    ep = config.get("editor_picks_section", {})
    resolved["editor_picks_section"] = {
        "mode": ep.get("mode", "auto"),
        "article_slugs": ep.get("article_slugs", [None] * 6),
        "articles": await _resolve_blog_slugs(ep.get("article_slugs", [])),
    }

    # Top stories
    ts = config.get("top_stories_section", {})
    resolved["top_stories_section"] = {
        "mode": ts.get("mode", "auto"),
        "article_slugs": ts.get("article_slugs", [None] * 6),
        "articles": await _resolve_blog_slugs(ts.get("article_slugs", [])),
    }

    return resolved


@router.put("/{category}/config")
async def save_config(request: Request, category: str):
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    _validate_category(category)

    data = await request.json()
    db = db_handler.get_db()

    # Collect slugs to validate
    slugs_to_check = set()

    fs = data.get("featured_section", {})
    if fs.get("mode") == "manual":
        if fs.get("main_article_slug"):
            slugs_to_check.add(fs["main_article_slug"])
        for s in fs.get("latest_news_slugs", []):
            if s:
                slugs_to_check.add(s)

    ep = data.get("editor_picks_section", {})
    if ep.get("mode") == "manual":
        for s in ep.get("article_slugs", []):
            if s:
                slugs_to_check.add(s)

    ts = data.get("top_stories_section", {})
    if ts.get("mode") == "manual":
        for s in ts.get("article_slugs", []):
            if s:
                slugs_to_check.add(s)

    # Validate slugs exist, are published, and belong to correct category
    if slugs_to_check:
        found = await db["blogs"].find(
            {
                "slug": {"$in": list(slugs_to_check)},
                "status": "published",
                "blogContent.blogCategory": {"$regex": f"^{re.escape(category)}$", "$options": "i"},
            },
            {"slug": 1},
        ).to_list(length=None)
        found_slugs = {d["slug"] for d in found}
        missing = slugs_to_check - found_slugs
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"These blog slugs are not found, not published, or not in category '{category}': {', '.join(sorted(missing))}",
            )

    # Build clean config
    config = {
        "category": category,
        "featured_section": {
            "mode": fs.get("mode", "auto"),
            "main_article_slug": fs.get("main_article_slug"),
            "latest_news_slugs": fs.get("latest_news_slugs", [None, None, None]),
        },
        "editor_picks_section": {
            "mode": ep.get("mode", "auto"),
            "article_slugs": ep.get("article_slugs", [None] * 6),
        },
        "top_stories_section": {
            "mode": ts.get("mode", "auto"),
            "article_slugs": ts.get("article_slugs", [None] * 6),
        },
    }

    # Upsert
    existing = await db["service_page_config"].find_one({"category": category})
    if existing:
        await db["service_page_config"].update_one(
            {"_id": existing["_id"]}, {"$set": config}
        )
    else:
        await db["service_page_config"].insert_one(config)

    # Invalidate cache
    cache_manager.invalidate(f"service_{category}")

    return {"status": "ok", "message": f"Service page config for '{category}' saved successfully"}


@router.get("/{category}/search-blogs")
async def search_blogs(request: Request, category: str, q: str = "", limit: int = 10):
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    _validate_category(category)

    db = db_handler.get_db()
    query = {
        "status": "published",
        "blogContent.blogCategory": {"$regex": f"^{re.escape(category)}$", "$options": "i"},
    }
    if q:
        query["blogContent.blogTitle"] = {"$regex": re.escape(q), "$options": "i"}

    blogs = await db["blogs"].find(query).sort("created_at", -1).limit(limit).to_list(length=limit)

    from datetime import datetime, timezone

    results = []
    for blog in blogs:
        content = blog.get("blogContent", {})
        created = blog.get("created_at")
        if isinstance(created, (int, float)):
            date_str = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%B %d, %Y")
        else:
            date_str = ""
        results.append({
            "slug": blog.get("slug", ""),
            "title": content.get("blogTitle", "Untitled"),
            "image_url": content.get("mainImageUrl", ""),
            "author": content.get("blogAuthor", ""),
            "date": date_str,
            "category": content.get("blogCategory", ""),
        })

    return results


@router.get("/{category}/automatic-preview")
async def automatic_preview(request: Request, category: str):
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    _validate_category(category)

    featured = await _auto_featured(category)
    editor_picks = await _auto_editor_picks(category)
    top_stories = await _auto_top_stories(category)

    return {
        "featured_section": featured,
        "editor_picks_section": editor_picks,
        "top_stories_section": top_stories,
    }


@router.post("/{category}/preview")
async def preview_service_page(request: Request, category: str):
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    _validate_category(category)

    config_data = await request.json()
    data = await resolve_config_to_service_data(config_data, category)

    from page_serving_routers.routers.navbar_fetcher import get_navbar_data

    navbar = await get_navbar_data()

    return _templates.TemplateResponse(
        request=request, name="service.html", context={"request": request, "data": data, "navbar": navbar}
    )
