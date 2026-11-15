"""Service for dispatching and managing SMS OTPs via MSG91 v5 API."""

import logging
import os
import re
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

MSG91_OTP_ENDPOINT = "https://control.msg91.com/api/v5/otp"
MSG91_RETRY_ENDPOINT = "https://control.msg91.com/api/v5/otp/retry"
MSG91_VERIFY_ENDPOINT = "https://control.msg91.com/api/v5/otp/verify"


def get_msg91_config() -> Dict[str, str]:
    """Retrieves MSG91 credentials and settings from environment variables."""
    return {
        "auth_key": os.getenv("MSG91_AUTH_KEY", "").strip(),
        "template_id": os.getenv("MSG91_OTP_TEMPLATE_ID", "").strip(),
        "sender_id": os.getenv("MSG91_SENDER_ID", "").strip(),
        "expiry_minutes": os.getenv("MSG91_OTP_EXPIRY_MINUTES", "10").strip() or "10",
    }


def is_msg91_configured() -> bool:
    """Checks whether valid MSG91 authentication key and template ID are present."""
    config = get_msg91_config()
    return bool(config["auth_key"] and config["template_id"])


def format_phone_for_msg91(phone: str) -> str:
    """Normalizes phone numbers to standard format required by MSG91 without leading plus."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        return f"91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits


async def send_otp(phone: str, otp_code: str) -> Dict[str, Any]:
    """Sends a 6-digit OTP to the recipient mobile number via MSG91 with mock fallback."""
    config = get_msg91_config()
    formatted_phone = format_phone_for_msg91(phone)

    if not is_msg91_configured():
        logger.info("[MSG91 MOCK] Sending OTP %s to %s (credentials not configured)", otp_code, formatted_phone)
        print(f"[MSG91 MOCK] Sending OTP {otp_code} to {formatted_phone} (credentials not configured)")
        return {
            "status": "ok",
            "mode": "mock",
            "message": "OTP generated in development mode.",
            "phone": formatted_phone,
            "demo_otp": otp_code,
        }

    params = {
        "template_id": config["template_id"],
        "mobile": formatted_phone,
        "otp": otp_code,
        "otp_expiry": config["expiry_minutes"],
    }
    if config["sender_id"]:
        params["sender"] = config["sender_id"]

    headers = {
        "authkey": config["auth_key"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "otp": otp_code,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                MSG91_OTP_ENDPOINT,
                params=params,
                json=payload,
                headers=headers,
            )

        response_data = {}
        try:
            response_data = response.json()
        except Exception:
            response_data = {"raw": response.text}

        if response.status_code >= 400:
            err_msg = response_data.get("message") or response.text or "Failed to send OTP via SMS gateway."
            logger.error("[MSG91 ERROR] Status %d: %s", response.status_code, err_msg)
            return {
                "status": "error",
                "mode": "live",
                "status_code": response.status_code,
                "message": err_msg,
                "detail": response_data,
            }

        logger.info("[MSG91 SUCCESS] OTP dispatched to %s", formatted_phone)
        return {
            "status": "ok",
            "mode": "live",
            "message": "OTP sent successfully to your mobile number.",
            "phone": formatted_phone,
            "provider_response": response_data,
        }
    except Exception as exc:
        logger.exception("[MSG91 EXCEPTION] Connection failure: %s", str(exc))
        return {
            "status": "error",
            "mode": "live",
            "message": "Unable to connect to SMS delivery provider.",
            "detail": str(exc),
        }
