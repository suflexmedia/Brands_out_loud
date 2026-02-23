"""Fetches and caches navbar dropdown data from MongoDB."""

from database_handler.connection import db_handler
from cache_manager import cache_manager


async def _fetch_navbar_from_db():
    """Fetch navbar data directly from MongoDB."""
    db = db_handler.get_db()
    collection = db["navbar"]

    doc_count = await collection.count_documents({})
    if doc_count == 0:
        return {}
    return await collection.find_one({})


async def get_navbar_data():
    """
    Returns navbar data using the centralized cache manager.
    Fixed 5-minute absolute expiry with stale-while-revalidate.
    """
    return await cache_manager.get("navbar", _fetch_navbar_from_db)
