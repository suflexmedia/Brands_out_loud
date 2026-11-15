"""Provides authentication routes including login, encrypted phone OTP registration, and user profiles."""

from datetime import datetime, timedelta, timezone
import os
import re
import secrets
import time
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
import jwt
from pydantic import BaseModel

from common.crypto_utils import (
    decrypt_pii,
    encrypt_pii,
    hash_blind_index,
    hash_otp,
    verify_otp_hash,
)
from common.msg91_service import send_otp
from database_handler.connection import db_handler

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

JWT_SECRET = os.getenv("JWT_SECRET", "brands-out-loud-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72
OTP_EXPIRY_SECONDS = 600
OTP_RESEND_COOLDOWN_SECONDS = 30


class RegisterRequest(BaseModel):
    """Direct registration payload."""

    name: str
    email: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    password: str


class SendRegisterOtpRequest(BaseModel):
    """Payload to request mobile OTP for registration."""

    name: str
    email: str
    phone: str
    company_name: Optional[str] = None
    password: str


class VerifyRegisterOtpRequest(BaseModel):
    """Payload with the 6-digit OTP to finalize registration."""

    email: str
    phone: str
    otp: str


class ResendRegisterOtpRequest(BaseModel):
    """Payload to request a fresh registration OTP."""

    email: str
    phone: str


class LoginRequest(BaseModel):
    """Login credentials payload."""

    email: str
    password: str


class SendLoginOtpRequest(BaseModel):
    """Payload to request a mobile OTP for sign in."""

    phone: str


class VerifyLoginOtpRequest(BaseModel):
    """Payload with mobile number and 6-digit OTP for sign in."""

    phone: str
    otp: str


class ResendLoginOtpRequest(BaseModel):
    """Payload to request a fresh OTP for sign in."""

    phone: str


class UpdateProfileRequest(BaseModel):
    """Payload to update basic profile information."""

    name: str
    company_name: Optional[str] = None


class SendPhoneChangeOtpRequest(BaseModel):
    """Payload to request an OTP for updating user phone number."""

    new_phone: str


class VerifyPhoneChangeOtpRequest(BaseModel):
    """Payload with the 6-digit OTP to confirm phone number change."""

    new_phone: str
    otp: str


def _clean_phone(phone: str) -> str:
    """Normalizes phone numbers to standard format."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""


def _generate_otp() -> str:
    """Generates a random 6-digit numeric OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def create_jwt_token(user_id: str, name: str, email: str) -> str:
    """Encodes a signed JWT auth token for the authenticated user."""
    payload = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Validates the signature and expiry of a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _extract_user_id_from_request(request: Request) -> str:
    """Extracts and verifies user ID from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = request.cookies.get("bol_token", "")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user_id


def get_authenticated_user_payload(request: Request) -> Optional[dict]:
    """Extracts and verifies JWT token from request header or cookie, returning payload or None."""
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = request.cookies.get("bol_token", "")

    if not token:
        return None
    try:
        return verify_jwt_token(token)
    except Exception:
        return None


@router.get("/login", tags=["Auth"])
async def serve_login_page(request: Request):
    """Serves the remastered login and registration page."""
    from page_serving_routers.routers.site_context import base_context

    context = await base_context(active_nav="login")
    context["seo"] = {
        "title": "Sign In / Register — Brands Out Loud",
        "description": "Sign in or create your Brands Out Loud account for exclusive editions and reports.",
    }
    return templates.TemplateResponse(request, "login.html", context)


@router.get("/profile", tags=["Auth"])
async def serve_profile_page(request: Request):
    """Serves the remastered account profile and library page."""
    from page_serving_routers.routers.site_context import base_context

    context = await base_context(active_nav="profile")
    context["seo"] = {
        "title": "My Account & Library — Brands Out Loud",
        "description": "View your purchased editions, read e-books online, and manage your account details.",
    }
    return templates.TemplateResponse(request, "profile.html", context)


@router.post("/api/auth/register/send-otp", tags=["Auth"])
async def send_register_otp(data: SendRegisterOtpRequest):
    """Validates registration input, encrypts PII, hashes OTP, and stores temporary session."""
    email_clean = data.email.lower().strip()
    phone_clean = _clean_phone(data.phone)
    name_clean = data.name.strip()

    if not name_clean:
        raise HTTPException(status_code=400, detail="Please enter your full name.")

    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    if not phone_clean or len(re.sub(r"\D", "", phone_clean)) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number.")

    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    phone_blind = hash_blind_index(phone_clean)
    db = db_handler.get_db()
    users = db["users"]

    existing_email = await users.find_one({"email": email_clean})
    if existing_email:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    existing_phone = await users.find_one({"$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}]})
    if existing_phone:
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")

    hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    otp_code = _generate_otp()
    otp_hashed = hash_otp(otp_code)
    now = time.time()

    pending_collection = db["pending_registrations"]
    await pending_collection.update_one(
        {"email": email_clean},
        {
            "$set": {
                "name": encrypt_pii(name_clean),
                "email": email_clean,
                "phone_encrypted": encrypt_pii(phone_clean),
                "phone_hash": phone_blind,
                "company_name": encrypt_pii(data.company_name.strip()) if data.company_name else None,
                "password": hashed_pw,
                "otp_hash": otp_hashed,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
                "updated_at": now,
            }
        },
        upsert=True,
    )

    sms_result = await send_otp(phone_clean, otp_code)
    if sms_result.get("status") == "error":
        raise HTTPException(
            status_code=502,
            detail=sms_result.get("message") or "Failed to dispatch verification SMS via gateway.",
        )

    res_data = {
        "status": "ok",
        "message": f"Verification code sent to {phone_clean}",
        "phone": phone_clean,
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if sms_result.get("mode") == "mock" and "demo_otp" in sms_result:
        res_data["demo_otp"] = sms_result["demo_otp"]

    return res_data


@router.post("/api/auth/register/resend-otp", tags=["Auth"])
async def resend_register_otp(data: ResendRegisterOtpRequest):
    """Regenerates a fresh registration OTP and updates its one-way hash with rate limiting."""
    email_clean = data.email.lower().strip()
    phone_clean = _clean_phone(data.phone)
    phone_blind = hash_blind_index(phone_clean)

    db = db_handler.get_db()
    pending = await db["pending_registrations"].find_one({
        "email": email_clean,
        "$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}],
    })

    if not pending:
        raise HTTPException(status_code=400, detail="Registration session expired. Please enter details again.")

    now = time.time()
    elapsed = now - pending.get("otp_sent_at", 0)
    if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
        wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
        raise HTTPException(status_code=429, detail=f"Please wait {wait}s before requesting another OTP.")

    otp_code = _generate_otp()
    otp_hashed = hash_otp(otp_code)

    await db["pending_registrations"].update_one(
        {"_id": pending["_id"]},
        {
            "$set": {
                "otp_hash": otp_hashed,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
                "updated_at": now,
            }
        },
    )

    sms_result = await send_otp(phone_clean, otp_code)
    if sms_result.get("status") == "error":
        raise HTTPException(
            status_code=502,
            detail=sms_result.get("message") or "Failed to dispatch verification SMS via gateway.",
        )

    res_data = {
        "status": "ok",
        "message": f"A new verification code has been sent to {phone_clean}",
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if sms_result.get("mode") == "mock" and "demo_otp" in sms_result:
        res_data["demo_otp"] = sms_result["demo_otp"]

    return res_data


@router.post("/api/auth/register/verify-otp", tags=["Auth"])
async def verify_register_otp(data: VerifyRegisterOtpRequest):
    """Verifies the HMAC-SHA256 OTP and writes the encrypted user record to MongoDB."""
    email_clean = data.email.lower().strip()
    phone_clean = _clean_phone(data.phone)
    phone_blind = hash_blind_index(phone_clean)
    entered_otp = re.sub(r"\D", "", data.otp or "")

    if len(entered_otp) != 6:
        raise HTTPException(status_code=400, detail="Please enter the complete 6-digit verification code.")

    db = db_handler.get_db()
    pending = await db["pending_registrations"].find_one({
        "email": email_clean,
        "$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}],
    })

    if not pending:
        raise HTTPException(status_code=400, detail="Registration session not found or expired.")

    now = time.time()
    if now > pending.get("otp_expires_at", 0):
        raise HTTPException(status_code=400, detail="Verification code has expired. Please resend a new OTP.")

    stored_otp_hash = pending.get("otp_hash")
    if not verify_otp_hash(entered_otp, stored_otp_hash):
        legacy_otp = str(pending.get("otp_code", ""))
        if not legacy_otp or legacy_otp != entered_otp:
            raise HTTPException(status_code=400, detail="Incorrect verification code. Please check and try again.")

    users = db["users"]
    existing = await users.find_one({"$or": [{"email": email_clean}, {"phone_hash": phone_blind}, {"phone": phone_clean}]})
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email or phone already exists.")

    user_doc = {
        "name": pending.get("name"),
        "email": pending["email"],
        "phone_encrypted": pending.get("phone_encrypted") or encrypt_pii(phone_clean),
        "phone_hash": phone_blind,
        "company_name": pending.get("company_name"),
        "password": pending["password"],
        "phone_verified": True,
        "created_at": datetime.now(timezone.utc),
        "last_login_at": datetime.now(timezone.utc),
    }

    result = await users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    await db["pending_registrations"].delete_one({"_id": pending["_id"]})

    plain_name = decrypt_pii(user_doc["name"]) or name_clean
    token = create_jwt_token(user_id, plain_name, user_doc["email"])

    from fastapi.responses import JSONResponse

    response = JSONResponse(
        content={
            "status": "ok",
            "token": token,
            "user": {
                "name": plain_name,
                "email": user_doc["email"],
                "phone": phone_clean,
            },
        }
    )
    response.set_cookie(
        key="bol_token",
        value=token,
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        samesite="lax",
    )
    return response


@router.post("/api/auth/register", tags=["Auth"])
async def register_user(data: RegisterRequest):
    """Fallback direct registration with encrypted credentials."""
    db = db_handler.get_db()
    users = db["users"]

    email_clean = data.email.lower().strip()
    phone_clean = _clean_phone(data.phone) if data.phone else None
    phone_blind = hash_blind_index(phone_clean) if phone_clean else None

    existing = await users.find_one({"email": email_clean})
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    if phone_blind:
        existing_phone = await users.find_one({"$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}]})
        if existing_phone:
            raise HTTPException(status_code=409, detail="An account with this phone number already exists")

    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_doc = {
        "name": encrypt_pii(data.name.strip()),
        "email": email_clean,
        "phone_encrypted": encrypt_pii(phone_clean) if phone_clean else None,
        "phone_hash": phone_blind,
        "company_name": encrypt_pii(data.company_name.strip()) if data.company_name else None,
        "password": hashed_password,
        "phone_verified": False,
        "created_at": datetime.now(timezone.utc),
        "last_login_at": datetime.now(timezone.utc),
    }

    result = await users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    plain_name = data.name.strip()
    token = create_jwt_token(user_id, plain_name, user_doc["email"])

    return {
        "status": "ok",
        "token": token,
        "user": {
            "name": plain_name,
            "email": user_doc["email"],
        },
    }


@router.post("/api/auth/login", tags=["Auth"])
async def login_user(data: LoginRequest):
    """Authenticates user with email or phone blind index and bcrypt password."""
    db = db_handler.get_db()
    users = db["users"]

    identifier = data.email.strip()
    query = {"email": identifier.lower()}
    if "@" not in identifier:
        cleaned_phone = _clean_phone(identifier)
        phone_blind = hash_blind_index(cleaned_phone)
        query = {
            "$or": [
                {"email": identifier.lower()},
                {"phone_hash": phone_blind},
                {"phone": cleaned_phone},
            ]
        }

    user = await users.find_one(query)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials. Please check your email/phone and password.")

    if not bcrypt.checkpw(data.password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials. Please check your email/phone and password.")

    now_utc = datetime.now(timezone.utc)
    await users.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": now_utc}})

    user_id = str(user["_id"])
    plain_name = decrypt_pii(user.get("name", "")) or user.get("name", "")
    plain_phone = decrypt_pii(user.get("phone_encrypted", "")) or user.get("phone", "")
    token = create_jwt_token(user_id, plain_name, user["email"])

    from fastapi.responses import JSONResponse

    response = JSONResponse(
        content={
            "status": "ok",
            "token": token,
            "user": {
                "name": plain_name,
                "email": user["email"],
                "phone": plain_phone,
            },
        }
    )
    response.set_cookie(
        key="bol_token",
        value=token,
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        samesite="lax",
    )
    return response


@router.post("/api/auth/login/send-otp", tags=["Auth"])
async def send_login_otp(data: SendLoginOtpRequest):
    """Generates and securely stores an encrypted OTP for registered phone login."""
    phone_clean = _clean_phone(data.phone)
    if not phone_clean or len(re.sub(r"\D", "", phone_clean)) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number.")

    phone_blind = hash_blind_index(phone_clean)
    db = db_handler.get_db()
    users = db["users"]

    user = await users.find_one({"$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}]})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found with this mobile number. Please check your number or create an account.",
        )

    otp_code = _generate_otp()
    otp_hashed = hash_otp(otp_code)
    now = time.time()

    await db["pending_login_otps"].update_one(
        {"phone_hash": phone_blind},
        {
            "$set": {
                "phone_hash": phone_blind,
                "phone_clean": phone_clean,
                "user_id": str(user["_id"]),
                "otp_hash": otp_hashed,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
                "updated_at": now,
            }
        },
        upsert=True,
    )

    sms_result = await send_otp(phone_clean, otp_code)
    if sms_result.get("status") == "error":
        raise HTTPException(
            status_code=502,
            detail=sms_result.get("message") or "Failed to dispatch login verification code via SMS gateway.",
        )

    res_data = {
        "status": "ok",
        "message": f"Verification code sent to {phone_clean}",
        "phone": phone_clean,
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if sms_result.get("mode") == "mock" and "demo_otp" in sms_result:
        res_data["demo_otp"] = sms_result["demo_otp"]

    return res_data


@router.post("/api/auth/login/resend-otp", tags=["Auth"])
async def resend_login_otp(data: ResendLoginOtpRequest):
    """Regenerates a fresh login OTP for an existing session with rate limiting."""
    phone_clean = _clean_phone(data.phone)
    phone_blind = hash_blind_index(phone_clean)

    db = db_handler.get_db()
    pending = await db["pending_login_otps"].find_one({"phone_hash": phone_blind})
    if not pending:
        raise HTTPException(status_code=400, detail="Login session expired. Please enter your mobile number again.")

    now = time.time()
    elapsed = now - pending.get("otp_sent_at", 0)
    if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
        wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
        raise HTTPException(status_code=429, detail=f"Please wait {wait}s before requesting another OTP.")

    otp_code = _generate_otp()
    otp_hashed = hash_otp(otp_code)

    await db["pending_login_otps"].update_one(
        {"_id": pending["_id"]},
        {
            "$set": {
                "otp_hash": otp_hashed,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
                "updated_at": now,
            }
        },
    )

    sms_result = await send_otp(phone_clean, otp_code)
    if sms_result.get("status") == "error":
        raise HTTPException(
            status_code=502,
            detail=sms_result.get("message") or "Failed to dispatch login verification code via SMS gateway.",
        )

    res_data = {
        "status": "ok",
        "message": f"A new verification code has been sent to {phone_clean}",
        "phone": phone_clean,
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if sms_result.get("mode") == "mock" and "demo_otp" in sms_result:
        res_data["demo_otp"] = sms_result["demo_otp"]

    return res_data


@router.post("/api/auth/login/verify-otp", tags=["Auth"])
async def verify_login_otp(data: VerifyLoginOtpRequest):
    """Verifies login OTP and returns signed JWT token along with cookie."""
    from bson import ObjectId
    from fastapi.responses import JSONResponse

    phone_clean = _clean_phone(data.phone)
    phone_blind = hash_blind_index(phone_clean)
    entered_otp = re.sub(r"\D", "", data.otp or "")

    if len(entered_otp) != 6:
        raise HTTPException(status_code=400, detail="Please enter the complete 6-digit verification code.")

    db = db_handler.get_db()
    pending = await db["pending_login_otps"].find_one({"phone_hash": phone_blind})
    if not pending:
        raise HTTPException(status_code=400, detail="Login session not found or expired.")

    now = time.time()
    if now > pending.get("otp_expires_at", 0):
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new OTP.")

    stored_otp_hash = pending.get("otp_hash")
    if not verify_otp_hash(entered_otp, stored_otp_hash):
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please check and try again.")

    user_id = pending.get("user_id")
    users = db["users"]
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    now_utc = datetime.now(timezone.utc)
    await users.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": now_utc}})
    await db["pending_login_otps"].delete_one({"_id": pending["_id"]})

    plain_name = decrypt_pii(user.get("name", "")) or user.get("name", "")
    plain_phone = decrypt_pii(user.get("phone_encrypted", "")) or user.get("phone", "")
    token = create_jwt_token(str(user["_id"]), plain_name, user["email"])

    response = JSONResponse(
        content={
            "status": "ok",
            "token": token,
            "user": {
                "name": plain_name,
                "email": user["email"],
                "phone": plain_phone,
            },
        }
    )
    response.set_cookie(
        key="bol_token",
        value=token,
        path="/",
        max_age=JWT_EXPIRATION_HOURS * 3600,
        samesite="lax",
    )
    return response


@router.get("/api/auth/me", tags=["Auth"])
async def get_current_user(request: Request):
    """Validates bearer token and returns decrypted user profile."""
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = request.cookies.get("bol_token", "")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")

    plain_phone = ""
    plain_name = payload.get("name", "")
    plain_company = ""
    if user_id:
        try:
            from bson import ObjectId
            db = db_handler.get_db()
            user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
            if user_doc:
                plain_name = decrypt_pii(user_doc.get("name", "")) or user_doc.get("name", "")
                plain_phone = decrypt_pii(user_doc.get("phone_encrypted", "")) or user_doc.get("phone", "")
                plain_company = decrypt_pii(user_doc.get("company_name", "")) or user_doc.get("company_name", "")
        except Exception:
            pass

    return {
        "status": "ok",
        "user": {
            "user_id": user_id,
            "name": plain_name,
            "email": payload.get("email"),
            "phone": plain_phone,
            "company_name": plain_company,
        },
    }


class DeleteAccountRequest(BaseModel):
    """Optional payload to verify password before account deletion."""

    password: Optional[str] = None


@router.delete("/api/auth/me", tags=["Auth"])
async def delete_current_user_account(request: Request, data: Optional[DeleteAccountRequest] = None):
    """Permanently deletes the currently authenticated user's account and session."""
    from fastapi.responses import JSONResponse

    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = request.cookies.get("bol_token", "")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    from bson import ObjectId
    db = db_handler.get_db()
    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Account not found")

    if data and data.password:
        if not bcrypt.checkpw(data.password.encode("utf-8"), user_doc["password"].encode("utf-8")):
            raise HTTPException(status_code=400, detail="Incorrect password verification")

    await db["users"].delete_one({"_id": ObjectId(user_id)})

    response = JSONResponse(content={"status": "ok", "message": "Account deleted successfully"})
    response.delete_cookie(key="bol_token", path="/")
    return response


@router.post("/api/auth/logout", tags=["Auth"])
async def logout_user():
    """Clears the authentication session and cookie."""
    from fastapi.responses import JSONResponse

    response = JSONResponse(content={"status": "ok", "message": "Logged out successfully"})
    response.delete_cookie(key="bol_token", path="/")
    return response


@router.get("/api/auth/purchases", tags=["Auth"])
async def get_user_purchases(request: Request):
    """Returns all confirmed book and magazine orders matching the authenticated user."""
    user_id = _extract_user_id_from_request(request)
    from bson import ObjectId
    db = db_handler.get_db()

    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    user_email = user_doc.get("email", "").lower().strip()
    user_phone_plain = decrypt_pii(user_doc.get("phone_encrypted", "")) or user_doc.get("phone", "")
    user_phone_digits = re.sub(r"\D", "", user_phone_plain) if user_phone_plain else ""

    query_conditions = [{"user_id": user_id}]
    if user_email:
        query_conditions.append({"email": {"$regex": f"^{re.escape(user_email)}$", "$options": "i"}})
    if user_phone_digits and len(user_phone_digits) >= 10:
        query_conditions.append({"phone": {"$regex": re.escape(user_phone_digits[-10:])}})

    orders_cursor = db["book_orders"].find({
        "$or": query_conditions,
        "status": {"$in": ["confirmed", "shipped", "delivered"]},
    }).sort("confirmed_at", -1)

    raw_orders = await orders_cursor.to_list(100)
    purchases = []
    for o in raw_orders:
        item = o.get("item") or {}
        slug = item.get("slug") or "laser-veda"
        read_url = f"/magazine/{slug}-edition/read" if slug == "laser-veda" else f"/magazine/{slug}/read"

        status_val = o.get("status", "confirmed")
        status_label = "Order Confirmed · Processing"
        progress_step = 1
        if status_val == "shipped":
            status_label = "Dispatched · In Transit"
            progress_step = 2
        elif status_val == "delivered":
            status_label = "Delivered"
            progress_step = 3

        confirmed_ts = o.get("confirmed_at")
        date_str = ""
        if confirmed_ts:
            try:
                date_str = datetime.fromtimestamp(confirmed_ts, timezone.utc).strftime("%d %b %Y")
            except Exception:
                date_str = str(confirmed_ts)

        purchases.append({
            "order_number": o.get("order_number", "BOL-ORDER"),
            "item_title": item.get("title", "LaserVEDA"),
            "item_subtitle": item.get("subtitle", "HEALING AT THE SPEED OF LIGHT"),
            "item_author": item.get("author", "Dr. Prof. Chandrashekhar Yavagal"),
            "item_edition": item.get("edition", "Hardcover · English"),
            "cover_url": item.get("cover_url", "/static/images/laserveda/book_cover.png"),
            "amount": (item.get("amount_paise", 79900)) / 100,
            "currency": item.get("currency", "INR"),
            "status": status_val,
            "status_label": status_label,
            "progress_step": progress_step,
            "date": date_str,
            "read_url": read_url,
            "has_ebook": True,
            "shipping_address": {
                "name": f"{o.get('first_name', '')} {o.get('last_name', '')}".strip(),
                "address_line_1": o.get("address_line_1", ""),
                "address_line_2": o.get("address_line_2", ""),
                "zip_code": o.get("zip_code", ""),
            },
        })

    return {"status": "ok", "purchases": purchases}


@router.put("/api/auth/profile", tags=["Auth"])
async def update_user_profile(data: UpdateProfileRequest, request: Request):
    """Updates the user's name and company name with AES-256-GCM encryption."""
    user_id = _extract_user_id_from_request(request)
    name_clean = data.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    from bson import ObjectId
    db = db_handler.get_db()
    users = db["users"]

    update_fields = {
        "name": encrypt_pii(name_clean),
        "updated_at": datetime.now(timezone.utc),
    }
    if data.company_name is not None:
        update_fields["company_name"] = encrypt_pii(data.company_name.strip()) if data.company_name.strip() else ""

    await users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})

    return {
        "status": "ok",
        "message": "Profile updated successfully",
        "user": {
            "name": name_clean,
            "company_name": data.company_name.strip() if data.company_name else "",
        },
    }


