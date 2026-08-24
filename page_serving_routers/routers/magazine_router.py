"""Serves the magazine issue listing, per-issue book grids and book detail pages."""

import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from page_serving_routers.routers import magazine_service
from page_serving_routers.routers.site_context import base_context

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))


LISTING_TEMPLATE = "magazine_remaster.html"
ISSUE_TEMPLATE = "magazine_issue.html"
BOOK_TEMPLATE = "magazine-book.html"


async def build_listing_context(content_override=None):
    """Builds the magazine listing context, optionally from unsaved content."""
    context = await base_context(active_nav="magazine", page_id="magazine_listing", content_override=content_override)
    issues = await magazine_service.get_issues()
    featured_slug = context["content"].get("hero", {}).get("featured_issue_slug")
    featured = next((i for i in issues if i["slug"] == featured_slug), issues[0] if issues else None)
    context.update({
        "issues": issues,
        "featured_issue": featured,
        "archive_issues": [i for i in issues if not featured or i["slug"] != featured["slug"]],
    })
    return context


async def build_issue_context(issue_slug: str, content_override=None):
    """Builds the issue context, returning None when the issue is missing."""
    issue = await magazine_service.get_issue(issue_slug)
    if not issue:
        return None
    context = await base_context(active_nav="magazine", page_id="magazine_issue", content_override=content_override)
    context.update({
        "issue": issue,
        "books": await magazine_service.get_books(issue_slug),
    })
    return context


async def build_book_context(issue_slug: str, book_slug: str, content_override=None):
    """Builds the book context, returning None when the book is missing."""
    book = await magazine_service.get_book(issue_slug, book_slug)
    if not book:
        return None
    context = await base_context(active_nav="magazine", page_id="book_detail", content_override=content_override)
    context.update({
        "book": book,
        "issue": await magazine_service.get_issue(issue_slug),
        "more_books": await magazine_service.get_other_books(issue_slug, book_slug),
    })
    return context


@router.get("/magazine", tags=["Pages"])
async def serve_magazine_listing(request: Request):
    """Serves the magazine landing page listing every published issue."""
    return templates.TemplateResponse(request, LISTING_TEMPLATE, await build_listing_context())


@router.get("/magazine/{issue_slug}", tags=["Pages"])
async def serve_issue_books(request: Request, issue_slug: str):
    """Serves the grid of books belonging to one magazine issue."""
    context = await build_issue_context(issue_slug)
    if not context:
        raise HTTPException(status_code=404, detail="Issue not found")
    return templates.TemplateResponse(request, ISSUE_TEMPLATE, context)


@router.get("/magazine/{issue_slug}/{book_slug}", tags=["Pages"])
async def serve_book_detail(request: Request, issue_slug: str, book_slug: str):
    """Serves the sales page for a single book."""
    context = await build_book_context(issue_slug, book_slug)
    if not context:
        raise HTTPException(status_code=404, detail="Book not found")
    return templates.TemplateResponse(request, BOOK_TEMPLATE, context)
