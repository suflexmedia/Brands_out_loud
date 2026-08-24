"""Generates the sitemap index, page sitemaps and robots.txt for the new URL scheme."""

from datetime import datetime, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response

from cache_manager import cache_manager
from database_handler import db_handler

router = APIRouter()

SITE_URL = "https://brandsoutloud.com"

STATIC_PATHS = [
    ("/", "1.0", "daily"),
    ("/blog", "0.9", "daily"),
    ("/magazine", "0.9", "weekly"),
    ("/contact", "0.5", "yearly"),
]


def _format_date(value) -> str:
    """Renders a stored timestamp of any supported type as an ISO date."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).date().isoformat()
    if isinstance(value, str) and value:
        return value[:10]
    return datetime.now(tz=timezone.utc).date().isoformat()


def _url_entry(path: str, lastmod: str, priority: str, changefreq: str) -> str:
    """Builds one url block."""
    return (
        "  <url>\n"
        f"    <loc>{escape(SITE_URL + path)}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>\n"
    )


def _wrap(entries: str) -> str:
    """Wraps url entries in a urlset document."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}"
        "</urlset>\n"
    )


def _xml(content: str) -> Response:
    """Returns an XML response."""
    return Response(content=content, media_type="application/xml")


async def _build_main() -> str:
    """Builds the static page sitemap."""
    today = datetime.now(tz=timezone.utc).date().isoformat()
    entries = "".join(_url_entry(path, today, priority, freq) for path, priority, freq in STATIC_PATHS)
    return _wrap(entries)


async def _build_blog() -> str:
    """Builds the sitemap of every published blog post."""
    db = db_handler.get_db()
    cursor = db["blogs"].find(
        {"isDeleted": {"$ne": True}, "status": "published"},
        {"slug": 1, "created_at": 1, "date": 1},
    ).sort("created_at", -1)
    entries = ""
    async for doc in cursor:
        slug = doc.get("slug")
        if not slug:
            continue
        lastmod = _format_date(doc.get("date") or doc.get("created_at"))
        entries += _url_entry(f"/blog/{slug}", lastmod, "0.6", "monthly")
    return _wrap(entries)


async def _build_magazine() -> str:
    """Builds the sitemap of every published issue and book."""
    db = db_handler.get_db()
    entries = ""
    async for issue in db["magazine_issues"].find({"status": "published"}, {"slug": 1, "created_at": 1}):
        slug = issue.get("slug")
        if not slug:
            continue
        entries += _url_entry(f"/magazine/{slug}", _format_date(issue.get("created_at")), "0.7", "monthly")

    async for book in db["books"].find({"status": "published"}, {"slug": 1, "issue_slug": 1, "created_at": 1}):
        slug = book.get("slug")
        issue_slug = book.get("issue_slug")
        if not slug or not issue_slug:
            continue
        entries += _url_entry(
            f"/magazine/{issue_slug}/{slug}", _format_date(book.get("created_at")), "0.6", "monthly"
        )
    return _wrap(entries)


async def _build_index() -> str:
    """Builds the sitemap index."""
    today = datetime.now(tz=timezone.utc).date().isoformat()
    names = ["sitemap-main.xml", "sitemap-blog.xml", "sitemap-magazine.xml"]
    body = "".join(
        f"  <sitemap>\n    <loc>{SITE_URL}/{name}</loc>\n    <lastmod>{today}</lastmod>\n  </sitemap>\n"
        for name in names
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}"
        "</sitemapindex>\n"
    )


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_index():
    """Serves the sitemap index."""
    return _xml(await cache_manager.get("sitemap_index", _build_index))


@router.get("/sitemap-main.xml", include_in_schema=False)
async def sitemap_main():
    """Serves the static page sitemap."""
    return _xml(await cache_manager.get("sitemap_main", _build_main))


@router.get("/sitemap-blog.xml", include_in_schema=False)
async def sitemap_blog():
    """Serves the blog post sitemap."""
    return _xml(await cache_manager.get("sitemap_blog", _build_blog))


@router.get("/sitemap-magazine.xml", include_in_schema=False)
async def sitemap_magazine():
    """Serves the magazine issue and book sitemap."""
    return _xml(await cache_manager.get("sitemap_magazine", _build_magazine))


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    """Serves robots.txt."""
    body = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "Disallow: /login\n"
        "Disallow: /static/\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    return Response(content=body, media_type="text/plain")
