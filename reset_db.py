"""
Run this script to wipe and re-seed all page-content collections from JSON_FILES.

Collections that are reset:
  site_settings, blog_categories, page_content

Collections that are intentionally left untouched:
  admin_users, admin_sessions, blogs, magazine_issues, books,
  page_views, pdf_download_leads, contact_leads

Usage:
    py reset_db.py
"""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

DB_NAME = "brands-out-loud"
BASE_DIR = Path(__file__).parent
JSON_DIR = BASE_DIR / "JSON_FILES"

SINGLETON_COLLECTIONS = {
    "site_settings": "site_settings.json",
    "blog_categories": "blog_categories.json",
}

PAGE_IDS = [
    "homepage",
    "blog_listing",
    "blog_post",
    "magazine_listing",
    "magazine_issue",
    "book_detail",
    "contact",
]


async def reset():
    """Drops and re-seeds every page-content collection from the JSON seeds."""
    mongo_url = os.getenv("mongo_public_url")
    if not mongo_url:
        raise ValueError("mongo_public_url is not set in .env")

    client = AsyncIOMotorClient(mongo_url)
    db = client[DB_NAME]

    print(f"Connected to MongoDB - database: '{DB_NAME}'\n")

    for col_name, file_name in SINGLETON_COLLECTIONS.items():
        json_file = JSON_DIR / file_name
        if not json_file.exists():
            print(f"  [SKIP] {col_name} - JSON file not found: {file_name}")
            continue
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        await db[col_name].drop()
        await db[col_name].insert_one(data)
        print(f"  [OK]   {col_name} - dropped and re-seeded from {file_name}")

    await db["page_content"].drop()
    for page_id in PAGE_IDS:
        json_file = JSON_DIR / f"page_{page_id}.json"
        if not json_file.exists():
            print(f"  [SKIP] page_content/{page_id} - seed file not found")
            continue
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["_id"] = page_id
        await db["page_content"].insert_one(data)
        print(f"  [OK]   page_content/{page_id} - re-seeded")

    print("\nDone. All page collections have been reset.")
    client.close()


if __name__ == "__main__":
    asyncio.run(reset())
