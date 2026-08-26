"""Admin API for editable page content, shared site chrome and blog categories."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from cache_manager import cache_manager
from common.auth import require_admin
from database_handler import db_handler

router = APIRouter(prefix="/admin/api/content", tags=["admin_content_api"])

EDITABLE_PAGES = {
    "homepage",
    "blog_listing",
    "blog_post",
    "magazine_listing",
    "magazine_issue",
    "book_detail",
    "contact",
}


@router.get("/pages/{page_id}")
async def get_page(page_id: str, _admin: dict = Depends(require_admin)):
    """Returns the stored content document for one editable page."""
    if page_id not in EDITABLE_PAGES:
        raise HTTPException(status_code=404, detail="Unknown page")
    db = db_handler.get_db()
    doc = await db["page_content"].find_one({"_id": page_id}) or {}
    doc.pop("_id", None)
    return doc


@router.put("/pages/{page_id}")
async def save_page(page_id: str, request: Request, _admin: dict = Depends(require_admin)):
    """Replaces the content document for one editable page."""
    if page_id not in EDITABLE_PAGES:
        raise HTTPException(status_code=404, detail="Unknown page")
    payload: Dict[str, Any] = await request.json()
    payload.pop("_id", None)
    db = db_handler.get_db()
    await db["page_content"].update_one({"_id": page_id}, {"$set": payload}, upsert=True)
    cache_manager.invalidate(f"page_content_{page_id}")
    return {"status": "ok", "message": "Page content saved"}


@router.post("/pages/{page_id}/preview")
async def preview_page(page_id: str, request: Request, _admin: dict = Depends(require_admin)):
    """Renders the live page template using the editor's unsaved content."""
    if page_id not in EDITABLE_PAGES:
        raise HTTPException(status_code=404, detail="Unknown page")

    from fastapi.responses import HTMLResponse

    from page_serving_routers.routers import (
        blog_router,
        contact_router,
        homepage_router,
        magazine_router,
    )

    content = await request.json()
    content.pop("_id", None)
    db = db_handler.get_db()

    def render(template_name: str, context: dict) -> HTMLResponse:
        template = homepage_router.templates.get_template(template_name)
        return HTMLResponse(template.render(**context, request=request))

    def unavailable(message: str) -> HTMLResponse:
        return HTMLResponse(
            "<!doctype html><html><body style=\"font-family:sans-serif;padding:3rem;"
            "color:#555;text-align:center\"><h2 style=\"color:#0D1030\">Preview unavailable</h2>"
            f"<p>{message}</p></body></html>"
        )

    if page_id == "homepage":
        return render(homepage_router.TEMPLATE_NAME, await homepage_router.build_context(content))

    if page_id == "blog_listing":
        return render(blog_router.LISTING_TEMPLATE, await blog_router.build_listing_context(content))

    if page_id == "magazine_listing":
        return render(magazine_router.LISTING_TEMPLATE, await magazine_router.build_listing_context(content))

    if page_id == "contact":
        context = await contact_router.base_context(active_nav="contact", content_override=content)
        return render("contact.html", context)

    if page_id == "blog_post":
        sample = await db["blogs"].find_one({"status": "published", "isDeleted": {"$ne": True}}, {"slug": 1})
        if not sample:
            return unavailable("Publish a blog post to preview this page.")
        context = await blog_router.build_post_context(sample["slug"], content)
        return render(blog_router.POST_TEMPLATE, context)

    if page_id == "magazine_issue":
        sample = await db["magazine_issues"].find_one({"status": "published"}, {"slug": 1})
        if not sample:
            return unavailable("Create a published magazine issue to preview this page.")
        context = await magazine_router.build_issue_context(sample["slug"], content)
        return render(magazine_router.ISSUE_TEMPLATE, context)

    if page_id == "book_detail":
        sample = await db["books"].find_one({"status": "published"}, {"slug": 1, "issue_slug": 1})
        if not sample:
            return unavailable("Create a published book to preview this page.")
        context = await magazine_router.build_book_context(sample["issue_slug"], sample["slug"], content)
        return render(magazine_router.BOOK_TEMPLATE, context)

    return unavailable("No preview is configured for this page.")


@router.get("/site-settings")
async def get_site_settings(_admin: dict = Depends(require_admin)):
    """Returns the shared nav and footer settings."""
    db = db_handler.get_db()
    doc = await db["site_settings"].find_one({"_id": "site_settings"}) or {}
    doc.pop("_id", None)
    return doc


@router.put("/site-settings")
async def save_site_settings(request: Request, _admin: dict = Depends(require_admin)):
    """Replaces the shared nav and footer settings."""
    payload: Dict[str, Any] = await request.json()
    payload.pop("_id", None)
    if not payload.get("nav") or not payload.get("footer"):
        raise HTTPException(status_code=400, detail="Both nav and footer are required")
    db = db_handler.get_db()
    await db["site_settings"].update_one({"_id": "site_settings"}, {"$set": payload}, upsert=True)
    cache_manager.invalidate("site_settings")
    return {"status": "ok", "message": "Site settings saved"}


@router.post("/site-settings/preview")
async def preview_site_settings(request: Request, _admin: dict = Depends(require_admin)):
    """Renders the homepage using unsaved navigation and footer settings."""
    from fastapi.responses import HTMLResponse

    from page_serving_routers.routers import homepage_router
    from page_serving_routers.routers.site_context import base_context as build_base

    payload = await request.json()
    payload.pop("_id", None)
    context = await build_base(active_nav="home", page_id="homepage", site_override=payload)
    template = homepage_router.templates.get_template(homepage_router.TEMPLATE_NAME)
    return HTMLResponse(template.render(**context, request=request))


@router.get("/blog-categories")
async def get_categories(_admin: dict = Depends(require_admin)):
    """Returns the admin-managed blog category list."""
    db = db_handler.get_db()
    doc = await db["blog_categories"].find_one({"_id": "blog_categories"}) or {}
    return doc.get("categories", [])


@router.put("/blog-categories")
async def save_categories(request: Request, _admin: dict = Depends(require_admin)):
    """Replaces the blog category list."""
    from common.text_utils import slugify

    payload = await request.json()
    raw = payload.get("categories", payload if isinstance(payload, list) else [])
    categories = []
    for index, item in enumerate(raw):
        label = (item.get("label") or "").strip()
        if not label:
            continue
        categories.append({
            "slug": item.get("slug") or slugify(label),
            "label": label,
            "order": item.get("order", index + 1),
        })
    if not categories:
        raise HTTPException(status_code=400, detail="At least one category is required")
    db = db_handler.get_db()
    await db["blog_categories"].update_one(
        {"_id": "blog_categories"}, {"$set": {"categories": categories}}, upsert=True
    )
    cache_manager.invalidate("blog_categories")
    cache_manager.invalidate("blog_listing")
    return {"status": "ok", "message": "Categories saved"}
