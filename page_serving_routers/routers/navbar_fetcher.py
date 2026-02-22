import time
from database_handler.connection import db_handler

navbar_cache = {
    "data": None,
    "expires_at": 0
}
CACHE_TTL = 300


async def get_navbar_data():
    """
    Fetches the navbar dropdown data from the cache if valid,
    otherwise fetches from MongoDB and updates the cache.
    TTL is 5 minutes (300 seconds).
    """
    current_time = time.time()

    if navbar_cache["data"] and current_time < navbar_cache["expires_at"]:
        navbar_cache["expires_at"] = current_time + CACHE_TTL
        return navbar_cache["data"]

    db_start_time = time.time()
    db = db_handler.get_db()
    collection = db["navbar"]

    doc_count = await collection.count_documents({})
    if doc_count == 0:
        navbar_data = {}
    else:
        navbar_data = await collection.find_one({})

    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | Navbar Data | Time: {db_elapsed:.4f}s")

    navbar_cache["data"] = navbar_data
    navbar_cache["expires_at"] = current_time + CACHE_TTL

    return navbar_data
