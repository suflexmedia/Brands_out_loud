"""Serves the contact page targeted by the site-wide call-to-action buttons."""

import os
import time
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database_handler import db_handler
from page_serving_routers.routers.site_context import base_context

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))


class ContactSubmission(BaseModel):
    """Data model for a contact form submission."""

    first_name: str
    last_name: Optional[str] = None
    email: str
    company_name: Optional[str] = None
    mobile_number: Optional[str] = None
    message: Optional[str] = None


@router.get("/contact", tags=["Pages"])
async def serve_contact(request: Request):
    """Serves the contact page."""
    context = await base_context(active_nav="contact", page_id="contact")
    return templates.TemplateResponse(request, "contact.html", context)


@router.post("/api/contact", tags=["Public API"])
async def submit_contact(submission: ContactSubmission):
    """Stores a contact form submission for the sales team."""
    try:
        db = db_handler.get_db()
        payload = submission.model_dump()
        payload["created_at"] = time.time()
        await db["contact_leads"].insert_one(payload)
        return {"status": "ok"}
    except Exception as error:
        print(f"Error saving contact submission: {error}")
        return {"status": "error", "message": "Could not save submission"}

