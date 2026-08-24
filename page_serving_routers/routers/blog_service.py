"""Normalises blog documents into the shape the remaster templates consume."""

import json
from typing import Any, Dict, List, Optional

from cache_manager import cache_manager
from database_handler import db_handler

PUBLISHED_FILTER = {"isDeleted": {"$ne": True}, "status": "published"}


def _coerce_content(raw: Any) -> Dict[str, Any]:
    """Returns blogContent as a dict whether it was stored as a dict or a JSON string."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}
    return raw or {}


def _estimate_read_time(sections: List[Dict[str, Any]]) -> int:
    """Estimates reading minutes from the text content of a block list."""
    words = 0
    for block in sections or []:
        if block.get("type") == "list":
            words += sum(len(str(item).split()) for item in block.get("items", []))
        elif isinstance(block.get("content"), str):
            words += len(block["content"].split())
    return max(1, round(words / 200))


def to_card(blog: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens a blog document into the card fields listing templates expect."""
    content = _coerce_content(blog.get("blogContent"))
    sections = content.get("dynamicSections", [])
    category = (content.get("blogCategory") or "").strip()
    return {
        "slug": blog.get("slug", ""),
        "url": f"/blog/{blog.get('slug', '')}",
        "title": content.get("blogTitle", ""),
        "excerpt": content.get("blogSummary", ""),
        "category": category,
        "category_label": category.title(),
        "image_url": content.get("mainImageUrl", ""),
        "image_alt": content.get("mainImageAlt", ""),
        "author_name": content.get("author") or "BOL Editorial",
        "author_avatar_url": content.get("authorAvatarUrl") or "",
        "date": blog.get("date") or "",
        "read_time": content.get("readTime") or _estimate_read_time(sections),
    }


def to_post(blog: Dict[str, Any]) -> Dict[str, Any]:
    """Expands a blog document into the full single-post view model."""
    card = to_card(blog)
    content = _coerce_content(blog.get("blogContent"))
    blocks = content.get("dynamicSections", [])
    card["blocks"] = blocks
    card["toc"] = build_toc(blocks)
    return card


def build_toc(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds a two-level table of contents from heading blocks."""
    toc: List[Dict[str, Any]] = []
    for block in blocks or []:
        block_type = block.get("type")
        if block_type in ("h1", "h2", "heading2"):
            toc.append({
                "id": block.get("id") or "",
                "title": block.get("content", ""),
                "children": [],
            })
        elif block_type in ("h3", "heading3") and toc:
            toc[-1]["children"].append({
                "id": block.get("id") or "",
                "title": block.get("content", ""),
            })
    return toc


async def _fetch_published() -> List[Dict[str, Any]]:
    db = db_handler.get_db()
    cursor = db["blogs"].find(PUBLISHED_FILTER, {"_id": 0}).sort("created_at", -1)
    return [to_card(doc) async for doc in cursor]


async def get_published_cards() -> List[Dict[str, Any]]:
    """Returns every published blog as a card, newest first, cached."""
    return await cache_manager.get("blog_listing", _fetch_published)


async def get_post(slug: str) -> Optional[Dict[str, Any]]:
    """Returns one published post by slug, cached per slug."""

    async def _fetch() -> Optional[Dict[str, Any]]:
        db = db_handler.get_db()
        doc = await db["blogs"].find_one({**PUBLISHED_FILTER, "slug": slug}, {"_id": 0})
        return to_post(doc) if doc else None

    return await cache_manager.get(f"blog_post_{slug}", _fetch)


async def get_related(category: str, exclude_slug: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Returns recent posts in the same category, excluding the current one."""
    cards = await get_published_cards()
    same = [c for c in cards if c["category"].lower() == (category or "").lower() and c["slug"] != exclude_slug]
    if len(same) < limit:
        others = [c for c in cards if c["slug"] != exclude_slug and c not in same]
        same = same + others
    return same[:limit]


def paginate(cards: List[Dict[str, Any]], page: int, per_page: int, category: str = "") -> Dict[str, Any]:
    """Filters cards by category and returns one page plus navigation metadata."""
    filtered = cards
    if category and category.lower() != "all":
        filtered = [c for c in cards if c["category"].lower() == category.lower()]
    total = len(filtered)
    start = max(0, (page - 1) * per_page)
    items = filtered[start:start + per_page]
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_next": start + per_page < total,
    }
