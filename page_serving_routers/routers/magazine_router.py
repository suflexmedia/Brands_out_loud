"""Serves the magazine issue listing, per-issue book grids and book detail pages."""

import os
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from page_serving_routers.routers import magazine_service
from page_serving_routers.routers.site_context import base_context

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))


LISTING_TEMPLATE = "magazine_remaster.html"
ISSUE_TEMPLATE = "magazine_issue.html"
BOOK_TEMPLATE = "magazine-book.html"
LAZERVEDA_TEMPLATE = "lazerveda-book.html"
PDF_VIEWER_TEMPLATE = "magazine_pdf_viewer.html"
PDF_FRAME_TEMPLATE = "magazine_flipbook_frame.html"


async def build_listing_context(content_override=None):
    """Builds the magazine listing context, optionally from unsaved content."""
    context = await base_context(active_nav="magazine", page_id="magazine_listing", content_override=content_override)
    issues = await magazine_service.get_issues()
    hero_data = context["content"].get("hero", {})
    featured_slug = hero_data.get("featured_issue_slug")
    featured = next((i for i in issues if i["slug"] == featured_slug), None)
    if not featured:
        featured = {
            "slug": hero_data.get("featured_issue_slug", "the-founder-issue"),
            "url": f"/magazine/{hero_data.get('featured_issue_slug', 'the-founder-issue')}",
            "title": hero_data.get("title", "The founder issue."),
            "issue_number": "12",
            "season_label": "AUTUMN 2024",
            "description": hero_data.get("description", ""),
            "stats": hero_data.get("stats", []),
            "meta_tags": hero_data.get("meta_tags", []),
            "cover_title_lines": hero_data.get("cover_title_lines", ["The", "Issue"]),
            "cover_variant": "edition-bg-1",
            "cover_image_url": "",
        }
    else:
        if not featured.get("stats"):
            featured["stats"] = hero_data.get("stats", [])
        if not featured.get("meta_tags"):
            featured["meta_tags"] = hero_data.get("meta_tags", [])
        if not featured.get("cover_title_lines"):
            featured["cover_title_lines"] = hero_data.get("cover_title_lines", ["The", "Issue"])

    archive_issues = [i for i in issues if not featured or i["slug"] != featured["slug"]]
    if not archive_issues or all(not i.get("badge") for i in archive_issues):
        archive_issues = context["content"].get("archive", {}).get("default_items", [])

    context.update({
        "issues": issues,
        "featured_issue": featured,
        "archive_issues": archive_issues,
        "published_books": await magazine_service.get_all_books(),
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


def _with_book_section_defaults(content: dict) -> dict:
    """Returns a shallow copy of book_detail content with default section labels filled in."""
    v2_data = magazine_service.get_hidden_lens_v2_data()
    merged = dict(content or {})
    existing_sections = {k: v for k, v in (merged.get("sections") or {}).items() if v}
    merged["sections"] = {**v2_data["default_sections"], **existing_sections}
    return merged


async def build_book_context(issue_slug: str, book_slug: str, content_override=None):
    """Builds the book context, returning None when the book is missing."""
    book = await magazine_service.get_book(issue_slug, book_slug)
    if not book:
        return None
    context = await base_context(active_nav="magazine", page_id="book_detail", content_override=content_override)
    context.update({
        "content": _with_book_section_defaults(context.get("content")),
        "book": book,
        "issue": await magazine_service.get_issue(issue_slug),
        "more_books": await magazine_service.get_other_books(issue_slug, book_slug),
    })
    return context


async def build_hidden_lens_v2_context(content_override=None):
    """Builds the recovered full-content context for The Hidden Lens v2 page."""
    context = await base_context(active_nav="magazine", page_id="book_detail", content_override=content_override)
    v2_data = magazine_service.get_hidden_lens_v2_data()
    context.update({
        "content": _with_book_section_defaults(context.get("content")),
        "book": v2_data["book"],
        "issue": await magazine_service.get_issue("the-founder-issue"),
        "more_books": v2_data["more_books"],
    })
    return context


@router.get("/magazine", tags=["Pages"])
async def serve_magazine_listing(request: Request):
    """Serves the magazine landing page listing every published issue."""
    return templates.TemplateResponse(request, LISTING_TEMPLATE, await build_listing_context())


@router.get("/magazine/lazer-veda", tags=["Pages"])
async def serve_lazerveda_book(request: Request):
    """Serves the dedicated LaserVEDA book landing page."""
    context = await base_context(active_nav="magazine")
    context["seo"] = {
        "title": "LaserVEDA® — Healing at the Speed of Light | Brands Out Loud",
        "description": "From Pain to Purpose - A Doctor's Journey Through Loss, Light, and the Fight to Make Healing Gentle Again.",
    }
    return templates.TemplateResponse(request, LAZERVEDA_TEMPLATE, context)


@router.get("/magazine/the-hidden-lens", tags=["Pages"])
async def serve_hidden_lens_book(request: Request):
    """Serves The Hidden Lens standalone book landing page."""
    book = await magazine_service.get_book_by_slug("the-hidden-lens")
    if not book:
        context = await build_hidden_lens_v2_context()
    else:
        issue_slug = book.get("issue_slug", "the-founder-issue")
        context = await base_context(active_nav="magazine", page_id="book_detail")
        context.update({
            "content": _with_book_section_defaults(context.get("content")),
            "book": book,
            "issue": await magazine_service.get_issue(issue_slug),
            "more_books": await magazine_service.get_other_books(issue_slug, "the-hidden-lens"),
        })
    return templates.TemplateResponse(request, BOOK_TEMPLATE, context)


@router.get("/magazine/{issue_slug}", tags=["Pages"])
async def serve_issue_books(request: Request, issue_slug: str):
    """Serves the grid of books belonging to one magazine issue."""
    context = await build_issue_context(issue_slug)
    if not context:
        raise HTTPException(status_code=404, detail="Issue not found")
    return templates.TemplateResponse(request, ISSUE_TEMPLATE, context)


@router.get("/magazine/india-in-a-centennium/the-hidden-lens-v2", tags=["Pages"])
async def serve_hidden_lens_v2(request: Request):
    """Serves the recovered pre-templatization version of The Hidden Lens book page."""
    context = await build_hidden_lens_v2_context()
    return templates.TemplateResponse(request, BOOK_TEMPLATE, context)


@router.get("/magazine/{issue_slug}/read", tags=["Pages"])
async def serve_issue_pdf_reader(request: Request, issue_slug: str):
    """Serves the interactive flipbook PDF reader for a magazine issue."""
    issue = await magazine_service.get_issue(issue_slug)
    if not issue or not issue.get("pdf_url"):
        raise HTTPException(status_code=404, detail="Issue PDF not found")
    context = await base_context(active_nav="magazine")
    all_issues = await magazine_service.get_issues()
    other_issues = [item for item in all_issues if item["slug"] != issue_slug][:6]
    pdf_url = issue["pdf_url"]
    context.update({
        "seo": {
            "title": f"{issue['title']} — Digital Edition | Brands Out Loud",
            "description": issue.get("description") or f"Read {issue['title']} online in our interactive magazine viewer.",
            "og_image": issue.get("cover_image_url", ""),
        },
        "issue": issue,
        "other_issues": other_issues,
        "download_url": f"/download_proxy?pdf={quote(pdf_url, safe='')}",
    })
    return templates.TemplateResponse(request, PDF_VIEWER_TEMPLATE, context)


@router.get("/magazine/{issue_slug}/viewer-frame", tags=["Pages"])
async def serve_issue_pdf_frame(request: Request, issue_slug: str):
    """Serves the standalone flipbook iframe document for a magazine issue."""
    issue = await magazine_service.get_issue(issue_slug)
    if not issue or not issue.get("pdf_url"):
        raise HTTPException(status_code=404, detail="Issue PDF not found")
    raw_pdf_url = issue["pdf_url"]
    return templates.TemplateResponse(request, PDF_FRAME_TEMPLATE, {
        "issue_title": issue.get("title", "Magazine Flipbook Viewer"),
        "raw_pdf_url": raw_pdf_url,
        "proxy_pdf_url": f"/api/pdf-proxy?url={quote(raw_pdf_url, safe='')}",
    })


@router.get("/magazine/{issue_slug}/{book_slug}", tags=["Pages"])
async def serve_book_detail(request: Request, issue_slug: str, book_slug: str):
    """Serves the sales page for a single book."""
    context = await build_book_context(issue_slug, book_slug)
    if not context:
        book_fallback = await magazine_service.get_book_by_slug(book_slug)
        if book_fallback and book_fallback.get("url"):
            return RedirectResponse(url=book_fallback["url"], status_code=301)
        raise HTTPException(status_code=404, detail="Book not found")
    custom_template = context["book"].get("custom_template")
    if custom_template == LAZERVEDA_TEMPLATE:
        context["seo"] = {
            "title": "LaserVEDA® — Healing at the Speed of Light | Brands Out Loud",
            "description": context["book"].get("subtitle") or context["book"].get("description", ""),
        }
        return templates.TemplateResponse(request, LAZERVEDA_TEMPLATE, context)
    return templates.TemplateResponse(request, BOOK_TEMPLATE, context)
