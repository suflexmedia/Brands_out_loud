"""Serves the LaserVEDA book order flow pages and Razorpay-ready checkout APIs."""

import hashlib
import hmac
import os
import re
import secrets
import time
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database_handler import db_handler
from page_serving_routers.routers.site_context import ASSET_VERSION

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "static", "templates"))

ORDER_COOKIE_NAME = "lv_order_session"
OTP_EXPIRY_SECONDS = 600
OTP_RESEND_COOLDOWN_SECONDS = 30

BOOK_ITEM = {
    "slug": "lazer-veda",
    "title": "LaserVEDA",
    "subtitle": "HEALING AT THE SPEED OF LIGHT",
    "author": "Dr. Prof. Chandrashekhar Yavagal",
    "edition": "Hardcover · English · Qty 1",
    "cover_url": "/static/images/lazerveda/book_cover.png",
    "sale_price": 799,
    "original_price": 999,
    "discount_amount": 200,
    "amount_paise": 79900,
    "currency": "INR",
    "note": "One copy. A new perspective on healing.",
}


class OrderDetailsRequest(BaseModel):
    """Validated contact and shipping details submitted in step 1."""

    first_name: str
    last_name: str
    phone: str
    email: str
    address_line_1: str
    address_line_2: Optional[str] = ""
    zip_code: str


class VerifyOtpRequest(BaseModel):
    """Six-digit OTP payload submitted in step 2."""

    otp: str


class RazorpayVerifyRequest(BaseModel):
    """Payment verification payload returned by Razorpay Checkout or sandbox mode."""

    mode: str = "razorpay"
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None


def _clean_text(value: Optional[str]) -> str:
    """Trims and collapses whitespace on user input strings."""
    return re.sub(r"\s+", " ", (value or "").strip())


def _normalize_phone(raw_phone: str) -> str:
    """Normalizes phone numbers into a clean display format."""
    cleaned = _clean_text(raw_phone)
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    if len(digits) == 12 and digits.startswith("91"):
        local = digits[2:]
        return f"+91 {local[:5]} {local[5:]}"
    return cleaned


def _generate_otp() -> str:
    """Generates a cryptographically random 6-digit OTP code."""
    return f"{secrets.randbelow(900000) + 100000}"


async def _generate_order_number(db) -> str:
    """Generates a unique LV-XXXXXX order reference number."""
    for _ in range(10):
        candidate = f"LV-{secrets.randbelow(900000) + 100000}"
        existing = await db["book_orders"].find_one({"order_number": candidate}, {"_id": 1})
        if not existing:
            return candidate
    return f"LV-{int(time.time()) % 1000000:06d}"


def _razorpay_credentials() -> tuple:
    """Returns configured Razorpay key ID and key secret from environment."""
    key_id = os.environ.get("RAZORPAY_KEY_ID", "").strip()
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()
    return key_id, key_secret


def _is_sms_live() -> bool:
    """Indicates whether an external SMS OTP gateway is enabled."""
    return os.environ.get("SMS_OTP_ENABLED", "").strip().lower() in ("1", "true", "yes")


async def _get_order_by_request(request: Request) -> Optional[dict]:
    """Fetches the current order session document from MongoDB."""
    session_id = request.cookies.get(ORDER_COOKIE_NAME)
    if not session_id:
        return None
    db = db_handler.get_db()
    return await db["book_orders"].find_one({"session_id": session_id})


def _base_order_context(order: Optional[dict], active_step: int) -> dict:
    """Builds common template context for all order flow pages."""
    return {
        "asset_version": ASSET_VERSION,
        "book": BOOK_ITEM,
        "order": order or {},
        "active_step": active_step,
        "book_page_url": "/magazine/lazer-veda",
        "sample_chapter_url": "/magazine/lazer-veda#get-the-book",
    }


@router.get("/order", tags=["Pages"])
async def serve_order_details(request: Request):
    """Serves step 1 of the LaserVEDA book order flow."""
    order = await _get_order_by_request(request)
    if order and order.get("status") == "confirmed":
        order = None
    context = _base_order_context(order, active_step=1)
    return templates.TemplateResponse(request, "order/order_details.html", context)


@router.get("/magazine/lazer-veda/order", tags=["Pages"])
async def redirect_lazerveda_order():
    """Redirects the book-scoped order URL to the canonical order step 1 route."""
    return RedirectResponse(url="/order", status_code=302)


