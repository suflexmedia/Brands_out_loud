"""Loads magazine issues and their books for the public magazine pages."""

from typing import Any, Dict, List, Optional

from cache_manager import cache_manager
from database_handler import db_handler

PUBLISHED = {"status": "published"}


def issue_card(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens an issue document into the archive-card shape."""
    slug = issue.get("slug", "")
    return {
        "slug": slug,
        "url": f"/magazine/{slug}",
        "title": issue.get("title", ""),
        "issue_number": issue.get("issue_number", ""),
        "season_label": issue.get("season_label", ""),
        "badge": issue.get("badge", ""),
        "description": issue.get("description", ""),
        "cover_image_url": issue.get("cover_image_url", ""),
        "cover_variant": issue.get("cover_variant", "edition-bg-1"),
        "cover_title_lines": issue.get("cover_title_lines", []),
        "brand": issue.get("brand", "BOL"),
        "stats": issue.get("stats", []),
        "meta_tags": issue.get("meta_tags", []),
        "pdf_url": issue.get("pdf_url", ""),
    }


def book_card(book: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens a book document into the grid-card shape."""
    issue_slug = book.get("issue_slug", "")
    slug = book.get("slug", "")
    return {
        "slug": slug,
        "issue_slug": issue_slug,
        "url": book.get("custom_url") or f"/magazine/{issue_slug}/{slug}",
        "custom_template": book.get("custom_template", ""),
        "title": book.get("title", ""),
        "subtitle": book.get("subtitle", ""),
        "author_name": book.get("author_name", ""),
        "category": book.get("category", ""),
        "pages_label": book.get("pages_label", ""),
        "price": book.get("price", {}),
        "brand": book.get("brand", "BOL"),
        "tag": book.get("tag", ""),
        "cover_image_url": book.get("cover_image_url", ""),
        "cover_variant": book.get("cover_variant", "cover-gradient-1"),
        "cover_title_lines": book.get("cover_title_lines", []),
        "background_number": book.get("background_number", ""),
    }


async def get_all_books(limit: int = 12) -> List[Dict[str, Any]]:
    """Returns all published books across issues, ordered by order then newest, cached."""

    async def _fetch() -> List[Dict[str, Any]]:
        db = db_handler.get_db()
        cursor = db["books"].find(PUBLISHED, {"_id": 0}).sort([("order", 1), ("created_at", -1)]).limit(limit)
        return [book_card(doc) async for doc in cursor]

    return await cache_manager.get("magazine_all_books", _fetch)


async def get_issues() -> List[Dict[str, Any]]:
    """Returns all published issues, ordered by order then newest, cached."""

    async def _fetch() -> List[Dict[str, Any]]:
        db = db_handler.get_db()
        cursor = db["magazine_issues"].find(PUBLISHED, {"_id": 0}).sort([("order", 1), ("created_at", -1)])
        return [issue_card(doc) async for doc in cursor]

    return await cache_manager.get("magazine_listing", _fetch)


async def get_issue(slug: str) -> Optional[Dict[str, Any]]:
    """Returns one published issue by slug, cached per slug."""

    async def _fetch() -> Optional[Dict[str, Any]]:
        db = db_handler.get_db()
        doc = await db["magazine_issues"].find_one({**PUBLISHED, "slug": slug}, {"_id": 0})
        return issue_card(doc) if doc else None

    return await cache_manager.get(f"magazine_issue_{slug}", _fetch)


async def get_books(issue_slug: str) -> List[Dict[str, Any]]:
    """Returns the published books belonging to an issue, cached per issue."""

    async def _fetch() -> List[Dict[str, Any]]:
        db = db_handler.get_db()
        cursor = db["books"].find({**PUBLISHED, "issue_slug": issue_slug}, {"_id": 0}).sort("order", 1)
        return [book_card(doc) async for doc in cursor]

    return await cache_manager.get(f"magazine_issue_{issue_slug}_books", _fetch)


async def get_book(issue_slug: str, slug: str) -> Optional[Dict[str, Any]]:
    """Returns the full detail document for one book, cached per book."""

    async def _fetch() -> Optional[Dict[str, Any]]:
        db = db_handler.get_db()
        doc = await db["books"].find_one(
            {**PUBLISHED, "issue_slug": issue_slug, "slug": slug}, {"_id": 0}
        )
        if not doc:
            return None
        detail = book_card(doc)
        detail.update({
            "cover_subtitle": doc.get("cover_subtitle", ""),
            "description": doc.get("description", ""),
            "badges": doc.get("badges", []),
            "rating": doc.get("rating", {}),
            "store_url": doc.get("store_url", "#"),
            "sample_url": doc.get("sample_url", "#"),
            "purchase_label": doc.get("purchase_label", ""),
            "sample_label": doc.get("sample_label", ""),
            "author_avatar_url": doc.get("author_avatar_url", ""),
            "about": doc.get("about", {}),
            "covers": doc.get("covers", []),
            "highlights": doc.get("highlights", []),
            "audience": doc.get("audience", []),
            "cta_banner": doc.get("cta_banner", {}),
        })
        return detail

    return await cache_manager.get(f"magazine_book_{issue_slug}_{slug}", _fetch)


async def get_other_books(issue_slug: str, exclude_slug: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Returns other published books for the 'More from BOL' grid, falling back to default cards."""
    db = db_handler.get_db()
    cursor = db["books"].find(
        {**PUBLISHED, "slug": {"$ne": exclude_slug}}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    books = [book_card(doc) async for doc in cursor]
    if len(books) < limit:
        existing_urls = {item["url"] for item in books}
        for fallback in get_hidden_lens_v2_data()["more_books"]:
            if len(books) >= limit:
                break
            if fallback["url"] not in existing_urls:
                books.append(fallback)
    return books


def get_hidden_lens_v2_data() -> Dict[str, Any]:
    """Returns the complete recovered book payload and fallback section copy for The Hidden Lens v2."""
    return {
        "book": {
            "slug": "the-hidden-lens-v2",
            "issue_slug": "india-in-a-centennium",
            "url": "/magazine/india-in-a-centennium/the-hidden-lens-v2",
            "title": "The Hidden Lens",
            "subtitle": "Understanding Unconscious Bias.",
            "author_name": "Mohit Kapoor",
            "author_avatar_url": "",
            "category": "LEADERSHIP",
            "pages_label": "248 PAGES",
            "brand": "BOL PRESS",
            "tag": "",
            "cover_image_url": "",
            "cover_variant": "cover-gradient-1",
            "cover_title_lines": ["The", "Hidden", "Lens"],
            "background_number": "",
            "description": (
                "A practical guide to the automatic judgements shaping our decisions — "
                "how they form, why they persist, and how greater self-awareness leads to "
                "fairer thinking in life, work, and leadership."
            ),
            "badges": [
                "248 pages",
                "Hardcover + eBook",
                "English",
                "Published Sep 2026",
            ],
            "rating": {
                "stars": "★★★★★",
                "score": "4.8",
            },
            "price": {
                "current": "₹599",
                "original": "₹799",
                "discount_label": "Save 25%",
            },
            "store_url": "#",
            "sample_url": "#",
            "about": {
                "quote": (
                    "Every day we make decisions that feel rational and deliberate. "
                    "Many of them aren't."
                ),
                "paragraphs": [
                    (
                        "In The Hidden Lens, Mohit Kapoor explores one of the most overlooked "
                        "aspects of human behaviour: unconscious bias. He explains how it "
                        "develops, why it affects the choices we make, and how greater "
                        "awareness can lead to fairer decisions in our personal and "
                        "professional lives."
                    ),
                    (
                        "Rather than stopping at theory, Kapoor connects bias to the "
                        "situations people face every day — hiring, leadership, teamwork, "
                        "the technologies we build — and offers simple, practical ways to "
                        "make more thoughtful and inclusive decisions."
                    ),
                    (
                        "Awareness is where change begins. This book is written for "
                        "professionals, educators, students, and curious readers alike — "
                        "anyone who wants to better understand human behaviour and make "
                        "fairer, more thoughtful decisions."
                    ),
                ],
            },
            "covers": [
                {
                    "num": "01",
                    "title": "How unconscious<br />bias develops",
                    "desc": "The neuroscience of pattern-matching — and why it isn’t a moral failing.",
                },
                {
                    "num": "02",
                    "title": "Why our brains rely<br />on shortcuts",
                    "desc": "The cognitive load equation and how shortcuts became survival tools.",
                },
                {
                    "num": "03",
                    "title": "What shapes our<br />assumptions",
                    "desc": "Upbringing, culture, media, and the invisible curriculum we all absorb.",
                },
                {
                    "num": "04",
                    "title": "How bias influences<br />decisions at work",
                    "desc": "From hiring and promotions to the meetings you don’t get invited to.",
                },
                {
                    "num": "05",
                    "title": "Practical ways to reduce bias",
                    "desc": "Everyday habits, team rituals, and structural fixes that actually stick.",
                },
                {
                    "num": "06",
                    "title": "Bias and emerging<br />technologies",
                    "desc": "What happens when biased data trains models we then trust to be neutral.",
                },
                {
                    "num": "07",
                    "title": "Why self-awareness is hard",
                    "desc": "The paradox at the heart of introspection — and how to work around it.",
                },
            ],
            "highlights": [
                {
                    "num": "01",
                    "text": "Evidence-based insights from psychology and behavioural science",
                },
                {
                    "num": "02",
                    "text": "Practical workplace applications and real-world examples",
                },
                {
                    "num": "03",
                    "text": "Self-reflection exercises to help identify personal biases",
                },
                {
                    "num": "04",
                    "text": "Actionable strategies for individuals and organisations",
                },
                {
                    "num": "05",
                    "text": "Balanced approach focused on empathy & behavioural change",
                },
            ],
            "audience": [
                "Business Leaders",
                "HR Professionals",
                "Curious readers",
                "Recruiters & Talent",
                "DEI Practitioners",
                "Managers & Team Leads",
                "Educators & Students",
                "Org Development Pros",
            ],
            "cta_banner": {
                "title": "The Hidden Lens",
                "description": (
                    "Pick up your copy of The Hidden Lens — in hardcover or as an eBook "
                    "and start noticing what you’ve been trained to overlook."
                ),
                "cta_label": "Purchase for",
                "image_url": "/static/images/remaster-homepage/magazine-books/book-founder-issue.png",
            },
        },
        "more_books": [
            {
                "url": "/magazine/the-comeback-issue",
                "cover_variant": "cover-gradient-1",
                "brand": "BOL",
                "tag": "SUMMER 2026 · 11",
                "cover_title_lines": ["The", "Comeback", "Issue"],
                "background_number": "11",
                "category": "LEADERSHIP",
                "pages_label": "224 PAGES",
                "title": "The Comeback Issue",
                "author_name": "Aditya Raghavan",
                "price": {"current": "₹549"},
            },
            {
                "url": "/magazine/the-second-career",
                "cover_variant": "cover-gradient-2",
                "brand": "BOL",
                "tag": "SPRING 2026 · 10",
                "cover_title_lines": ["The", "Second", "Career"],
                "background_number": "10",
                "category": "LEADERSHIP",
                "pages_label": "224 PAGES",
                "title": "The Second Career",
                "author_name": "Aditya Raghavan",
                "price": {"current": "₹549"},
            },
            {
                "url": "/magazine/money-meaning",
                "cover_variant": "cover-gradient-3",
                "brand": "BOL",
                "tag": "WINTER 2025 · 09",
                "cover_title_lines": ["Money", "&", "Meaning"],
                "background_number": "09",
                "category": "LEADERSHIP",
                "pages_label": "224 PAGES",
                "title": "Money & Meaning",
                "author_name": "Aditya Raghavan",
                "price": {"current": "₹549"},
            },
            {
                "url": "/magazine/boards-not-bosses",
                "cover_variant": "cover-gradient-4",
                "brand": "BOL",
                "tag": "AUTUMN 2025 · 08",
                "cover_title_lines": ["Boards.", "Not", "Bosses."],
                "background_number": "08",
                "category": "LEADERSHIP",
                "pages_label": "224 PAGES",
                "title": "The Quiet Founder",
                "author_name": "Aditya Raghavan",
                "price": {"current": "₹549"},
            },
        ],
        "default_sections": {
            "about_title": "About the book",
            "covers_title": 'What the book <span class="highlight-blue">covers</span>',
            "covers_subtitle": (
                "Rather than looking at unconscious bias from a single perspective, "
                "the book examines it from many angles. It explores:"
            ),
            "highlights_title": 'Book <span class="highlight-blue">highlights</span>',
            "audience_title": "Who should read this book",
            "audience_subtitle": "The book is ideal for",
            "more_books_title": 'More from <span class="highlight-blue">BOL</span>',
            "browse_all": {
                "label": "Browse all books →",
                "href": "/magazine",
            },
            "purchase_label": "Purchase Now",
            "sample_label": "Read a Sample",
        },
    }
