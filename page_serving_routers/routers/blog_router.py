"""Serves the blog listing, single posts and the paginated listing API."""

import os

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates

from page_serving_routers.routers import blog_service
from page_serving_routers.routers.site_context import base_context, get_blog_categories

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))

LATEST_PAGE_SIZE = 6

LISTING_TEMPLATE = "blog_remaster.html"
POST_TEMPLATE = "blog_page_remaster.html"


async def build_listing_context(content_override=None):
    """Builds the blog listing context, optionally from unsaved content."""
    context = await base_context(active_nav="blog", page_id="blog_listing", content_override=content_override)
    cards = await blog_service.get_published_cards()
    content = context["content"]

    by_slug = {card["slug"]: card for card in cards}

    def pick(slug, fallback_index=None):
        if slug and slug in by_slug:
            return by_slug[slug]
        if fallback_index is not None and len(cards) > fallback_index:
            return cards[fallback_index]
        return None

    hero = content.get("hero", {})
    must_read = content.get("must_read", {})
    deep_dive = content.get("deep_dive", {})

    context.update({
        "categories": await get_blog_categories(),
        "featured_post": pick(hero.get("featured_post_slug"), 0),
        "must_read_main": pick(must_read.get("main_post_slug"), 1),
        "trending_posts": [pick(s) for s in must_read.get("trending_post_slugs", []) if pick(s)] or cards[2:5],
        "latest": blog_service.paginate(cards, 1, LATEST_PAGE_SIZE),
        "deep_dive_featured": pick(deep_dive.get("featured_post_slug"), 0),
        "deep_dive_items": [pick(s) for s in deep_dive.get("item_slugs", []) if pick(s)] or cards[:4],
    })
    return context


async def build_post_context(slug: str, content_override=None):
    """Builds the single post context, returning None when the post is missing."""
    post = await blog_service.get_post(slug)
    if not post:
        return None
    context = await base_context(active_nav="blog", page_id="blog_post", content_override=content_override)
    context.update({
        "post": post,
        "related_posts": await blog_service.get_related(post["category"], slug),
        "seo": {"title": post["title"], "description": post["excerpt"], "og_image": post["image_url"]},
    })
    return context


@router.get("/blog", tags=["Pages"])
async def serve_blog_listing(request: Request):
    """Serves the blog landing page."""
    return templates.TemplateResponse(request, LISTING_TEMPLATE, await build_listing_context())


@router.get("/api/blogs", tags=["Public API"])
async def api_list_blogs(
    page: int = Query(1, ge=1),
    per_page: int = Query(LATEST_PAGE_SIZE, ge=1, le=24),
    category: str = Query(""),
):
    """Returns a page of blog cards for the listing's load-more control."""
    cards = await blog_service.get_published_cards()
    return blog_service.paginate(cards, page, per_page, category)


@router.get("/blog/{slug}", tags=["Pages"])
async def serve_blog_post(request: Request, slug: str):
    """Serves a single blog post."""
    context = await build_post_context(slug)
    if not context:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(request, POST_TEMPLATE, context)