@router.get("/order/verify", tags=["Pages"])
async def serve_order_verify(request: Request):
    """Serves step 2 phone OTP verification for the active order session."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone"):
        return RedirectResponse(url="/order", status_code=302)
    if order.get("status") == "confirmed":
        return RedirectResponse(url="/order/confirmed", status_code=302)
    sent_at = order.get("otp_sent_at", 0)
    remaining_cooldown = max(0, int(OTP_RESEND_COOLDOWN_SECONDS - (time.time() - sent_at)))
    context = _base_order_context(order, active_step=2)
    context.update({
        "remaining_cooldown": remaining_cooldown,
        "demo_otp": "" if _is_sms_live() else order.get("otp_code", ""),
    })
    return templates.TemplateResponse(request, "order/order_verify.html", context)


@router.get("/order/review", tags=["Pages"])
async def serve_order_review(request: Request):
    """Serves step 3 order review and Razorpay payment initiation."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone"):
        return RedirectResponse(url="/order", status_code=302)
    if not order.get("phone_verified"):
        return RedirectResponse(url="/order/verify", status_code=302)
    if order.get("status") == "confirmed":
        return RedirectResponse(url="/order/confirmed", status_code=302)
    key_id, key_secret = _razorpay_credentials()
    context = _base_order_context(order, active_step=3)
    context["razorpay_configured"] = bool(key_id and key_secret)
    return templates.TemplateResponse(request, "order/order_review.html", context)


@router.get("/order/placed", tags=["Pages"])
async def serve_order_placed(request: Request):
    """Serves the celebration screen immediately after order placement."""
    order = await _get_order_by_request(request)
    if not order or order.get("status") != "confirmed":
        return RedirectResponse(url="/order", status_code=302)
    context = _base_order_context(order, active_step=4)
    return templates.TemplateResponse(request, "order/order_placed.html", context)


@router.get("/order/confirmed", tags=["Pages"])
async def serve_order_confirmed(request: Request):
    """Serves the detailed order confirmation receipt page."""
    order = await _get_order_by_request(request)
    if not order or order.get("status") != "confirmed":
        return RedirectResponse(url="/order", status_code=302)
    context = _base_order_context(order, active_step=5)
    return templates.TemplateResponse(request, "order/order_confirmed.html", context)


