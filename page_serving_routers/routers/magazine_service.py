"""Loads magazine issues and their books for the public magazine pages."""

from typing import Any, Dict, List, Optional

from cache_manager import cache_manager
from database_handler import db_handler

PUBLISHED = {"status": "published"}


def issue_card(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens an issue document into the archive-card shape."""
    slug = issue.get("slug", "")
    return {
        "slug": slug,
        "url": f"/magazine/{slug}",
        "title": issue.get("title", ""),
        "issue_number": issue.get("issue_number", ""),
        "season_label": issue.get("season_label", ""),
        "badge": issue.get("badge", ""),
        "description": issue.get("description", ""),
        "cover_image_url": issue.get("cover_image_url", ""),
        "cover_variant": issue.get("cover_variant", "edition-bg-1"),
        "cover_title_lines": issue.get("cover_title_lines", []),
        "brand": issue.get("brand", "BOL"),
        "stats": issue.get("stats", []),
        "meta_tags": issue.get("meta_tags", []),
        "pdf_url": issue.get("pdf_url", ""),
    }


def book_card(book: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens a book document into the grid-card shape."""
    issue_slug = book.get("issue_slug", "")
    slug = book.get("slug", "")
    return {
        "slug": slug,
        "issue_slug": issue_slug,
        "url": f"/magazine/{issue_slug}/{slug}",
        "title": book.get("title", ""),
        "subtitle": book.get("subtitle", ""),
        "author_name": book.get("author_name", ""),
        "category": book.get("category", ""),
        "pages_label": book.get("pages_label", ""),
        "price": book.get("price", {}),
        "brand": book.get("brand", "BOL"),
        "tag": book.get("tag", ""),
        "cover_image_url": book.get("cover_image_url", ""),
        "cover_variant": book.get("cover_variant", "cover-gradient-1"),
        "cover_title_lines": book.get("cover_title_lines", []),
        "background_number": book.get("background_number", ""),
    }


async def get_issues() -> List[Dict[str, Any]]:
    """Returns all published issues, ordered by order then newest, cached."""

    async def _fetch() -> List[Dict[str, Any]]:
        db = db_handler.get_db()
        cursor = db["magazine_issues"].find(PUBLISHED, {"_id": 0}).sort([("order", 1), ("created_at", -1)])
        return [issue_card(doc) async for doc in cursor]

    return await cache_manager.get("magazine_listing", _fetch)


async def get_issue(slug: str) -> Optional[Dict[str, Any]]:
    """Returns one published issue by slug, cached per slug."""

    async def _fetch() -> Optional[Dict[str, Any]]:
        db = db_handler.get_db()
        doc = await db["magazine_issues"].find_one({**PUBLISHED, "slug": slug}, {"_id": 0})
        return issue_card(doc) if doc else None

    return await cache_manager.get(f"magazine_issue_{slug}", _fetch)


async def get_books(issue_slug: str) -> List[Dict[str, Any]]:
    """Returns the published books belonging to an issue, cached per issue."""

    async def _fetch() -> List[Dict[str, Any]]:
        db = db_handler.get_db()
        cursor = db["books"].find({**PUBLISHED, "issue_slug": issue_slug}, {"_id": 0}).sort("order", 1)
        return [book_card(doc) async for doc in cursor]

    return await cache_manager.get(f"magazine_issue_{issue_slug}_books", _fetch)


async def get_book(issue_slug: str, slug: str) -> Optional[Dict[str, Any]]:
    """Returns the full detail document for one book, cached per book."""

    async def _fetch() -> Optional[Dict[str, Any]]:
        db = db_handler.get_db()
        doc = await db["books"].find_one(
            {**PUBLISHED, "issue_slug": issue_slug, "slug": slug}, {"_id": 0}
        )
        if not doc:
            return None
        detail = book_card(doc)
        detail.update({
            "description": doc.get("description", ""),
            "badges": doc.get("badges", []),
            "rating": doc.get("rating", {}),
            "store_url": doc.get("store_url", "#"),
            "sample_url": doc.get("sample_url", "#"),
            "author_avatar_url": doc.get("author_avatar_url", ""),
            "about": doc.get("about", {}),
            "covers": doc.get("covers", []),
            "highlights": doc.get("highlights", []),
            "audience": doc.get("audience", []),
            "cta_banner": doc.get("cta_banner", {}),
        })
        return detail

    return await cache_manager.get(f"magazine_book_{issue_slug}_{slug}", _fetch)


async def get_other_books(issue_slug: str, exclude_slug: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Returns other published books for the 'More from BOL' grid."""
    db = db_handler.get_db()
    cursor = db["books"].find(
        {**PUBLISHED, "slug": {"$ne": exclude_slug}}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    return [book_card(doc) async for doc in cursor]
