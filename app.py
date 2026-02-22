from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import time
import httpx
import uvicorn

from PAGE_SERVING_ROUTERS.routers.homepage_router import router as homepage_router
from PAGE_SERVING_ROUTERS.routers.service_router import router as service_router
from PAGE_SERVING_ROUTERS.routers.magazine_homepage_router import router as magazine_homepage_router
from PAGE_SERVING_ROUTERS.routers.magazine_page_router import router as magazine_page_router
from PAGE_SERVING_ROUTERS.routers.blog_router import router as blog_router
from PAGE_SERVING_ROUTERS.routers.auth_router import router as auth_router

from database_handler import db_handler
from bucket_handler import bucket_handler

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
        
        # Homepage
        if await db["homepage"].count_documents({}) == 0:
            try:
                with open(os.path.join(json_dir, "homepage.json"), "r", encoding="utf-8") as f:
                    await db["homepage"].insert_one(json.load(f))
                print("Seeded homepage collection.")
            except FileNotFoundError:
                print("Seed file not found for homepage")
                
        # Magazine Homepage
        if await db["magazine_homepage"].count_documents({}) == 0:
            try:
                with open(os.path.join(json_dir, "magazine_homepage.json"), "r", encoding="utf-8") as f:
                    await db["magazine_homepage"].insert_one(json.load(f))
                print("Seeded magazine_homepage collection.")
            except FileNotFoundError:
                print("Seed file not found for magazine_homepage")
                
        # Magazine Page
        magazine_page_doc = await db["magazine_page"].find_one({})
        magazine_grid = magazine_page_doc.get("magazine_grid_section", []) if magazine_page_doc else []
        has_new_schema = len(magazine_grid) > 0 and "pdf_name" in magazine_grid[0]
        needs_reseed = magazine_page_doc is None or "ad_banner_1" not in magazine_page_doc or not has_new_schema
        if needs_reseed:
            try:
                await db["magazine_page"].drop()
                with open(os.path.join(json_dir, "magazine_page.json"), "r", encoding="utf-8") as f:
                    await db["magazine_page"].insert_one(json.load(f))
                print("Seeded magazine_page collection.")
            except FileNotFoundError:
                print("Seed file not found for magazine_page")

        # Services
        for category in ["business", "technology", "gcc", "sustainability", "semiconductor"]:
            col_name = f"service_{category}"
            if await db[col_name].count_documents({}) == 0:
                try:
                    with open(os.path.join(json_dir, f"{col_name}.json"), "r", encoding="utf-8") as f:
                        await db[col_name].insert_one(json.load(f))
                    print(f"Seeded {col_name} collection.")
                except FileNotFoundError:
                    print(f"Seed file not found for {col_name}")

        # Navbar
        if await db["navbar"].count_documents({}) == 0:
            try:
                with open(os.path.join(json_dir, "navbar.json"), "r", encoding="utf-8") as f:
                    await db["navbar"].insert_one(json.load(f))
                print("Seeded navbar collection.")
            except FileNotFoundError:
                print("Seed file not found for navbar")

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

app = FastAPI(title="Brands of cloud", lifespan=lifespan)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """
    Middleware to log the total execution time of the request.
    This helps identify slow API calls overall.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    print(f"API Execution Time | [{request.method}] {request.url.path} | Total Time: {process_time:.4f}s")
    return response


app.mount("/static", StaticFiles(directory="PAGE_SERVING_ROUTERS/static"), name="static")


app.include_router(homepage_router)
app.include_router(service_router)
app.include_router(magazine_homepage_router)
app.include_router(magazine_page_router)
app.include_router(blog_router)
app.include_router(auth_router)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Returns the health status of the API."""
    return {"status": "ok"}


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