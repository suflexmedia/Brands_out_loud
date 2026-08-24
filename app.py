from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import time
import hashlib
import asyncio
import httpx
import uvicorn
import bcrypt
from pymongo import ASCENDING

from page_serving_routers.routers.homepage_router import router as homepage_router
from page_serving_routers.routers.magazine_router import router as magazine_router
from page_serving_routers.routers.blog_router import router as blog_router
from page_serving_routers.routers.contact_router import router as contact_router
from page_serving_routers.routers.auth_router import router as auth_router
from page_serving_routers.routers.sitemap_router import router as sitemap_router
from page_serving_routers.routers.admin_router import router as admin_router
from API_ROUTERS.admin.admin_blog_router import router as admin_blog_api_router
from API_ROUTERS.admin.admin_magazine_router import router as admin_magazine_api_router
from API_ROUTERS.admin.admin_analytics_router import router as admin_analytics_api_router
from API_ROUTERS.admin.admin_content_router import router as admin_content_api_router
from API_ROUTERS.admin.admin_magazine_issue_router import router as admin_magazine_issue_api_router

from database_handler import db_handler
from bucket_handler import bucket_handler
from cache_manager import cache_manager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup and shutdown logic.
    """
    import json
    
    try:
        db_handler.connect()
        bucket_handler.connect()
        
        # Seed database collections if they are empty
        db = db_handler.get_db()
        json_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JSON_FILES")
        
        for singleton in ["site_settings", "blog_categories"]:
            if await db[singleton].count_documents({}) == 0:
                try:
                    with open(os.path.join(json_dir, f"{singleton}.json"), "r", encoding="utf-8") as f:
                        await db[singleton].insert_one(json.load(f))
                    print(f"Seeded {singleton} collection.")
                except FileNotFoundError:
                    print(f"Seed file not found for {singleton}")

        for page_id in ["homepage", "blog_listing", "magazine_listing", "magazine_issue",
                        "blog_post", "book_detail", "contact"]:
            if await db["page_content"].count_documents({"_id": page_id}) == 0:
                try:
                    with open(os.path.join(json_dir, f"page_{page_id}.json"), "r", encoding="utf-8") as f:
                        doc = json.load(f)
                    doc["_id"] = page_id
                    await db["page_content"].insert_one(doc)
                    print(f"Seeded page_content/{page_id}.")
                except FileNotFoundError:
                    print(f"Seed file not found for page_{page_id}")

        for collection, field in [("blogs", "slug"), ("magazine_issues", "slug")]:
            try:
                await db[collection].create_index([(field, ASCENDING)], unique=True, name=f"{collection}_{field}_unique")
            except Exception as idx_err:
                print(f"Index note for {collection}: {idx_err}")
        try:
            await db["books"].create_index(
                [("issue_slug", ASCENDING), ("slug", ASCENDING)], unique=True, name="books_issue_slug_unique"
            )
        except Exception as idx_err:
            print(f"Index note for books: {idx_err}")

        # Blogs
        if await db["blogs"].count_documents({}) == 0:
            try:
                with open(os.path.join(json_dir, "blog.json"), "r", encoding="utf-8") as f:
                    blog_data = json.load(f)
                if isinstance(blog_data, list) and len(blog_data) > 0:
                    await db["blogs"].insert_many(blog_data)
                elif isinstance(blog_data, dict):
                    blog_list = list(blog_data.values())
                    if len(blog_list) > 0:
                        await db["blogs"].insert_many(blog_list)
                print("Seeded blogs collection.")
            except FileNotFoundError:
                print("Seed file not found for blogs")

        # Admin Users Collection
        if await db["admin_users"].count_documents({}) == 0:
            admin_username = os.environ.get("ADMIN_USERNAME", "admin")
            admin_password = os.environ.get("ADMIN_PASSWORD", "password")
            
            # Hash the password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
            
            default_admin = {
                "username": admin_username,
                "password_hash": hashed_password,
                "role": "system_admin",
                "permissions": ["analytics", "edit_pages", "blog_section", "magazine_section"],
                "created_at": time.time()
            }
            await db["admin_users"].insert_one(default_admin)
            print("Seeded default admin user into admin_users collection.")

        # Ensure older admin users are migrated to system_admin role
        await db["admin_users"].update_many(
            {"$or": [{"role": "system administrator"}, {"role": {"$exists": False}}]},
            {"$set": {
                "role": "system_admin",
                "permissions": ["analytics", "edit_pages", "blog_section", "magazine_section"]
            }}
        )

        from datetime import datetime, timedelta
        try:
            await db["page_views"].create_index(
                [("timestamp", ASCENDING)],
                expireAfterSeconds=90 * 24 * 60 * 60,
                name="page_views_ttl_90d"
            )
            await db["page_views"].create_index(
                [("path", ASCENDING), ("timestamp", ASCENDING)],
                name="page_views_path_ts"
            )
            await db["page_views"].create_index(
                [("ip_hash", ASCENDING), ("timestamp", ASCENDING)],
                name="page_views_ip_ts"
            )
            print("Page views indexes ensured.")
        except Exception as idx_err:
            print(f"Page views index creation note: {idx_err}")

    except Exception as e:
        print(f"Error during startup connection initialization: {e}")
    yield
    
    try:
        db_handler.disconnect()
    except Exception as e:
        print(f"Error during shutdown connection cleanup: {e}")

class HealthCheck(BaseModel):
    """Data model for health check response."""
    status: str

TRACKED_PREFIXES = ("/", "/blog", "/magazine", "/contact", "/login")
EXCLUDED_PREFIXES = ("/static/", "/admin/", "/api/", "/health", "/download_proxy", "/favicon", "/sitemap", "/robots.txt")


def _parse_device_type(ua: str) -> str:
    """Determine device type from user-agent string."""
    ua_lower = ua.lower()
    if any(kw in ua_lower for kw in ("mobile", "android", "iphone", "ipod", "opera mini", "iemobile")):
        return "mobile"
    if any(kw in ua_lower for kw in ("ipad", "tablet", "kindle", "silk", "playbook")):
        return "tablet"
    if "bot" in ua_lower or "crawler" in ua_lower or "spider" in ua_lower:
        return "bot"
    return "desktop"


def _should_track(path: str, method: str) -> bool:
    """Decide whether a request path should be tracked for analytics."""
    if method != "GET":
        return False
    for prefix in EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return False
    if path == "/":
        return True
    for prefix in TRACKED_PREFIXES:
        if prefix != "/" and path.startswith(prefix):
            return True
    return False


app = FastAPI(title="Brands of cloud", lifespan=lifespan)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """
    Middleware to log the total execution time of the request
    and track public page views in MongoDB for analytics.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    print(f"API Execution Time | [{request.method}] {request.url.path} | Total Time: {process_time:.4f}s")

    req_path = request.url.path
    if _should_track(req_path, request.method):
        try:
            from datetime import datetime, timezone
            client_ip = request.client.host if request.client else "unknown"
            ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
            user_agent = request.headers.get("user-agent", "")
            referer = request.headers.get("referer", "")

            page_view = {
                "path": req_path,
                "timestamp": datetime.now(timezone.utc),
                "process_time": round(process_time, 4),
                "ip_hash": ip_hash,
                "user_agent": user_agent,
                "referer": referer,
                "device_type": _parse_device_type(user_agent),
            }

            db = db_handler.get_db()
            asyncio.create_task(db["page_views"].insert_one(page_view))
        except Exception as track_err:
            print(f"Page view tracking error: {track_err}")

    return response


