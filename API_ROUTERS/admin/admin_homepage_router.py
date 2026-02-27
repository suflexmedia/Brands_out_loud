"""Admin API endpoints for editing the homepage configuration."""

import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database_handler import db_handler
from cache_manager import cache_manager
from datetime import datetime, timezone, timedelta
import re

router = APIRouter(prefix="/admin/api/homepage", tags=["admin_homepage_api"])

COOKIE_NAME = "admin_session"

# Templates for rendering homepage preview
_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PAGE_SERVING_ROUTERS", "static", "templates")
_templates = Jinja2Templates(directory=_BASE_DIR)


async def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


# ── Default config template ──────────────────────────────────────────

DEFAULT_CONFIG = {
    "hero_section": {
        "main_article_slug": None,
        "side_article_slugs": [None, None, None],
    },
    "featured_section_1": {
        "mode": "auto",
        "main_article_slug": None,
        "latest_news_slugs": [None, None, None],
    },
    "strip_section": {
        "items": ["STARTUPS", "AI", "BUSINESS", "ENTREPRENEUR", "EVENTS", "BRANDS", "TRENDS"],
    },
    "top_stories_section": {
        "top_story_main_slug": None,
        "leadership_spotlight": {
            "title": "Leadership Spotlight",
            "leader_name": "",
            "leader_role": "",
            "leader_bio": "",
            "leader_image_url": "",
            "link": "#",
        },
    },
    "ad_banner": {
        "image_url": "",
        "link": "",
    },
    "featured_section_2": {
        "mode": "auto",
        "main_article_slug": None,
        "latest_news_slugs": [None, None, None],
    },
    "category_grid_section": {
        "sustainability": {
            "mode": "auto",
            "article_slugs": [None, None, None],
        },
        "semiconductor": {
            "mode": "auto",
            "article_slugs": [None, None, None],
        },
    },
}


# ── Helper functions (shared logic) ─────────────────────────────────

def _blog_to_article(blog: dict) -> dict:
    """Convert a blog document to the article format the homepage template expects."""
    content = blog.get("blogContent", {})
    created = blog.get("created_at")
    if isinstance(created, (int, float)):
        date_str = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%B %d, %Y")
    else:
        date_str = ""
    return {
        "author": content.get("blogAuthor", ""),
        "date": date_str,
        "title": content.get("blogTitle", "Untitled"),
        "excerpt": content.get("blogExcerpt", ""),
        "image_url": content.get("mainImageUrl", ""),
        "link": f"/blog/{blog.get('slug', '')}",
        "badge": content.get("blogCategory", "").upper(),
    }


async def _resolve_blog_slug(slug: str | None) -> dict | None:
    """Look up a single published blog by slug and return article format."""
    if not slug:
        return None
    db = db_handler.get_db()
    blog = await db["blogs"].find_one({"slug": slug, "status": "published"})
    if not blog:
        return None
    return _blog_to_article(blog)


async def _resolve_blog_slugs(slugs: list) -> list:
    """Resolve a list of slugs, returning article dicts (None for missing)."""
    results = []
    for slug in slugs:
        results.append(await _resolve_blog_slug(slug))
    return results


async def get_most_visited_blogs(limit: int, category: str | None = None) -> list[dict]:
    """Get most visited published blogs by aggregating page_views for /blog/* paths."""
    db = db_handler.get_db()
    ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)

    pipeline = [
        {
            "$match": {
                "path": {"$regex": "^/blog/"},
                "timestamp": {"$gte": ninety_days_ago},
            }
        },
        {
            "$group": {
                "_id": "$path",
                "view_count": {"$sum": 1},
            }
        },
        {"$addFields": {"_tiebreaker": {"$rand": {}}}},
        {"$sort": {"view_count": -1, "_tiebreaker": -1}},
        {"$limit": limit * 3},  # fetch extra to filter by category/published
    ]

    view_docs = await db["page_views"].aggregate(pipeline).to_list(length=limit * 3)

    results = []
    for doc in view_docs:
        slug = doc["_id"].replace("/blog/", "", 1)
        query = {"slug": slug, "status": "published"}
        if category:
            query["blogContent.blogCategory"] = {"$regex": f"^{category}$", "$options": "i"}
        blog = await db["blogs"].find_one(query)
        if blog:
            article = _blog_to_article(blog)
            article["view_count"] = doc["view_count"]
            results.append(article)
        if len(results) >= limit:
            break

    return results


async def get_most_recent_blogs(limit: int) -> list[dict]:
    """Get most recently created published blogs."""
    db = db_handler.get_db()
    blogs = await db["blogs"].find({"status": "published"}).sort("created_at", -1).limit(limit).to_list(length=limit)
    return [_blog_to_article(b) for b in blogs]


async def _get_homepage_config() -> dict:
    """Get the homepage config from DB, or return default."""
    db = db_handler.get_db()
    doc = await db["homepage_config"].find_one({})
    if not doc:
        return dict(DEFAULT_CONFIG)

    # Remove _id for JSON serialization
    doc.pop("_id", None)
    return doc


