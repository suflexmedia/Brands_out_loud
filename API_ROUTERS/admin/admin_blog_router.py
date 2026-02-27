from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from database_handler import db_handler
from bucket_handler.minio_client import bucket_handler
from cache_manager import cache_manager
import time
import os
import uuid
import io
import mimetypes

router = APIRouter(prefix="/admin/api", tags=["admin_api"])

COOKIE_NAME = "admin_session"

CATEGORY_HEADINGS = {
    "business": "Latest Business Stories",
    "technology": "Tech Innovations",
    "gcc": "GCC Regional News",
    "sustainability": "Green Initiatives",
    "semiconductor": "Chip Industry Updates",
}

MAX_NAVBAR_POSTS = 3


async def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid admin session cookie in the DB."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
        
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


async def update_navbar_collection():
    """Rebuild the navbar collection from the latest published blogs per category.

    For each category, fetches the most recent MAX_NAVBAR_POSTS published blogs
    and writes the result as a single document into the 'navbar' collection.
    """
    db = db_handler.get_db()

    navbar_data = {}

    for category_key, heading in CATEGORY_HEADINGS.items():
        category_filter = {
            "status": "published",
            "blogContent.blogCategory": {"$regex": f"^{category_key}$", "$options": "i"},
        }

        cursor = db["blogs"].find(category_filter).sort("created_at", -1).limit(MAX_NAVBAR_POSTS)
        blogs = await cursor.to_list(length=MAX_NAVBAR_POSTS)

        posts = []
        for blog in blogs:
            blog_content = blog.get("blogContent", {})
            posts.append({
                "title": blog_content.get("blogTitle", "Untitled"),
                "image_url": blog_content.get("mainImageUrl", ""),
                "slug": blog.get("slug", ""),
            })

        navbar_data[category_key] = {
            "heading": heading,
            "posts": posts,
        }

    existing = await db["navbar"].find_one({})
    if existing:
        await db["navbar"].update_one(
            {"_id": existing["_id"]},
            {"$set": navbar_data},
        )
    else:
        await db["navbar"].insert_one(navbar_data)

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

    await update_navbar_collection()
    cache_manager.invalidate("blogs")
    cache_manager.invalidate("navbar")
    cache_manager.invalidate("homepage")
    cache_manager.invalidate_pattern("related_blogs_")

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

    await update_navbar_collection()
    cache_manager.invalidate("blogs")
    cache_manager.invalidate("navbar")
    cache_manager.invalidate("homepage")
    cache_manager.invalidate_pattern("related_blogs_")

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

    await update_navbar_collection()
    cache_manager.invalidate("blogs")
    cache_manager.invalidate("navbar")
    cache_manager.invalidate("homepage")
    cache_manager.invalidate_pattern("related_blogs_")

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

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif", ".tiff"}

@router.get("/gallery")
async def api_list_gallery(request: Request, media_type: str = "all"):
    """List files in MinIO gallery bucket.

    Args:
        media_type: Filter by type - 'images' for images only, 'all' for everything.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        client = bucket_handler.get_client()
        bucket_name = bucket_handler.bucket_name
        
        objects = client.list_objects(bucket_name, prefix="gallery/", recursive=True)
        
        images = []
        for obj in objects:
            if media_type == "images":
                ext = os.path.splitext(obj.object_name)[1].lower()
                if ext not in IMAGE_EXTENSIONS:
                    continue

            endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
            url = f"{endpoint}/{bucket_name}/{obj.object_name}"
            
            raw_name = obj.object_name.replace("gallery/", "", 1)
            parts = raw_name.split("_", 1)
            if len(parts) == 2 and len(parts[0]) == 36:
                display_name = parts[1]
            else:
                display_name = raw_name
            
            images.append({
                "object_name": obj.object_name,
                "display_name": display_name,
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
        
        safe_original = file.filename.replace("/", "_").replace("\\", "_")
        unique_filename = f"gallery/{uuid.uuid4()}_{safe_original}"
        
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
