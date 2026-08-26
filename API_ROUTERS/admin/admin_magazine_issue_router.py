"""Admin CRUD for magazine issues and the books that belong to them."""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from common.auth import require_admin
from common.cache_helpers import invalidate_magazine_caches
from common.text_utils import SLUG_PATTERN, slugify
from database_handler import db_handler

router = APIRouter(prefix="/admin/api/magazine", tags=["admin_magazine_api"])

ISSUE_FIELDS = [
    "title", "issue_number", "season_label", "badge", "description",
    "cover_image_url", "cover_variant", "cover_title_lines", "brand",
    "stats", "meta_tags", "pdf_url", "status", "order",
]

BOOK_FIELDS = [
    "title", "subtitle", "author_name", "author_avatar_url", "category",
    "pages_label", "price", "brand", "tag", "cover_image_url", "cover_variant",
    "cover_title_lines", "background_number", "description", "badges", "rating",
    "store_url", "sample_url", "about", "covers", "highlights", "audience",
    "cta_banner", "status", "order",
]


ORDINAL_KEYS = {"num", "order", "stars", "brand", "cover_variant", "status"}


def _is_blank(value) -> bool:
    """Returns True when a value carries no author-supplied content."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _prune(value):
    """Recursively drops list entries the admin left completely empty."""
    if isinstance(value, dict):
        return {key: _prune(item) for key, item in value.items()}
    if isinstance(value, list):
        cleaned = []
        for item in value:
            pruned = _prune(item)
            if isinstance(pruned, dict):
                meaningful = {k: v for k, v in pruned.items() if k not in ORDINAL_KEYS}
                if meaningful and all(_is_blank(v) for v in meaningful.values()):
                    continue
            elif _is_blank(pruned):
                continue
            cleaned.append(pruned)
        return cleaned
    return value


def _pick(payload: Dict[str, Any], allowed) -> Dict[str, Any]:
    """Returns only the whitelisted keys present in the payload, pruned of empty rows."""
    return {key: _prune(payload[key]) for key in allowed if key in payload}


async def _resolve_slug(payload: Dict[str, Any], collection: str, extra_filter: Dict[str, Any]) -> str:
    """Derives and validates a unique slug for a new document."""
    db = db_handler.get_db()
    slug = (payload.get("slug") or slugify(payload.get("title", ""))).strip()
    if not slug or not SLUG_PATTERN.match(slug):
        raise HTTPException(status_code=400, detail="Slug must be lowercase letters, numbers and hyphens")
    if await db[collection].find_one({**extra_filter, "slug": slug}):
        raise HTTPException(status_code=400, detail="That slug is already in use")
    return slug


@router.get("/issues")
async def list_issues(_admin: dict = Depends(require_admin)):
    """Returns every magazine issue, newest first."""
    db = db_handler.get_db()
    cursor = db["magazine_issues"].find({}).sort("created_at", -1)
    issues = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        issues.append(doc)
    return issues


@router.post("/issues")
async def create_issue(request: Request, _admin: dict = Depends(require_admin)):
    """Creates a magazine issue."""
    payload = await request.json()
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="Title is required")
    slug = await _resolve_slug(payload, "magazine_issues", {})
    doc = _pick(payload, ISSUE_FIELDS)
    doc.update({"slug": slug, "created_at": time.time()})
    doc.setdefault("status", "published")
    db = db_handler.get_db()
    await db["magazine_issues"].insert_one(doc)
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Issue created", "slug": slug}


@router.put("/issues/{slug}")
async def update_issue(slug: str, request: Request, _admin: dict = Depends(require_admin)):
    """Updates a magazine issue without allowing its slug to change."""
    payload = await request.json()
    doc = _pick(payload, ISSUE_FIELDS)
    db = db_handler.get_db()
    result = await db["magazine_issues"].update_one({"slug": slug}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Issue updated"}


@router.delete("/issues/{slug}")
async def delete_issue(slug: str, _admin: dict = Depends(require_admin)):
    """Deletes an issue only when it has no books attached."""
    db = db_handler.get_db()
    if await db["books"].count_documents({"issue_slug": slug}) > 0:
        raise HTTPException(status_code=400, detail="Remove this issue's books before deleting it")
    result = await db["magazine_issues"].delete_one({"slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Issue deleted"}


@router.get("/issues/{issue_slug}/books")
async def list_books(issue_slug: str, _admin: dict = Depends(require_admin)):
    """Returns every book belonging to an issue."""
    db = db_handler.get_db()
    cursor = db["books"].find({"issue_slug": issue_slug}).sort("order", 1)
    books = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        books.append(doc)
    return books


@router.post("/issues/{issue_slug}/books")
async def create_book(issue_slug: str, request: Request, _admin: dict = Depends(require_admin)):
    """Creates a book inside an issue."""
    db = db_handler.get_db()
    if not await db["magazine_issues"].find_one({"slug": issue_slug}):
        raise HTTPException(status_code=404, detail="Issue not found")
    payload = await request.json()
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="Title is required")
    slug = await _resolve_slug(payload, "books", {"issue_slug": issue_slug})
    doc = _pick(payload, BOOK_FIELDS)
    doc.update({"slug": slug, "issue_slug": issue_slug, "created_at": time.time()})
    doc.setdefault("status", "published")
    await db["books"].insert_one(doc)
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Book created", "slug": slug}


@router.put("/issues/{issue_slug}/books/{slug}")
async def update_book(issue_slug: str, slug: str, request: Request, _admin: dict = Depends(require_admin)):
    """Updates a book without allowing its slug or parent issue to change."""
    payload = await request.json()
    doc = _pick(payload, BOOK_FIELDS)
    db = db_handler.get_db()
    result = await db["books"].update_one({"issue_slug": issue_slug, "slug": slug}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Book updated"}


@router.delete("/issues/{issue_slug}/books/{slug}")
async def delete_book(issue_slug: str, slug: str, _admin: dict = Depends(require_admin)):
    """Deletes a book."""
    db = db_handler.get_db()
    result = await db["books"].delete_one({"issue_slug": issue_slug, "slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    invalidate_magazine_caches()
    return {"status": "ok", "message": "Book deleted"}