# ── API Endpoints ────────────────────────────────────────────────────

@router.get("/config")
async def get_config(request: Request):
    """Return current homepage config with resolved blog details for manual slugs."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    config = await _get_homepage_config()

    # Resolve blog details for the admin preview
    resolved = {}

    # Hero section
    hero = config.get("hero_section", {})
    resolved["hero_section"] = {
        "main_article_slug": hero.get("main_article_slug"),
        "main_article": await _resolve_blog_slug(hero.get("main_article_slug")),
        "side_article_slugs": hero.get("side_article_slugs", [None, None, None]),
        "side_articles": await _resolve_blog_slugs(hero.get("side_article_slugs", [])),
    }

    # Featured section 1
    fs1 = config.get("featured_section_1", {})
    resolved["featured_section_1"] = {
        "mode": fs1.get("mode", "auto"),
        "main_article_slug": fs1.get("main_article_slug"),
        "main_article": await _resolve_blog_slug(fs1.get("main_article_slug")),
        "latest_news_slugs": fs1.get("latest_news_slugs", [None, None, None]),
        "latest_news": await _resolve_blog_slugs(fs1.get("latest_news_slugs", [])),
    }

    # Top stories
    ts = config.get("top_stories_section", {})
    resolved["top_stories_section"] = {
        "top_story_main_slug": ts.get("top_story_main_slug"),
        "top_story_main": await _resolve_blog_slug(ts.get("top_story_main_slug")),
        "leadership_spotlight": ts.get("leadership_spotlight", DEFAULT_CONFIG["top_stories_section"]["leadership_spotlight"]),
    }

    # Featured section 2
    fs2 = config.get("featured_section_2", {})
    resolved["featured_section_2"] = {
        "mode": fs2.get("mode", "auto"),
        "main_article_slug": fs2.get("main_article_slug"),
        "main_article": await _resolve_blog_slug(fs2.get("main_article_slug")),
        "latest_news_slugs": fs2.get("latest_news_slugs", [None, None, None]),
        "latest_news": await _resolve_blog_slugs(fs2.get("latest_news_slugs", [])),
    }

    # Category grid
    cg = config.get("category_grid_section", {})
    resolved["category_grid_section"] = {}
    for cat_key in ("sustainability", "semiconductor"):
        cat = cg.get(cat_key, {"mode": "auto", "article_slugs": [None, None, None]})
        resolved["category_grid_section"][cat_key] = {
            "mode": cat.get("mode", "auto"),
            "article_slugs": cat.get("article_slugs", [None, None, None]),
            "articles": await _resolve_blog_slugs(cat.get("article_slugs", [])),
        }

    # Strip section & ad banner (pass through)
    resolved["strip_section"] = config.get("strip_section", DEFAULT_CONFIG["strip_section"])
    resolved["ad_banner"] = config.get("ad_banner", DEFAULT_CONFIG["ad_banner"])

    return resolved


@router.put("/config")
async def save_config(request: Request):
    """Save the full homepage config. Validates slugs exist & are published."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    db = db_handler.get_db()

    # Collect all slugs to validate
    slugs_to_check = set()

    hero = data.get("hero_section", {})
    if hero.get("main_article_slug"):
        slugs_to_check.add(hero["main_article_slug"])
    for s in hero.get("side_article_slugs", []):
        if s:
            slugs_to_check.add(s)

    for section_key in ("featured_section_1", "featured_section_2"):
        section = data.get(section_key, {})
        if section.get("mode") == "manual":
            if section.get("main_article_slug"):
                slugs_to_check.add(section["main_article_slug"])
            for s in section.get("latest_news_slugs", []):
                if s:
                    slugs_to_check.add(s)

    ts = data.get("top_stories_section", {})
    if ts.get("top_story_main_slug"):
        slugs_to_check.add(ts["top_story_main_slug"])

    cg = data.get("category_grid_section", {})
    for cat_key in ("sustainability", "semiconductor"):
        cat = cg.get(cat_key, {})
        if cat.get("mode") == "manual":
            for s in cat.get("article_slugs", []):
                if s:
                    slugs_to_check.add(s)

    # Validate all slugs exist and are published
    if slugs_to_check:
        found = await db["blogs"].find(
            {"slug": {"$in": list(slugs_to_check)}, "status": "published"},
            {"slug": 1}
        ).to_list(length=None)
        found_slugs = {d["slug"] for d in found}
        missing = slugs_to_check - found_slugs
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"These blog slugs are not found or not published: {', '.join(sorted(missing))}"
            )

    # Build clean config document
    config = {
        "hero_section": {
            "main_article_slug": hero.get("main_article_slug"),
            "side_article_slugs": hero.get("side_article_slugs", [None, None, None]),
        },
        "featured_section_1": {
            "mode": data.get("featured_section_1", {}).get("mode", "auto"),
            "main_article_slug": data.get("featured_section_1", {}).get("main_article_slug"),
            "latest_news_slugs": data.get("featured_section_1", {}).get("latest_news_slugs", [None, None, None]),
        },
        "strip_section": data.get("strip_section", DEFAULT_CONFIG["strip_section"]),
        "top_stories_section": {
            "top_story_main_slug": ts.get("top_story_main_slug"),
            "leadership_spotlight": ts.get("leadership_spotlight", DEFAULT_CONFIG["top_stories_section"]["leadership_spotlight"]),
        },
        "ad_banner": data.get("ad_banner", DEFAULT_CONFIG["ad_banner"]),
        "featured_section_2": {
            "mode": data.get("featured_section_2", {}).get("mode", "auto"),
            "main_article_slug": data.get("featured_section_2", {}).get("main_article_slug"),
            "latest_news_slugs": data.get("featured_section_2", {}).get("latest_news_slugs", [None, None, None]),
        },
        "category_grid_section": {},
    }

    for cat_key in ("sustainability", "semiconductor"):
        cat_data = cg.get(cat_key, {})
        config["category_grid_section"][cat_key] = {
            "mode": cat_data.get("mode", "auto"),
            "article_slugs": cat_data.get("article_slugs", [None, None, None]),
        }

    # Upsert config
    existing = await db["homepage_config"].find_one({})
    if existing:
        await db["homepage_config"].update_one({"_id": existing["_id"]}, {"$set": config})
    else:
        await db["homepage_config"].insert_one(config)

    # Invalidate homepage cache so the public site picks up changes
    cache_manager.invalidate("homepage")

    return {"status": "ok", "message": "Homepage config saved successfully"}


