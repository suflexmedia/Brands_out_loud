"""Migrates legacy collections into the remastered content structure.

Run with the project venv active:  py migrate_to_remaster.py
The script is idempotent and never deletes legacy data.
"""

import asyncio
import json
import os
import time

from dotenv import load_dotenv

from common.text_utils import slugify
from database_handler import db_handler

load_dotenv()

JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JSON_FILES")

SINGLETON_SEEDS = ["site_settings", "blog_categories"]
PAGE_SEEDS = [
    "homepage", "blog_listing", "blog_post",
    "magazine_listing", "magazine_issue", "book_detail", "contact",
]


def _read_seed(name):
    """Reads a seed file from JSON_FILES, returning None when it is absent."""
    path = os.path.join(JSON_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


async def seed_singletons(db):
    """Inserts the shared settings documents when they do not exist yet."""
    for name in SINGLETON_SEEDS:
        if await db[name].count_documents({}) > 0:
            print(f"  {name}: already present")
            continue
        seed = _read_seed(name)
        if seed is None:
            print(f"  {name}: seed file missing")
            continue
        await db[name].insert_one(seed)
        print(f"  {name}: seeded")


async def seed_pages(db):
    """Inserts each page_content document when it does not exist yet."""
    for page_id in PAGE_SEEDS:
        if await db["page_content"].count_documents({"_id": page_id}) > 0:
            print(f"  page_content/{page_id}: already present")
            continue
        seed = _read_seed(f"page_{page_id}")
        if seed is None:
            print(f"  page_content/{page_id}: seed file missing")
            continue
        seed["_id"] = page_id
        await db["page_content"].insert_one(seed)
        print(f"  page_content/{page_id}: seeded")


async def normalise_blogs(db):
    """Repairs blog documents so every consumer sees one consistent shape."""
    fixed = 0
    categories = set()
    async for blog in db["blogs"].find({}):
        updates = {}
        content = blog.get("blogContent")

        if isinstance(content, str):
            try:
                content = json.loads(content)
                updates["blogContent"] = content
            except (ValueError, TypeError):
                print(f"  ! {blog.get('slug')}: unparseable blogContent, skipped")
                continue

        if not isinstance(content, dict):
            continue

        category = (content.get("blogCategory") or "").strip()
        if category:
            categories.add(category.lower())
            if category != category.lower():
                updates["blogContent.blogCategory"] = category.lower()

        if not blog.get("slug"):
            updates["slug"] = slugify(content.get("blogTitle", "")) or f"post-{int(time.time())}"

        if blog.get("isDeleted") is None:
            updates["isDeleted"] = False

        if not blog.get("status"):
            updates["status"] = "published"

        if isinstance(blog.get("created_at"), str):
            updates["created_at"] = time.time()

        if updates:
            await db["blogs"].update_one({"_id": blog["_id"]}, {"$set": updates})
            fixed += 1

    print(f"  normalised {fixed} blog document(s)")
    return categories


async def merge_categories(db, found):
    """Adds any category already used by existing blogs to the managed list."""
    doc = await db["blog_categories"].find_one({"_id": "blog_categories"}) or {}
    categories = doc.get("categories", [])
    known = {c["slug"] for c in categories}
    order = max([c.get("order", 0) for c in categories] or [0])

    added = []
    for slug in sorted(found):
        if slug in known:
            continue
        order += 1
        categories.append({"slug": slug, "label": slug.replace("-", " ").title(), "order": order})
        added.append(slug)

    if added:
        await db["blog_categories"].update_one(
            {"_id": "blog_categories"}, {"$set": {"categories": categories}}, upsert=True
        )
        print(f"  added legacy categories: {', '.join(added)}")
    else:
        print("  no new categories to add")


async def migrate_magazines(db):
    """Converts each legacy magazine document into a magazine issue."""
    migrated = 0
    skipped = 0
    async for magazine in db["magazines"].find({}):
        slug = magazine.get("slug") or slugify(magazine.get("title", ""))
        if not slug:
            skipped += 1
            continue
        if await db["magazine_issues"].find_one({"slug": slug}):
            skipped += 1
            continue

        title = magazine.get("title", "")
        await db["magazine_issues"].insert_one({
            "slug": slug,
            "title": title,
            "issue_number": magazine.get("issue_number", ""),
            "season_label": magazine.get("date", ""),
            "badge": "",
            "description": magazine.get("description", ""),
            "cover_image_url": magazine.get("image_url", ""),
            "cover_variant": "edition-bg-1",
            "cover_title_lines": [line for line in title.split(" ") if line][:2],
            "brand": "BOL",
            "stats": [],
            "meta_tags": [],
            "pdf_url": magazine.get("pdf_url", ""),
            "status": magazine.get("status", "published"),
            "order": 0,
            "created_at": magazine.get("created_at", time.time()),
            "migrated_from": "magazines",
        })
        migrated += 1

    print(f"  migrated {migrated} magazine(s) into magazine_issues, skipped {skipped}")


async def main():
    """Runs every migration step in order."""
    db_handler.connect()
    db = db_handler.get_db()

    print("Seeding shared settings...")
    await seed_singletons(db)

    print("Seeding page content...")
    await seed_pages(db)

    print("Normalising blogs...")
    found = await normalise_blogs(db)

    print("Merging blog categories...")
    await merge_categories(db, found)

    print("Migrating magazines...")
    await migrate_magazines(db)

    db_handler.disconnect()
    print("Migration complete.")


if __name__ == "__main__":
    asyncio.run(main())
