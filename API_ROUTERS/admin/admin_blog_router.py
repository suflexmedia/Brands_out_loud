from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from database_handler import db_handler
from bucket_handler.minio_client import bucket_handler
import time
import os
import uuid
import io
import mimetypes

router = APIRouter(prefix="/admin/api", tags=["admin_api"])

# Session cookie name (must match admin_router.py)
COOKIE_NAME = "admin_session"

async def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid admin session cookie in the DB."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
        
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None

# ---------------------------------------------------------
# Blog Management Endpoints
# ---------------------------------------------------------

@router.get("/blogs")
async def api_list_blogs(request: Request):
    """Get all blogs."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db = db_handler.get_db()
    blogs = await db["blogs"].find({}).sort("created_at", -1).to_list(length=None)
    
    # Remove _id for JSON serialization
    for blog in blogs:
        if "_id" in blog:
            blog["_id"] = str(blog["_id"])
            
    return blogs

@router.post("/blogs")
async def api_create_blog(request: Request):
    """Create a new blog."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    db = db_handler.get_db()
    data = await request.json()
    
    slug = data.get("slug")
    if not slug:
        raise HTTPException(status_code=400, detail="Slug is required")
        
    existing = await db["blogs"].find_one({"slug": slug})
    if existing:
        raise HTTPException(status_code=400, detail="Blog with this slug already exists")
        
    data["created_at"] = time.time()
    await db["blogs"].insert_one(data)
    
    return {"status": "ok", "message": "Blog created successfully"}

@router.put("/blogs/{slug}")
async def api_update_blog(request: Request, slug: str):
    """Update an existing blog."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    db = db_handler.get_db()
    data = await request.json()
    
    # Remove _id if it's in the data to avoid update conflicts
    data.pop("_id", None)
    
    result = await db["blogs"].update_one(
        {"slug": slug},
        {"$set": data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
        
    return {"status": "ok", "message": "Blog updated successfully"}

@router.delete("/blogs/{slug}")
async def api_delete_blog(request: Request, slug: str, redirect_url: str = None):
    """Delete a blog and optionally add a redirect URL."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    db = db_handler.get_db()
    result = await db["blogs"].delete_one({"slug": slug})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
        
    # If a redirect URL is provided, save it
    if redirect_url:
        old_path = f"/blog/{slug}"
        # Store in redirects collection
        await db["redirects"].update_one(
            {"old_path": old_path},
            {"$set": {
                "old_path": old_path,
                "new_path": redirect_url,
                "created_at": time.time(),
                "type": "deleted_blog"
            }},
            upsert=True
        )
        
    return {"status": "ok", "message": "Blog deleted successfully"}

# ---------------------------------------------------------
# MinIO Gallery Endpoints
# ---------------------------------------------------------

@router.get("/gallery")
async def api_list_gallery(request: Request):
    """List images in MinIO gallery bucket."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        client = bucket_handler.get_client()
        bucket_name = bucket_handler.bucket_name
        
        objects = client.list_objects(bucket_name, prefix="gallery/", recursive=True)
        
        images = []
        for obj in objects:
            endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
            url = f"{endpoint}/{bucket_name}/{obj.object_name}"
            
            images.append({
                "object_name": obj.object_name,
                "size": obj.size,
                "url": url,
                "last_modified": str(obj.last_modified)
            })
            
        return sorted(images, key=lambda x: x["last_modified"], reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gallery/upload")
async def api_upload_gallery(request: Request, file: UploadFile = File(...)):
    """Upload an image to MinIO gallery."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        client = bucket_handler.get_client()
        bucket_name = bucket_handler.bucket_name
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"gallery/{uuid.uuid4()}{file_extension}"
        
        content = await file.read()
        file_size = len(content)
        
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        client.put_object(
            bucket_name,
            unique_filename,
            io.BytesIO(content),
            file_size,
            content_type=content_type
        )
        
        endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
        url = f"{endpoint}/{bucket_name}/{unique_filename}"
        
        return {
            "status": "ok", 
            "message": "File uploaded successfully",
            "url": url,
            "object_name": unique_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/gallery/{object_name:path}")
async def api_delete_gallery(request: Request, object_name: str):
    """Delete an image from MinIO gallery."""
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        if not object_name.startswith("gallery/"):
            raise HTTPException(status_code=400, detail="Only files in the gallery folder can be deleted")
            
        client = bucket_handler.get_client()
        bucket_name = bucket_handler.bucket_name
        
        client.remove_object(bucket_name, object_name)
        
        return {"status": "ok", "message": "File deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
