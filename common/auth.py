"""Single source of truth for admin session authentication."""

from typing import Optional

from fastapi import HTTPException, Request

from database_handler import db_handler

COOKIE_NAME = "admin_session"


async def is_authenticated(request: Request) -> bool:
    """Returns True when the request carries a valid admin session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


async def get_current_admin(request: Request) -> Optional[dict]:
    """Returns the admin user document for the request's session, or None."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    if not session:
        return None
    return await db["admin_users"].find_one({"username": session["username"]})


async def require_admin(request: Request) -> dict:
    """FastAPI dependency that rejects unauthenticated API callers with 401."""
    admin = await get_current_admin(request)
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return admin


async def require_system_admin(request: Request) -> dict:
    """FastAPI dependency that restricts an API route to system_admin users."""
    admin = await require_admin(request)
    if admin.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return admin
