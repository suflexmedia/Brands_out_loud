import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional
from database_handler.connection import db_handler

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

JWT_SECRET = os.getenv("JWT_SECRET", "brands-out-loud-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72


class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def create_jwt_token(user_id: str, name: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/login", tags=["Auth"])
async def serve_login_page(request: Request):
    from PAGE_SERVING_ROUTERS.routers.navbar_fetcher import get_navbar_data
    navbar = await get_navbar_data()
    return templates.TemplateResponse("login.html", {"request": request, "navbar": navbar})


@router.post("/api/auth/register", tags=["Auth"])
async def register_user(data: RegisterRequest):
    db = db_handler.get_db()
    users = db["users"]

    existing = await users.find_one({"email": data.email.lower().strip()})
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())

    user_doc = {
        "name": data.name.strip(),
        "email": data.email.lower().strip(),
        "phone": data.phone.strip() if data.phone else None,
        "company_name": data.company_name.strip() if data.company_name else None,
        "password": hashed_password.decode("utf-8"),
        "created_at": datetime.now(timezone.utc),
    }

    result = await users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_jwt_token(user_id, user_doc["name"], user_doc["email"])

    return {
        "status": "ok",
        "token": token,
        "user": {
            "name": user_doc["name"],
            "email": user_doc["email"],
        },
    }


@router.post("/api/auth/login", tags=["Auth"])
async def login_user(data: LoginRequest):
    db = db_handler.get_db()
    users = db["users"]

    user = await users.find_one({"email": data.email.lower().strip()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(data.password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_jwt_token(user_id, user["name"], user["email"])

    return {
        "status": "ok",
        "token": token,
        "user": {
            "name": user["name"],
            "email": user["email"],
        },
    }


@router.get("/api/auth/me", tags=["Auth"])
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ", 1)[1]
    payload = verify_jwt_token(token)

    return {
        "status": "ok",
        "user": {
            "name": payload.get("name"),
            "email": payload.get("email"),
        },
    }
