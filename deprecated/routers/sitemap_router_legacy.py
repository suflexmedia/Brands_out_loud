"""
Dynamic XML Sitemap generation for Brands Out Loud.

Generates 7 sitemaps + a sitemap index:
  1. sitemap-main.xml       – Homepage, magazine homepage, 5 service pages
  2. sitemap-business.xml   – /business + its blogs
  3. sitemap-technology.xml – /technology + its blogs
  4. sitemap-gcc.xml        – /gcc + its blogs
  5. sitemap-sustainability.xml – /sustainability + its blogs
  6. sitemap-semiconductor.xml  – /semiconductor + its blogs
  7. sitemap-magazine.xml   – /magazine + all published magazines

All sitemaps are cached for 1 hour and auto-invalidated when
blogs or magazines are created/updated/deleted.
"""

from fastapi import APIRouter, Request
from fastapi.responses import Response
from datetime import datetime, timezone
import json

from database_handler import db_handler
from cache_manager import cache_manager

router = APIRouter()

SITE_URL = "https://brandsoutloud.com"
SERVICE_CATEGORIES = ["business", "technology", "gcc", "sustainability", "semiconductor"]

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _format_date(dt) -> str:
    """Convert a datetime or timestamp to W3C date format for sitemaps."""
    if dt is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%d")
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, str):
        try:
            parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            return parsed.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _xml_response(content: str) -> Response:
    """Return an XML response with proper content type and cache headers."""
    return Response(
        content=content,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


def _url_entry(loc: str, lastmod: str = None, changefreq: str = None, priority: str = None) -> str:
    """Build a single <url> entry."""
    parts = [f"  <url>\n    <loc>{loc}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
    if priority:
        parts.append(f"    <priority>{priority}</priority>")
    parts.append("  </url>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Helpers to fetch data from MongoDB
# ---------------------------------------------------------------------------

async def _fetch_published_blogs_by_category(category: str) -> list:
    """Fetch all published blogs for a given category."""
    db = db_handler.get_db()
    cursor = db["blogs"].find(
        {
            "isDeleted": {"$ne": True},
            "status": "published",
        },
        {"slug": 1, "blogContent": 1, "created_at": 1, "date": 1},
    ).sort("created_at", -1)

    blogs = []
    async for doc in cursor:
        blog_content = doc.get("blogContent", {})
        if isinstance(blog_content, str):
            try:
                blog_content = json.loads(blog_content)
            except (json.JSONDecodeError, TypeError):
                blog_content = {}

        blog_category = blog_content.get("blogCategory", "").lower().strip()
        if blog_category == category.lower():
            blogs.append({
                "slug": doc.get("slug"),
                "lastmod": _format_date(doc.get("created_at") or doc.get("date")),
            })
    return blogs


async def _fetch_all_published_blogs() -> list:
    """Fetch all published blogs (for sitemap index lastmod)."""
    db = db_handler.get_db()
    cursor = db["blogs"].find(
        {"isDeleted": {"$ne": True}, "status": "published"},
        {"slug": 1, "created_at": 1, "date": 1},
    ).sort("created_at", -1).limit(1)

    result = []
    async for doc in cursor:
        result.append({
            "lastmod": _format_date(doc.get("created_at") or doc.get("date")),
        })
    return result


async def _fetch_published_magazines() -> list:
    """Fetch all published magazines."""
    db = db_handler.get_db()
    cursor = db["magazines"].find(
        {"status": "published"},
        {"slug": 1, "created_at": 1},
    ).sort("created_at", -1)

    magazines = []
    async for doc in cursor:
        magazines.append({
            "slug": doc.get("slug"),
            "lastmod": _format_date(doc.get("created_at")),
        })
    return magazines


# ---------------------------------------------------------------------------
# Sitemap Index
# ---------------------------------------------------------------------------

@router.get("/sitemap.xml")
async def sitemap_index(request: Request):
    """Sitemap index that lists all individual sitemaps."""

    async def _build():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Get latest blog date for service sitemaps
        latest_blogs = await _fetch_all_published_blogs()
        blog_lastmod = latest_blogs[0]["lastmod"] if latest_blogs else today

        # Get latest magazine date
        magazines = await _fetch_published_magazines()
        mag_lastmod = magazines[0]["lastmod"] if magazines else today

        sitemaps = [
            (f"{SITE_URL}/sitemap-main.xml", today),
        ]
        for cat in SERVICE_CATEGORIES:
            sitemaps.append((f"{SITE_URL}/sitemap-{cat}.xml", blog_lastmod))
        sitemaps.append((f"{SITE_URL}/sitemap-magazine.xml", mag_lastmod))

        entries = []
        for loc, lastmod in sitemaps:
            entries.append(
                f"  <sitemap>\n"
                f"    <loc>{loc}</loc>\n"
                f"    <lastmod>{lastmod}</lastmod>\n"
                f"  </sitemap>"
            )

        return (
            XML_HEADER
            + '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(entries)
            + "\n</sitemapindex>\n"
        )

    content = await cache_manager.get("sitemap_index", _build)
    return _xml_response(content)


# ---------------------------------------------------------------------------
# Main Sitemap (static pages)
# ---------------------------------------------------------------------------

@router.get("/sitemap-main.xml")
async def sitemap_main():
    """Main sitemap with homepage, magazine homepage, and service pages."""

    async def _build():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        urls = [
            _url_entry(SITE_URL, lastmod=today, changefreq="daily", priority="1.0"),
            _url_entry(f"{SITE_URL}/magazine", lastmod=today, changefreq="weekly", priority="0.8"),
        ]
        for cat in SERVICE_CATEGORIES:
            urls.append(
                _url_entry(f"{SITE_URL}/{cat}", lastmod=today, changefreq="daily", priority="0.8")
            )
        return (
            XML_HEADER
            + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    content = await cache_manager.get("sitemap_main", _build)
    return _xml_response(content)


# ---------------------------------------------------------------------------
# Service Category Sitemaps (one per category)
# ---------------------------------------------------------------------------

async def _build_service_sitemap(category: str) -> str:
    """Build sitemap XML for a service category page and its blogs."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    blogs = await _fetch_published_blogs_by_category(category)

    urls = [
        _url_entry(f"{SITE_URL}/{category}", lastmod=today, changefreq="daily", priority="0.8"),
    ]
    for blog in blogs:
        urls.append(
            _url_entry(
                f"{SITE_URL}/blog/{blog['slug']}",
                lastmod=blog["lastmod"],
                changefreq="monthly",
                priority="0.6",
            )
        )

    return (
        XML_HEADER
        + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


@router.get("/sitemap-business.xml")
async def sitemap_business():
    content = await cache_manager.get(
        "sitemap_business", lambda: _build_service_sitemap("business")
    )
    return _xml_response(content)


@router.get("/sitemap-technology.xml")
async def sitemap_technology():
    content = await cache_manager.get(
        "sitemap_technology", lambda: _build_service_sitemap("technology")
    )
    return _xml_response(content)


@router.get("/sitemap-gcc.xml")
async def sitemap_gcc():
    content = await cache_manager.get(
        "sitemap_gcc", lambda: _build_service_sitemap("gcc")
    )
    return _xml_response(content)


@router.get("/sitemap-sustainability.xml")
async def sitemap_sustainability():
    content = await cache_manager.get(
        "sitemap_sustainability", lambda: _build_service_sitemap("sustainability")
    )
    return _xml_response(content)


@router.get("/sitemap-semiconductor.xml")
async def sitemap_semiconductor():
    content = await cache_manager.get(
        "sitemap_semiconductor", lambda: _build_service_sitemap("semiconductor")
    )
    return _xml_response(content)


# ---------------------------------------------------------------------------
# Magazine Sitemap
# ---------------------------------------------------------------------------

@router.get("/sitemap-magazine.xml")
async def sitemap_magazine():
    """Sitemap with magazine homepage and all published magazines."""

    async def _build():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        magazines = await _fetch_published_magazines()

        urls = [
            _url_entry(f"{SITE_URL}/magazine", lastmod=today, changefreq="weekly", priority="0.8"),
        ]
        for mag in magazines:
            urls.append(
                _url_entry(
                    f"{SITE_URL}/magazine/{mag['slug']}",
                    lastmod=mag["lastmod"],
                    changefreq="monthly",
                    priority="0.7",
                )
            )

        return (
            XML_HEADER
            + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    content = await cache_manager.get("sitemap_magazine", _build)
    return _xml_response(content)


# ---------------------------------------------------------------------------
# robots.txt
# ---------------------------------------------------------------------------

@router.get("/robots.txt")
async def robots_txt():
    """Serve robots.txt pointing to the sitemap index."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "Disallow: /login\n"
        "Disallow: /static/\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")