@router.get("/search-blogs")
async def search_blogs(request: Request, q: str = "", category: str = "", limit: int = 10):
    """Search published blogs by title for the admin blog picker."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    query = {"status": "published"}

    if q:
        query["blogContent.blogTitle"] = {"$regex": re.escape(q), "$options": "i"}
    if category:
        query["blogContent.blogCategory"] = {"$regex": f"^{category}$", "$options": "i"}

    blogs = await db["blogs"].find(query).sort("created_at", -1).limit(limit).to_list(length=limit)

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


@router.get("/automatic-preview")
async def automatic_preview(request: Request):
    """Return computed data for all auto-capable sections (for admin preview)."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    trending = await get_most_visited_blogs(4)
    latest = await get_most_recent_blogs(4)
    sustainability = await get_most_visited_blogs(3, category="sustainability")
    semiconductor = await get_most_visited_blogs(3, category="semiconductor")

    return {
        "featured_section_1": {
            "main_article": trending[0] if len(trending) > 0 else None,
            "latest_news": trending[1:4] if len(trending) > 1 else [],
        },
        "featured_section_2": {
            "main_article": latest[0] if len(latest) > 0 else None,
            "latest_news": latest[1:4] if len(latest) > 1 else [],
        },
        "category_grid_section": {
            "sustainability": sustainability,
            "semiconductor": semiconductor,
        },
    }


# ── Preview Endpoint ─────────────────────────────────────────────

_EMPTY_ARTICLE = {
    "author": "",
    "date": "",
    "title": "",
    "excerpt": "",
    "image_url": "",
    "link": "#",
    "badge": "",
}


async def _resolve_config_to_homepage_data(config: dict) -> dict:
    """Resolve a homepage config dict into the data structure homepage.html expects.

    Mirrors the logic in homepage_router._fetch_homepage_from_db but works on
    an arbitrary (possibly unsaved) config object so the preview iframe can
    show changes before they are persisted.
    """

    async def _safe_resolve(slug):
        art = await _resolve_blog_slug(slug)
        return art if art else dict(_EMPTY_ARTICLE)

    async def _safe_resolve_list(slugs):
        return [await _safe_resolve(s) for s in (slugs or [])]

    data = {}

    # Hero Section (always manual)
    hero = config.get("hero_section", {})
    data["hero_section"] = {
        "main_article": await _safe_resolve(hero.get("main_article_slug")),
        "side_articles": await _safe_resolve_list(hero.get("side_article_slugs", [])),
    }

    # Featured Section 1 (Trending)
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

    # Strip Section
    data["strip_section"] = config.get("strip_section", {
        "items": ["STARTUPS", "AI", "BUSINESS", "ENTREPRENEUR", "EVENTS", "BRANDS", "TRENDS"]
    })

    # Top Stories Section (always manual)
    ts = config.get("top_stories_section", {})
    top_story = await _safe_resolve(ts.get("top_story_main_slug"))
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

    # Ad Banner
    data["ad_banner"] = config.get("ad_banner", {"image_url": "", "link": ""})

    # Featured Section 2 (Latest)
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

    # Category Grid Section
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


@router.post("/preview")
async def preview_homepage(request: Request):
    """Render the homepage template with the given (unsaved) config and return the full HTML."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    config_data = await request.json()

    # Resolve slugs and auto sections
    data = await _resolve_config_to_homepage_data(config_data)

    # Get navbar data
    from PAGE_SERVING_ROUTERS.routers.navbar_fetcher import get_navbar_data
    navbar = await get_navbar_data()

    html = _templates.TemplateResponse("homepage.html", {
        "request": request,
        "data": data,
        "navbar": navbar,
    })
    return html
