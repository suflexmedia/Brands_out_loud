from fastapi import APIRouter, Request, HTTPException
from database_handler import db_handler
from cache_manager import cache_manager
import time
import uuid

router = APIRouter(prefix="/admin/api", tags=["admin_magazine_api"])

COOKIE_NAME = "admin_session"


async def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid admin session cookie in the DB."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False

    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


@router.get("/magazines/categories")
async def api_magazine_categories(request: Request):
    """Return sorted list of distinct non-empty category values from the magazines collection."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    categories = await db["magazines"].distinct("category")
    result = sorted([c for c in categories if c and c.strip()])
    return result


@router.get("/magazines")
async def api_list_magazines(request: Request):
    """Get all magazines sorted by created_at descending."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    magazines = await db["magazines"].find({}).sort("created_at", -1).to_list(length=None)

    for mag in magazines:
        if "_id" in mag:
            mag["_id"] = str(mag["_id"])

    return magazines


@router.post("/magazines")
async def api_create_magazine(request: Request):
    """Create a new magazine."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    data = await request.json()

    title = data.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    pdf_url = data.get("pdf_url")
    if not pdf_url:
        raise HTTPException(status_code=400, detail="PDF URL is required")

    image_url = data.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")

    slug = data.get("slug")
    if not slug:
        raise HTTPException(status_code=400, detail="Slug is required")

    existing = await db["magazines"].find_one({"slug": slug})
    if existing:
        raise HTTPException(status_code=400, detail="Magazine with this slug already exists")

    magazine = {
        "slug": slug,
        "title": title,
        "pdf_url": pdf_url,
        "image_url": image_url,
        "category": data.get("category", ""),
        "status": data.get("status", "published"),
        "date": data.get("date", ""),
        "created_at": time.time(),
    }

    await db["magazines"].insert_one(magazine)

    cache_manager.invalidate("magazines")
    cache_manager.invalidate("magazines_grid")
    cache_manager.invalidate_pattern("magazines_page_")
    cache_manager.invalidate("sitemap_index")
    cache_manager.invalidate("sitemap_magazine")

    return {"status": "ok", "message": "Magazine created successfully"}


@router.put("/magazines/{slug}")
async def api_update_magazine(request: Request, slug: str):
    """Update an existing magazine."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    data = await request.json()

    data.pop("_id", None)

    result = await db["magazines"].update_one(
        {"slug": slug},
        {"$set": data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Magazine not found")

    cache_manager.invalidate("magazines")
    cache_manager.invalidate("magazines_grid")
    cache_manager.invalidate_pattern("magazines_page_")
    cache_manager.invalidate("sitemap_index")
    cache_manager.invalidate("sitemap_magazine")

    return {"status": "ok", "message": "Magazine updated successfully"}


@router.delete("/magazines/{slug}")
async def api_delete_magazine(request: Request, slug: str):
    """Delete a magazine."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    result = await db["magazines"].delete_one({"slug": slug})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Magazine not found")

    cache_manager.invalidate("magazines")
    cache_manager.invalidate("magazines_grid")
    cache_manager.invalidate_pattern("magazines_page_")
    cache_manager.invalidate("sitemap_index")
    cache_manager.invalidate("sitemap_magazine")

    return {"status": "ok", "message": "Magazine deleted successfully"}


@router.get("/magazines/grid")
async def api_magazines_grid(request: Request, page: int = 1, per_page: int = 9, exclude_slug: str = None):
    """
    Get paginated published magazines for the explore earlier editions grid.
    Excludes the current magazine if exclude_slug is provided.
    Returns max 9 per page with pagination info.
    """
    db = db_handler.get_db()

    query = {"status": "published"}
    if exclude_slug:
        query["slug"] = {"$ne": exclude_slug}

    total = await db["magazines"].count_documents(query)
    skip = (page - 1) * per_page

    magazines = await db["magazines"].find(query).sort("created_at", -1).skip(skip).limit(per_page).to_list(length=per_page)

    for mag in magazines:
        if "_id" in mag:
            mag["_id"] = str(mag["_id"])

    total_pages = (total + per_page - 1) // per_page

    return {
        "magazines": magazines,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