@router.post("/api/auth/profile/phone/send-otp", tags=["Auth"])
async def send_phone_change_otp(data: SendPhoneChangeOtpRequest, request: Request):
    """Validates the new phone number, checks uniqueness, hashes OTP, and stores session."""
    user_id = _extract_user_id_from_request(request)
    phone_clean = _clean_phone(data.new_phone)
    if not phone_clean or len(re.sub(r"\D", "", phone_clean)) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number.")

    phone_blind = hash_blind_index(phone_clean)
    from bson import ObjectId
    db = db_handler.get_db()
    users = db["users"]

    existing = await users.find_one({
        "_id": {"$ne": ObjectId(user_id)},
        "$or": [{"phone_hash": phone_blind}, {"phone": phone_clean}],
    })
    if existing:
        raise HTTPException(status_code=409, detail="This mobile number is already linked to another account.")

    now = time.time()
    phone_changes = db["phone_change_requests"]
    prior = await phone_changes.find_one({"user_id": user_id, "new_phone_hash": phone_blind})
    if prior and (now - prior.get("otp_sent_at", 0)) < OTP_RESEND_COOLDOWN_SECONDS:
        wait = int(OTP_RESEND_COOLDOWN_SECONDS - (now - prior.get("otp_sent_at", 0)))
        raise HTTPException(status_code=429, detail=f"Please wait {wait}s before requesting another OTP.")

    otp_code = _generate_otp()
    otp_hashed = hash_otp(otp_code)

    await phone_changes.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "new_phone_encrypted": encrypt_pii(phone_clean),
                "new_phone_hash": phone_blind,
                "new_phone_clean": phone_clean,
                "otp_hash": otp_hashed,
                "otp_sent_at": now,
                "otp_expires_at": now + OTP_EXPIRY_SECONDS,
            }
        },
        upsert=True,
    )

    sms_result = await send_otp(phone_clean, otp_code)
    if sms_result.get("status") == "error":
        raise HTTPException(
            status_code=502,
            detail=sms_result.get("message") or "Failed to dispatch verification SMS via gateway.",
        )

    res_data = {
        "status": "ok",
        "message": f"Verification code sent to {phone_clean}",
        "phone": phone_clean,
        "cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    if sms_result.get("mode") == "mock" and "demo_otp" in sms_result:
        res_data["demo_otp"] = sms_result["demo_otp"]

    return res_data


@router.post("/api/auth/profile/phone/verify-otp", tags=["Auth"])
async def verify_phone_change_otp(data: VerifyPhoneChangeOtpRequest, request: Request):
    """Verifies OTP and securely updates the user's encrypted phone and blind index."""
    user_id = _extract_user_id_from_request(request)
    phone_clean = _clean_phone(data.new_phone)
    phone_blind = hash_blind_index(phone_clean)
    entered_otp = re.sub(r"\D", "", data.otp or "")

    if len(entered_otp) != 6:
        raise HTTPException(status_code=400, detail="Please enter a valid 6-digit OTP.")

    from bson import ObjectId
    db = db_handler.get_db()
    phone_changes = db["phone_change_requests"]
    record = await phone_changes.find_one({"user_id": user_id, "new_phone_hash": phone_blind})
    if not record:
        raise HTTPException(status_code=400, detail="Phone verification session expired. Please request a new OTP.")

    if time.time() > record.get("otp_expires_at", 0):
        await phone_changes.delete_one({"_id": record["_id"]})
        raise HTTPException(status_code=400, detail="Verification code expired. Please request a new one.")

    if not verify_otp_hash(entered_otp, record.get("otp_hash")):
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please check and try again.")

    users = db["users"]
    await users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "phone_encrypted": record.get("new_phone_encrypted") or encrypt_pii(phone_clean),
                "phone_hash": phone_blind,
                "phone_verified": True,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    await phone_changes.delete_one({"_id": record["_id"]})

    return {
        "status": "ok",
        "message": "Mobile number updated and verified successfully",
        "phone": phone_clean,
    }
