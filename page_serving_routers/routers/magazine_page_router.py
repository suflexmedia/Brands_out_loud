import os
from urllib.parse import unquote
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database_handler.connection import db_handler
from PAGE_SERVING_ROUTERS.routers.navbar_fetcher import get_navbar_data
import time

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


magazine_page_cache = {
    "data": None,
    "expires_at": 0
}
CACHE_TTL = 300


async def get_magazine_page_data():
    """
    Fetches the magazine page data from the cache if valid,
    otherwise fetches from MongoDB and updates the cache.
    """
    current_time = time.time()

    if magazine_page_cache["data"] and current_time < magazine_page_cache["expires_at"]:
        magazine_page_cache["expires_at"] = current_time + CACHE_TTL
        return magazine_page_cache["data"]

    db_start_time = time.time()
    db = db_handler.get_db()
    collection = db["magazine_page"]

    doc_count = await collection.count_documents({})
    if doc_count == 0:
        magazine_page_data = {}
    else:
        magazine_page_data = await collection.find_one({})

    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | Magazine Page Data | Time: {db_elapsed:.4f}s")

    magazine_page_cache["data"] = magazine_page_data
    magazine_page_cache["expires_at"] = current_time + CACHE_TTL

    return magazine_page_data


def build_pdf_url(pdf_name: str) -> str:
    """
    Constructs the full PDF URL from the MinIO public endpoint,
    bucket name, and the PDF filename.
    """
    endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "").rstrip("/")
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "brands-out-loud")
    decoded_name = unquote(pdf_name)
    return f"{endpoint}/{bucket_name}/{decoded_name}"


@router.get("/magazine/{pdf_name:path}", tags=["Pages"])
async def serve_magazine_page(request: Request, pdf_name: str):
    """
    Serves the magazine page with the PDF viewer.
    Only the PDF filename is passed as a URL parameter.
    The full PDF URL is constructed from MINIO_PUBLIC_ENDPOINT + MINIO_BUCKET_NAME + pdf_name.
    """
    data = await get_magazine_page_data()
    navbar = await get_navbar_data()
    pdf_url = build_pdf_url(pdf_name)
    print(f"Magazine Page | PDF Name: {pdf_name} | Full URL: {pdf_url}")
    return templates.TemplateResponse(
        "magazine-page.html",
        {"request": request, "data": data, "navbar": navbar, "pdf_url": pdf_url}
    )