@router.post("/api/order/details", tags=["Order API"])
async def save_order_details(payload: OrderDetailsRequest, request: Request, response: Response):
    """Validates contact and shipping details, issues an OTP, and persists the draft order."""
    first_name = _clean_text(payload.first_name)
    last_name = _clean_text(payload.last_name)
    email = _clean_text(payload.email).lower()
    phone = _normalize_phone(payload.phone)
    address_line_1 = _clean_text(payload.address_line_1)
    address_line_2 = _clean_text(payload.address_line_2)
    zip_code = re.sub(r"\D", "", payload.zip_code or "")

    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="Please enter both your first and last name.")
    if len(re.sub(r"\D", "", phone)) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit phone number.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if not address_line_1:
        raise HTTPException(status_code=400, detail="Please enter your shipping address.")
    if not re.match(r"^\d{6}$", zip_code):
        raise HTTPException(status_code=400, detail="Please enter a valid 6-digit postal ZIP code.")

    db = db_handler.get_db()
    existing = await _get_order_by_request(request)
    now = time.time()
    otp_code = _generate_otp()

    if existing and existing.get("status") != "confirmed":
        session_id = existing["session_id"]
        phone_changed = existing.get("phone") != phone
        already_verified = bool(existing.get("phone_verified")) and not phone_changed
    else:
        session_id = secrets.token_urlsafe(32)
        already_verified = False

    order_doc = {
        "session_id": session_id,
        "book_slug": BOOK_ITEM["slug"],
        "book_title": BOOK_ITEM["title"],
        "amount": BOOK_ITEM["sale_price"],
        "original_price": BOOK_ITEM["original_price"],
        "discount_amount": BOOK_ITEM["discount_amount"],
        "currency": BOOK_ITEM["currency"],
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "zip_code": zip_code,
        "otp_code": otp_code,
        "otp_sent_at": now,
        "otp_expires_at": now + OTP_EXPIRY_SECONDS,
        "phone_verified": already_verified,
        "status": "verified" if already_verified else "otp_pending",
        "updated_at": now,
    }

    await db["book_orders"].update_one(
        {"session_id": session_id},
        {"$set": order_doc, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )

    response.set_cookie(
        key=ORDER_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )

    print(f"[LaserVEDA Order OTP] Phone: {phone} | OTP: {otp_code}")

    result = {
        "status": "ok",
        "redirect_url": "/order/verify",
    }
    if not _is_sms_live():
        result["demo_otp"] = otp_code
    return result


@router.post("/api/order/resend-otp", tags=["Order API"])
async def resend_order_otp(request: Request):
    """Issues a fresh 6-digit OTP for the active order session after cooldown."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone"):
        raise HTTPException(status_code=400, detail="Order session expired. Please start again.")
    if order.get("status") == "confirmed":
        raise HTTPException(status_code=400, detail="This order is already confirmed.")

    now = time.time()
    elapsed = now - order.get("otp_sent_at", 0)
    if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
        wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
        raise HTTPException(status_code=429, detail=f"Please wait {wait}s before requesting another OTP.")

    otp_code = _generate_otp()
    db = db_handler.get_db()
    await db["book_orders"].update_one(
        {"session_id": order["session_id"]},
        {
            "$set": {
                "otp_code": otp_code,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
                "phone_verified": False,
                "status": "otp_pending",
                "updated_at": now,
            }
        },
    )

    print(f"[LaserVEDA Order OTP Resent] Phone: {order['phone']} | OTP: {otp_code}")

    result = {
        "status": "ok",
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if not _is_sms_live():
        result["demo_otp"] = otp_code
    return result


@router.post("/api/order/verify-otp", tags=["Order API"])
async def verify_order_otp(payload: VerifyOtpRequest, request: Request):
    """Verifies the 6-digit OTP and advances the order session to review."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone"):
        raise HTTPException(status_code=400, detail="Order session expired. Please enter your details again.")
    if order.get("status") == "confirmed":
        return {"status": "ok", "redirect_url": "/order/confirmed"}

    entered = re.sub(r"\D", "", payload.otp or "")
    if len(entered) != 6:
        raise HTTPException(status_code=400, detail="Please enter the complete 6-digit verification code.")

    now = time.time()
    if now > order.get("otp_expires_at", 0):
        raise HTTPException(status_code=400, detail="Your verification code has expired. Please resend a new OTP.")

    expected = str(order.get("otp_code", ""))
    if not hmac.compare_digest(entered, expected):
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please check and try again.")

    db = db_handler.get_db()
    await db["book_orders"].update_one(
        {"session_id": order["session_id"]},
        {
            "$set": {
                "phone_verified": True,
                "status": "verified",
                "verified_at": now,
                "updated_at": now,
            }
        },
    )
    return {"status": "ok", "redirect_url": "/order/review"}


