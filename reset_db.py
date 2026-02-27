"""
Run this script to wipe and re-seed all page-content collections from JSON_FILES.

Collections that are reset:
  homepage, magazine_homepage, magazine_page, navbar,
  service_business, service_technology, service_gcc,
  service_sustainability, service_semiconductor

Collections that are intentionally left untouched:
  admin_users, blogs, page_views, pdf_download_leads

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

PAGE_COLLECTIONS = [
    "homepage",
    "magazine_homepage",
    "magazine_page",
    "navbar",
    "service_business",
    "service_technology",
    "service_gcc",
    "service_sustainability",
    "service_semiconductor",
]

JSON_MAP = {
    "homepage": "homepage.json",
    "magazine_homepage": "magazine_homepage.json",
    "magazine_page": "magazine_page.json",
    "navbar": "navbar.json",
    "service_business": "service_business.json",
    "service_technology": "service_technology.json",
    "service_gcc": "service_gcc.json",
    "service_sustainability": "service_sustainability.json",
    "service_semiconductor": "service_semiconductor.json",
}


async def reset():
    mongo_url = os.getenv("mongo_public_url")
    if not mongo_url:
        raise ValueError("mongo_public_url is not set in .env")

    client = AsyncIOMotorClient(mongo_url)
    db = client[DB_NAME]

    print(f"Connected to MongoDB — database: '{DB_NAME}'\n")

    for col_name in PAGE_COLLECTIONS:
        json_file = JSON_DIR / JSON_MAP[col_name]

        if not json_file.exists():
            print(f"  [SKIP] {col_name} — JSON file not found: {json_file.name}")
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        await db[col_name].drop()
        await db[col_name].insert_one(data)
        print(f"  [OK]   {col_name} — dropped and re-seeded from {json_file.name}")

    print("\nDone. All page collections have been reset.")
    client.close()


if __name__ == "__main__":
    asyncio.run(reset())
