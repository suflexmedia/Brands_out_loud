from fastapi import APIRouter, Request, HTTPException, Query
from database_handler import db_handler
from cache_manager import cache_manager
from datetime import datetime, timezone, timedelta
import os

router = APIRouter(prefix="/admin/api/analytics", tags=["admin_analytics_api"])

COOKIE_NAME = "admin_session"


async def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid admin session cookie in the DB."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    db = db_handler.get_db()
    session = await db["admin_sessions"].find_one({"token": token})
    return session is not None


def _get_time_range(period: str) -> datetime:
    """Return a UTC datetime representing the start of the given period."""
    now = datetime.now(timezone.utc)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        return now - timedelta(days=7)
    elif period == "month":
        return now - timedelta(days=30)
    elif period == "year":
        return now - timedelta(days=365)
    return datetime(2000, 1, 1, tzinfo=timezone.utc)


@router.get("/overview")
async def analytics_overview(request: Request):
    """
    Returns the main overview metrics for the analytics dashboard:
    total blogs, magazines, PDF leads, admin users, active sessions,
    and page view summaries for today/week/month.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()

    total_blogs = await db["blogs"].count_documents({})
    total_magazines = await db["magazines"].count_documents({"status": "published"})
    total_pdf_leads = await db["pdf_download_leads"].count_documents({})
    total_admin_users = await db["admin_users"].count_documents({})
    active_sessions = await db["admin_sessions"].count_documents({})

    now = datetime.now(timezone.utc)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = now - timedelta(days=7)
    start_month = now - timedelta(days=30)

    views_today = await db["page_views"].count_documents({"timestamp": {"$gte": start_today}})
    views_week = await db["page_views"].count_documents({"timestamp": {"$gte": start_week}})
    views_month = await db["page_views"].count_documents({"timestamp": {"$gte": start_month}})
    views_total = await db["page_views"].count_documents({})

    unique_today_pipeline = [
        {"$match": {"timestamp": {"$gte": start_today}}},
        {"$group": {"_id": "$ip_hash"}},
        {"$count": "count"}
    ]
    unique_today_result = await db["page_views"].aggregate(unique_today_pipeline).to_list(1)
    unique_today = unique_today_result[0]["count"] if unique_today_result else 0

    unique_week_pipeline = [
        {"$match": {"timestamp": {"$gte": start_week}}},
        {"$group": {"_id": "$ip_hash"}},
        {"$count": "count"}
    ]
    unique_week_result = await db["page_views"].aggregate(unique_week_pipeline).to_list(1)
    unique_week = unique_week_result[0]["count"] if unique_week_result else 0

    unique_month_pipeline = [
        {"$match": {"timestamp": {"$gte": start_month}}},
        {"$group": {"_id": "$ip_hash"}},
        {"$count": "count"}
    ]
    unique_month_result = await db["page_views"].aggregate(unique_month_pipeline).to_list(1)
    unique_month = unique_month_result[0]["count"] if unique_month_result else 0

    realtime_pipeline = [
        {"$match": {"timestamp": {"$gte": now - timedelta(minutes=5)}}},
        {"$group": {"_id": "$ip_hash"}},
        {"$count": "count"}
    ]
    realtime_result = await db["page_views"].aggregate(realtime_pipeline).to_list(1)
    realtime_visitors = realtime_result[0]["count"] if realtime_result else 0

    return {
        "content": {
            "total_blogs": total_blogs,
            "total_magazines": total_magazines,
            "total_pdf_leads": total_pdf_leads,
            "total_admin_users": total_admin_users,
            "active_sessions": active_sessions,
        },
        "traffic": {
            "views_today": views_today,
            "views_week": views_week,
            "views_month": views_month,
            "views_total": views_total,
            "unique_today": unique_today,
            "unique_week": unique_week,
            "unique_month": unique_month,
            "realtime_visitors": realtime_visitors,
        },
    }


@router.get("/top-pages")
async def analytics_top_pages(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Returns the most visited pages for the given time period.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {}
    if period != "all":
        match_stage = {"timestamp": {"$gte": _get_time_range(period)}}

    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$path",
            "views": {"$sum": 1},
            "unique_visitors": {"$addToSet": "$ip_hash"},
            "avg_response_time": {"$avg": "$process_time"},
        }},
        {"$project": {
            "path": "$_id",
            "views": 1,
            "unique_visitors": {"$size": "$unique_visitors"},
            "avg_response_time": {"$round": ["$avg_response_time", 4]},
            "_id": 0,
        }},
        {"$sort": {"views": -1}},
        {"$limit": limit},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(limit)
    return {"period": period, "pages": results}


@router.get("/traffic-over-time")
async def analytics_traffic_over_time(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year)$"),
):
    """
    Returns page views grouped by time interval for chart display.
    - today: grouped by hour
    - week/month: grouped by day
    - year: grouped by month
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    start = _get_time_range(period)

    if period == "today":
        group_format = "%H:00"
        date_expr = {"$dateToString": {"format": "%Y-%m-%d %H:00", "date": "$timestamp"}}
        label_expr = {"$dateToString": {"format": "%H:00", "date": "$timestamp"}}
    elif period in ("week", "month"):
        group_format = "%Y-%m-%d"
        date_expr = {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
        label_expr = {"$dateToString": {"format": "%b %d", "date": "$timestamp"}}
    else:
        group_format = "%Y-%m"
        date_expr = {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}}
        label_expr = {"$dateToString": {"format": "%b %Y", "date": "$timestamp"}}

    pipeline = [
        {"$match": {"timestamp": {"$gte": start}}},
        {"$group": {
            "_id": date_expr,
            "label": {"$first": label_expr},
            "views": {"$sum": 1},
            "unique_visitors": {"$addToSet": "$ip_hash"},
        }},
        {"$project": {
            "date": "$_id",
            "label": 1,
            "views": 1,
            "unique_visitors": {"$size": "$unique_visitors"},
            "_id": 0,
        }},
        {"$sort": {"date": 1}},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(366)
    return {"period": period, "data": results}


@router.get("/device-breakdown")
async def analytics_device_breakdown(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
):
    """
    Returns page view count grouped by device type (mobile, desktop, tablet, bot).
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {}
    if period != "all":
        match_stage = {"timestamp": {"$gte": _get_time_range(period)}}

    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$device_type",
            "count": {"$sum": 1},
        }},
        {"$project": {
            "device": "$_id",
            "count": 1,
            "_id": 0,
        }},
        {"$sort": {"count": -1}},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(10)
    return {"period": period, "devices": results}


@router.get("/top-referrers")
async def analytics_top_referrers(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Returns top referrer domains sorted by count.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {"referer": {"$ne": ""}}
    if period != "all":
        match_stage["timestamp"] = {"$gte": _get_time_range(period)}

    pipeline = [
        {"$match": match_stage},
        {"$addFields": {
            "referer_parts": {"$split": [{"$arrayElemAt": [{"$split": ["$referer", "://"]}, 1]}, "/"]},
        }},
        {"$addFields": {
            "referer_domain": {"$arrayElemAt": ["$referer_parts", 0]},
        }},
        {"$group": {
            "_id": "$referer_domain",
            "count": {"$sum": 1},
        }},
        {"$project": {
            "domain": "$_id",
            "count": 1,
            "_id": 0,
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(limit)
    return {"period": period, "referrers": results}


@router.get("/blog-categories")
async def analytics_blog_categories(request: Request):
    """
    Returns blog count grouped by category.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()

    pipeline = [
        {"$project": {
            "category": {
                "$ifNull": ["$blogContent.blogCategory", "$blogCategory"]
            }
        }},
        {"$group": {
            "_id": {"$ifNull": ["$category", "Uncategorized"]},
            "count": {"$sum": 1},
        }},
        {"$project": {
            "category": "$_id",
            "count": 1,
            "_id": 0,
        }},
        {"$sort": {"count": -1}},
    ]

    results = await db["blogs"].aggregate(pipeline).to_list(50)
    return {"categories": results}


@router.get("/recent-activity")
async def analytics_recent_activity(
    request: Request,
    limit: int = Query(10, ge=1, le=30),
):
    """
    Returns the most recently created blogs and magazines combined
    into a unified activity feed.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()

    recent_blogs = await db["blogs"].find(
        {},
        {"slug": 1, "blogContent.blogTitle": 1, "blogCategory": 1, "created_at": 1, "_id": 0}
    ).sort("created_at", -1).to_list(limit)

    recent_magazines = await db["magazines"].find(
        {},
        {"slug": 1, "title": 1, "status": 1, "created_at": 1, "_id": 0}
    ).sort("created_at", -1).to_list(limit)

    def _to_float_ts(val):
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        if hasattr(val, "timestamp"):
            return val.timestamp()
        if isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                return dt.timestamp()
            except (ValueError, TypeError):
                pass
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    activities = []
    for blog in recent_blogs:
        blog_content = blog.get("blogContent", {})
        title = blog_content.get("blogTitle", blog.get("slug", "Untitled"))
        activities.append({
            "type": "blog",
            "title": title,
            "slug": blog.get("slug", ""),
            "created_at": _to_float_ts(blog.get("created_at")),
        })

    for mag in recent_magazines:
        activities.append({
            "type": "magazine",
            "title": mag.get("title", "Untitled"),
            "slug": mag.get("slug", ""),
            "status": mag.get("status", ""),
            "created_at": _to_float_ts(mag.get("created_at")),
        })

    activities.sort(key=lambda x: x.get("created_at", 0), reverse=True)

    return {"activities": activities[:limit]}


@router.get("/top-blogs")
async def analytics_top_blogs(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Returns the most viewed blog posts based on page_views data.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {"path": {"$regex": "^/blog/"}}
    if period != "all":
        match_stage["timestamp"] = {"$gte": _get_time_range(period)}

    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": "$path",
            "views": {"$sum": 1},
            "unique_visitors": {"$addToSet": "$ip_hash"},
        }},
        {"$project": {
            "path": "$_id",
            "views": 1,
            "unique_visitors": {"$size": "$unique_visitors"},
            "_id": 0,
        }},
        {"$sort": {"views": -1}},
        {"$limit": limit},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(limit)

    for item in results:
        slug = item["path"].replace("/blog/", "", 1).rstrip("/")
        blog = await db["blogs"].find_one(
            {"slug": slug},
            {"blogContent.blogTitle": 1, "_id": 0}
        )
        if blog:
            item["title"] = blog.get("blogContent", {}).get("blogTitle", slug)
        else:
            item["title"] = slug

    return {"period": period, "blogs": results}


@router.get("/pdf-leads")
async def analytics_pdf_leads(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    """
    Returns paginated PDF download leads with full details
    and a source column (blog/magazine) derived from pdf_link.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()

    total = await db["pdf_download_leads"].count_documents({})
    skip = (page - 1) * per_page

    leads = await db["pdf_download_leads"].find(
        {},
        {"_id": 0}
    ).sort("_id", -1).skip(skip).limit(per_page).to_list(per_page)

    magazine_cache = {}
    for lead in leads:
        pdf_link = lead.get("pdf_link") or ""
        pdf_link_lower = pdf_link.lower()

        if "magazine" in pdf_link_lower:
            lead["source"] = "magazine"
        else:
            lead["source"] = "blog"

        doc_name = ""
        if pdf_link:
            if pdf_link not in magazine_cache:
                mag = await db["magazines"].find_one(
                    {"pdf_url": pdf_link},
                    {"title": 1, "_id": 0}
                )
                magazine_cache[pdf_link] = mag.get("title") if mag else None

            if magazine_cache[pdf_link]:
                doc_name = magazine_cache[pdf_link]
            else:
                filename = pdf_link.rstrip("/").split("/")[-1]
                if "." in filename:
                    doc_name = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title()
                else:
                    doc_name = filename

        lead["document_name"] = doc_name

    by_pdf_pipeline = [
        {"$group": {
            "_id": "$pdf_link",
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {
            "pdf_link": "$_id",
            "count": 1,
            "_id": 0,
        }},
    ]
    by_pdf = await db["pdf_download_leads"].aggregate(by_pdf_pipeline).to_list(10)

    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        "total": total,
        "leads": leads,
        "by_pdf": by_pdf,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get("/registered-users")
async def analytics_registered_users(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    """
    Returns paginated list of registered users (from the public users collection).
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()

    total = await db["users"].count_documents({})
    skip = (page - 1) * per_page

    users = await db["users"].find(
        {},
        {"password": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)

    for u in users:
        if "_id" in u:
            u["_id"] = str(u["_id"])
        if "created_at" in u and hasattr(u["created_at"], "isoformat"):
            u["created_at"] = u["created_at"].isoformat()

    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        "total": total,
        "users": users,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get("/peak-hours")
async def analytics_peak_hours(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
):
    """
    Returns page view count grouped by hour of day (0-23) for heatmap display.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {}
    if period != "all":
        match_stage = {"timestamp": {"$gte": _get_time_range(period)}}

    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": {"$hour": "$timestamp"},
            "count": {"$sum": 1},
        }},
        {"$project": {
            "hour": "$_id",
            "count": 1,
            "_id": 0,
        }},
        {"$sort": {"hour": 1}},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(24)

    hours_map = {r["hour"]: r["count"] for r in results}
    full_hours = [{"hour": h, "count": hours_map.get(h, 0)} for h in range(24)]

    return {"period": period, "hours": full_hours}


@router.get("/response-times")
async def analytics_response_times(
    request: Request,
    period: str = Query("month", regex="^(today|week|month|year|all)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Returns the slowest pages by average response time.
    """
    if not await is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = db_handler.get_db()
    match_stage = {}
    if period != "all":
        match_stage = {"timestamp": {"$gte": _get_time_range(period)}}

    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$path",
            "avg_time": {"$avg": "$process_time"},
            "max_time": {"$max": "$process_time"},
            "min_time": {"$min": "$process_time"},
            "request_count": {"$sum": 1},
        }},
        {"$match": {"request_count": {"$gte": 3}}},
        {"$project": {
            "path": "$_id",
            "avg_time": {"$round": ["$avg_time", 4]},
            "max_time": {"$round": ["$max_time", 4]},
            "min_time": {"$round": ["$min_time", 4]},
            "request_count": 1,
            "_id": 0,
        }},
        {"$sort": {"avg_time": -1}},
        {"$limit": limit},
    ]

    results = await db["page_views"].aggregate(pipeline).to_list(limit)
    return {"period": period, "pages": results}
