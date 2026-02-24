import os
import uuid
import bcrypt
import time
from typing import Optional

from pydantic import BaseModel
from bson.objectid import ObjectId

from fastapi import APIRouter, Request, Response, Form, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse

from database_handler import db_handler
from bucket_handler.minio_client import bucket_handler

router = APIRouter(prefix="/admin", tags=["admin"])

# Session cookie name
COOKIE_NAME = "admin_session"

async def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid admin session cookie in the DB."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
        
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None

async def get_current_admin(request: Request) -> Optional[dict]:
    """Get the current admin user document from DB based on cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    if not session:
        return None
    user = await db["admin_users"].find_one({"username": session["username"]})
    return user

@router.get("/login")
async def login_page(request: Request):
    """Serve the admin login HTML page."""
    if await is_authenticated(request):
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/login.html")

@router.post("/login")
async def login_post(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle the login form submission."""
    db = db_handler.get_db()
    admin_user = await db["admin_users"].find_one({"username": username})
    
    if admin_user:
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), admin_user["password_hash"].encode('utf-8')):
            
            # Generate new session token and store in DB
            new_token = str(uuid.uuid4())
            await db["admin_sessions"].insert_one({
                "token": new_token,
                "username": username
            })
            
            redirect = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
            # Keep them logged in for 7 days
            redirect.set_cookie(
                key=COOKIE_NAME,
                value=new_token,
                max_age=60 * 60 * 24 * 7,
                httponly=True,
                samesite="lax",
            )
            return redirect
    
    # Invalid credentials, redirect back to login
    return RedirectResponse(url="/admin/login?error=Invalid+credentials", status_code=status.HTTP_302_FOUND)

@router.get("/dashboard")
async def dashboard_page(request: Request):
    """Serve the admin dashboard HTML page."""
    if not await is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/dashboard.html")

@router.get("/user-management")
async def user_management_page(request: Request):
    """Serve the admin user management HTML page."""
    current_admin = await get_current_admin(request)
    if not current_admin or current_admin.get("role") != "system_admin":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/user_management.html")

@router.get("/blogs")
async def admin_blogs_page(request: Request):
    """Serve the admin blog management HTML page."""
    if not await is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/blog_management.html")


@router.get("/magazines")
async def admin_magazines_page(request: Request):
    """Serve the admin magazine management HTML page."""
    if not await is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/magazine_management.html")


@router.get("/analytics")
async def admin_analytics_page(request: Request):
    """Serve the admin analytics HTML page."""
    if not await is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    return FileResponse("PAGE_SERVING_ROUTERS/static/templates/admin/analytics.html")


@router.get("/logout")
async def logout(request: Request):
    """Clear the session cookie from DB and log the user out."""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        db = db_handler.get_db()
        await db["admin_sessions"].delete_one({"token": token})
        
    redirect = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(key=COOKIE_NAME)
    return redirect

class UserCreate(BaseModel):
    username: str
    password: str
    permissions: list[str]
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[list[str]] = None

class ProfileUpdate(BaseModel):
    password: Optional[str] = None

@router.get("/me")
async def get_me(request: Request):
    """Get current user info (role and permissions)."""
    user = await get_current_admin(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "username": user.get("username"),
        "role": user.get("role", "user"),
        "permissions": user.get("permissions", [])
    }

@router.get("/users")
async def list_users(request: Request):
    """List all users (system_admin only)."""
    current_admin = await get_current_admin(request)
    if not current_admin or current_admin.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    db = db_handler.get_db()
    users = await db["admin_users"].find({}, {"password_hash": 0}).to_list(length=100)
    for u in users:
        u["_id"] = str(u["_id"])
    return users

@router.post("/users")
async def create_user(request: Request, user_data: UserCreate):
    """Create a new user (system_admin only)."""
    current_admin = await get_current_admin(request)
    if not current_admin or current_admin.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    db = db_handler.get_db()
    existing = await db["admin_users"].find_one({"username": user_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
        
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')
    
    new_user = {
        "username": user_data.username,
        "password_hash": hashed_password,
        "role": user_data.role,
        "permissions": user_data.permissions,
        "created_at": time.time()
    }
    
    await db["admin_users"].insert_one(new_user)
    return {"status": "ok", "message": "User created successfully"}

@router.put("/users/{user_id}")
async def update_user(request: Request, user_id: str, update_data: UserUpdate):
    """Update a user (system_admin only)."""
    current_admin = await get_current_admin(request)
    if not current_admin or current_admin.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    db = db_handler.get_db()
    
    update_fields = {}
    if update_data.username is not None:
        # Check if new username exists for a different user
        existing = await db["admin_users"].find_one({"username": update_data.username})
        if existing and str(existing["_id"]) != user_id:
            raise HTTPException(status_code=400, detail="Username already exists")
        update_fields["username"] = update_data.username
        
    if update_data.password is not None and update_data.password.strip():
        salt = bcrypt.gensalt()
        update_fields["password_hash"] = bcrypt.hashpw(update_data.password.encode('utf-8'), salt).decode('utf-8')
    if update_data.role is not None:
        if update_data.role != "system_admin":
            user_to_update = await db["admin_users"].find_one({"_id": ObjectId(user_id)})
            if user_to_update and user_to_update.get("role") == "system_admin":
                admin_count = await db["admin_users"].count_documents({"role": "system_admin"})
                if admin_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot demote the only system admin")
        update_fields["role"] = update_data.role
    if update_data.permissions is not None:
        update_fields["permissions"] = update_data.permissions
        
    if update_fields:
        try:
            result = await db["admin_users"].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
             raise HTTPException(status_code=400, detail="Invalid user ID or database error")
             
    return {"status": "ok", "message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: str):
    """Delete a user (system_admin only)."""
    current_admin = await get_current_admin(request)
    if not current_admin or current_admin.get("role") != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    db = db_handler.get_db()
    try:
        if str(current_admin["_id"]) == user_id:
             raise HTTPException(status_code=400, detail="Cannot delete your own account")
             
        # Optional: delete active sessions for the user to force logout
        user_to_delete = await db["admin_users"].find_one({"_id": ObjectId(user_id)})
        if user_to_delete:
             if user_to_delete.get("role") == "system_admin":
                 admin_count = await db["admin_users"].count_documents({"role": "system_admin"})
                 if admin_count <= 1:
                     raise HTTPException(status_code=400, detail="Cannot delete the only system admin")
             await db["admin_sessions"].delete_many({"username": user_to_delete["username"]})
             
        result = await db["admin_users"].delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
         if isinstance(e, HTTPException): raise e
         raise HTTPException(status_code=400, detail="Invalid user ID or database error")
         
    return {"status": "ok", "message": "User deleted successfully"}

@router.put("/profile")
async def update_profile(request: Request, profile_data: ProfileUpdate):
    """Update current user's profile info (e.g. password)."""
    current_user = await get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    update_fields = {}
    if profile_data.password:
        salt = bcrypt.gensalt()
        update_fields["password_hash"] = bcrypt.hashpw(profile_data.password.encode('utf-8'), salt).decode('utf-8')
        
    if update_fields:
        db = db_handler.get_db()
        await db["admin_users"].update_one(
            {"username": current_user["username"]},
            {"$set": update_fields}
        )
        
    return {"status": "ok", "message": "Profile updated successfully"}
