"""Loads shared site chrome and per-page content documents from MongoDB."""

import json
import os
from typing import Any, Dict

from cache_manager import cache_manager
from database_handler import db_handler

JSON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "JSON_FILES")

ASSET_VERSION = "3"


def _load_seed(name: str) -> Dict[str, Any]:
    """Reads a seed document from JSON_FILES, returning an empty dict if absent."""
    try:
        with open(os.path.join(JSON_DIR, f"{name}.json"), "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


async def _fetch_site_settings() -> Dict[str, Any]:
    db = db_handler.get_db()
    doc = await db["site_settings"].find_one({"_id": "site_settings"})
    if not doc:
        doc = _load_seed("site_settings")
    doc.pop("_id", None)
    return doc


async def get_site_settings() -> Dict[str, Any]:
    """Returns the shared nav/footer settings, cached."""
    return await cache_manager.get("site_settings", _fetch_site_settings)


async def get_page_content(page_id: str) -> Dict[str, Any]:
    """Returns the singleton content document for a page, cached per page."""

    async def _fetch() -> Dict[str, Any]:
        db = db_handler.get_db()
        doc = await db["page_content"].find_one({"_id": page_id})
        if not doc:
            doc = _load_seed(f"page_{page_id}")
        doc.pop("_id", None)
        return doc

    return await cache_manager.get(f"page_content_{page_id}", _fetch)


async def get_blog_categories() -> list:
    """Returns the ordered admin-managed blog category list, cached."""

    async def _fetch() -> list:
        db = db_handler.get_db()
        doc = await db["blog_categories"].find_one({"_id": "blog_categories"})
        if not doc:
            doc = _load_seed("blog_categories")
        return sorted(doc.get("categories", []), key=lambda item: item.get("order", 0))

    return await cache_manager.get("blog_categories", _fetch)


async def base_context(
    active_nav: str = "",
    page_id: str = "",
    content_override: Dict[str, Any] = None,
    site_override: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Builds the template context every remaster page needs."""
    site = site_override if site_override is not None else await get_site_settings()
    if content_override is not None:
        content = content_override
    else:
        content = await get_page_content(page_id) if page_id else {}
    return {
        "site": site,
        "content": content,
        "seo": content.get("seo", {}),
        "active_nav": active_nav,
        "asset_version": ASSET_VERSION,
    }
