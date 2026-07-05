"""Serves individual magazine pages with cached data and PDF viewer."""

import os
from urllib.parse import unquote
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
from page_serving_routers.routers.navbar_fetcher import get_navbar_data
from cache_manager import cache_manager

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def _fetch_magazine_page_from_db():
    """Fetch magazine page data directly from MongoDB."""
    db = db_handler.get_db()
    collection = db["magazine_page"]

    doc_count = await collection.count_documents({})
    if doc_count == 0:
        return {}
    return await collection.find_one({})


async def get_magazine_page_data():
    """
    Returns magazine page data using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    return await cache_manager.get("magazine_page", _fetch_magazine_page_from_db)


def build_pdf_url(pdf_name: str) -> str:
    """
    Constructs the full PDF URL from the MinIO public endpoint,
    bucket name, and the PDF filename.
    """
    endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "").rstrip("/")
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "brands-out-loud")
    decoded_name = unquote(pdf_name)
    return f"{endpoint}/{bucket_name}/{decoded_name}"


async def find_magazine_by_slug(slug: str):
    """Look up a magazine from the magazines collection by slug."""
    db = db_handler.get_db()
    return await db["magazines"].find_one({"slug": slug})


@router.get("/api/magazines/grid", tags=["Public API"])
async def public_magazines_grid(
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=18),
    exclude_slug: str = Query(None),
):
    """
    Public endpoint for the explore earlier editions grid.
    Returns paginated published magazines, excluding the current one if specified.
    Max 9 per page with pagination metadata.
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

    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        "magazines": magazines,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get("/magazine/{pdf_name:path}", tags=["Pages"])
async def serve_magazine_page(request: Request, pdf_name: str):
    """
    Serves the magazine page with the PDF viewer.
    First checks if pdf_name matches a magazine slug in the magazines collection.
    If found, uses the stored pdf_url. Otherwise falls back to constructing
    the URL from MinIO endpoint + bucket + pdf_name.
    """
    data = await get_magazine_page_data()
    navbar = await get_navbar_data()

    magazine = await find_magazine_by_slug(pdf_name)

    if magazine:
        pdf_url = magazine.get("pdf_url", "")
        current_slug = magazine.get("slug", "")
        magazine_title = magazine.get("title", "")
    else:
        pdf_url = build_pdf_url(pdf_name)
        current_slug = ""
        magazine_title = ""

    print(f"Magazine Page | PDF Name: {pdf_name} | Full URL: {pdf_url} | Slug: {current_slug}")
    return templates.TemplateResponse(
        request=request,
        name="magazine-page.html",
        context={
            "request": request,
            "data": data,
            "navbar": navbar,
            "pdf_url": pdf_url,
            "current_slug": current_slug,
            "magazine_title": magazine_title,
        }
    )