@router.post("/api/order/razorpay/create", tags=["Order API"])
async def create_razorpay_order(request: Request):
    """Creates a Razorpay order via REST API or returns sandbox config when creds are absent."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone"):
        raise HTTPException(status_code=400, detail="Order session not found.")
    if not order.get("phone_verified"):
        raise HTTPException(status_code=400, detail="Please verify your phone number first.")
    if order.get("status") == "confirmed":
        return {"status": "already_confirmed", "redirect_url": "/order/confirmed"}

    key_id, key_secret = _razorpay_credentials()
    now = time.time()
    db = db_handler.get_db()

    if not key_id or not key_secret:
        sandbox_order_id = f"order_sandbox_{secrets.token_hex(6)}"
        await db["book_orders"].update_one(
            {"session_id": order["session_id"]},
            {
                "$set": {
                    "razorpay_order_id": sandbox_order_id,
                    "payment_mode": "sandbox",
                    "status": "payment_pending",
                    "updated_at": now,
                }
            },
        )
        return {
            "status": "ok",
            "mode": "sandbox",
            "razorpay_order_id": sandbox_order_id,
            "amount": BOOK_ITEM["amount_paise"],
            "currency": BOOK_ITEM["currency"],
        }

    receipt = f"lv_{order['session_id'][:16]}"
    rzp_payload = {
        "amount": BOOK_ITEM["amount_paise"],
        "currency": BOOK_ITEM["currency"],
        "receipt": receipt,
        "notes": {
            "book": BOOK_ITEM["title"],
            "customer_name": f"{order['first_name']} {order['last_name']}",
            "customer_email": order["email"],
            "customer_phone": order["phone"],
        },
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        rzp_res = await client.post(
            "https://api.razorpay.com/v1/orders",
            json=rzp_payload,
            auth=(key_id, key_secret),
        )

    if rzp_res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Unable to initiate Razorpay payment. Please try again.")

    rzp_data = rzp_res.json()
    await db["book_orders"].update_one(
        {"session_id": order["session_id"]},
        {
            "$set": {
                "razorpay_order_id": rzp_data["id"],
                "payment_mode": "razorpay",
                "status": "payment_pending",
                "updated_at": now,
            }
        },
    )

    return {
        "status": "ok",
        "mode": "razorpay",
        "key_id": key_id,
        "razorpay_order_id": rzp_data["id"],
        "amount": rzp_data["amount"],
        "currency": rzp_data["currency"],
        "name": "Brands Out Loud",
        "description": f"{BOOK_ITEM['title']} — {BOOK_ITEM['edition']}",
        "prefill": {
            "name": f"{order['first_name']} {order['last_name']}",
            "email": order["email"],
            "contact": re.sub(r"\D", "", order["phone"]),
        },
    }


@router.post("/api/order/razorpay/verify", tags=["Order API"])
async def verify_razorpay_payment(payload: RazorpayVerifyRequest, request: Request):
    """Verifies Razorpay signature (or sandbox checkout) and confirms the book order."""
    order = await _get_order_by_request(request)
    if not order or not order.get("phone_verified"):
        raise HTTPException(status_code=400, detail="Verified order session not found.")
    if order.get("status") == "confirmed":
        return {
            "status": "ok",
            "order_number": order.get("order_number"),
            "redirect_url": "/order/placed",
        }

    key_id, key_secret = _razorpay_credentials()
    now = time.time()
    db = db_handler.get_db()

    if key_id and key_secret:
        if not payload.razorpay_order_id or not payload.razorpay_payment_id or not payload.razorpay_signature:
            raise HTTPException(status_code=400, detail="Missing Razorpay payment confirmation fields.")
        if payload.razorpay_order_id != order.get("razorpay_order_id"):
            raise HTTPException(status_code=400, detail="Razorpay order reference mismatch.")
        sign_body = f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}".encode("utf-8")
        expected_signature = hmac.new(key_secret.encode("utf-8"), sign_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, payload.razorpay_signature):
            raise HTTPException(status_code=400, detail="Razorpay signature verification failed.")
        payment_id = payload.razorpay_payment_id
        payment_mode = "razorpay"
    else:
        payment_id = payload.razorpay_payment_id or f"pay_sandbox_{secrets.token_hex(6)}"
        payment_mode = "sandbox"

    order_number = await _generate_order_number(db)
    await db["book_orders"].update_one(
        {"session_id": order["session_id"]},
        {
            "$set": {
                "razorpay_payment_id": payment_id,
                "razorpay_signature": payload.razorpay_signature or "",
                "payment_mode": payment_mode,
                "order_number": order_number,
                "status": "confirmed",
                "confirmed_at": now,
                "updated_at": now,
            }
        },
    )

    return {
        "status": "ok",
        "order_number": order_number,
        "redirect_url": "/order/placed",
    }


@router.post("/api/order/razorpay/webhook", tags=["Order API"])
async def razorpay_webhook(request: Request):
    """Handles asynchronous Razorpay payment webhooks when webhook secret is configured."""
    webhook_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip()
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Razorpay webhook secret is not configured.")

    signature = request.headers.get("X-Razorpay-Signature", "")
    raw_body = await request.body()
    expected = hmac.new(webhook_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not signature or not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid Razorpay webhook signature.")

    event = await request.json()
    event_name = event.get("event", "")
    if event_name == "payment.captured":
        entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        rzp_order_id = entity.get("order_id")
        rzp_payment_id = entity.get("id")
        if rzp_order_id:
            db = db_handler.get_db()
            existing = await db["book_orders"].find_one({"razorpay_order_id": rzp_order_id})
            if existing and existing.get("status") != "confirmed":
                order_number = await _generate_order_number(db)
                now = time.time()
                await db["book_orders"].update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "razorpay_payment_id": rzp_payment_id or "",
                            "order_number": order_number,
                            "payment_mode": "razorpay",
                            "status": "confirmed",
                            "confirmed_at": now,
                            "updated_at": now,
                        }
                    },
                )
    return {"status": "ok"}