app.mount("/static", StaticFiles(directory="page_serving_routers/static"), name="static")


app.include_router(sitemap_router)
app.include_router(homepage_router)
app.include_router(magazine_router)
app.include_router(blog_router)
app.include_router(contact_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(admin_blog_api_router)
app.include_router(admin_magazine_api_router)
app.include_router(admin_analytics_api_router)
app.include_router(admin_content_api_router)
app.include_router(admin_magazine_issue_api_router)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Returns the health status of the API."""
    return {"status": "ok"}


@app.get("/admin/api/cache/status")
async def cache_status(request: Request):
    """Returns the current state of all application caches."""
    from API_ROUTERS.admin.admin_blog_router import is_authenticated
    if not await is_authenticated(request):
        from fastapi import HTTPException as HE
        raise HE(status_code=401, detail="Unauthorized")
    return cache_manager.get_status()


@app.post("/admin/api/cache/invalidate")
async def cache_invalidate(request: Request):
    """
    Invalidate one or all caches.
    Body: {"key": "blogs"} to invalidate a specific cache,
          {"key": "all"} to invalidate everything,
          {"prefix": "service_"} to invalidate by prefix.
    """
    from API_ROUTERS.admin.admin_blog_router import is_authenticated
    if not await is_authenticated(request):
        from fastapi import HTTPException as HE
        raise HE(status_code=401, detail="Unauthorized")

    body = await request.json()
    key = body.get("key")
    prefix = body.get("prefix")

    if key == "all":
        cache_manager.invalidate_all()
        return {"status": "ok", "message": "All caches invalidated"}
    elif key:
        cache_manager.invalidate(key)
        return {"status": "ok", "message": f"Cache '{key}' invalidated"}
    elif prefix:
        cache_manager.invalidate_pattern(prefix)
        return {"status": "ok", "message": f"Caches with prefix '{prefix}' invalidated"}
    else:
        from fastapi import HTTPException as HE
        raise HE(status_code=400, detail="Provide 'key' or 'prefix' in request body")


@app.get("/download_proxy")
async def download_proxy(
    pdf: str = Query(..., description="URL of the PDF to download"),
    filename: Optional[str] = Query("document.pdf", description="Filename for the download")
):
    """
    Proxies a PDF download from an external URL so the browser
    receives it as a file attachment with the correct headers.
    """
    async def stream_pdf():
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", pdf) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

    safe_filename = filename or pdf.split("/")[-1] or "document.pdf"

    return StreamingResponse(
        stream_pdf(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Cache-Control": "no-cache",
        }
    )


class PdfDownloadFormData(BaseModel):
    """Data model for the PDF download form submission."""
    first_name: str
    last_name: Optional[str] = None
    email: str
    company_name: Optional[str] = None
    mobile_number: Optional[str] = None
    pdf_link: str


@app.post("/api/pdf-download-form")
async def pdf_download_form(form_data: PdfDownloadFormData):
    """
    Stores the PDF download form submission in the database
    for lead tracking purposes.
    """
    try:
        db = db_handler.get_db()
        collection = db["pdf_download_leads"]
        await collection.insert_one(form_data.model_dump())
        return {"status": "ok"}
    except Exception as e:
        print(f"Error saving PDF download form: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)